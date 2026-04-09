"""
db.py — SQLite database layer for Archive Scout.
Manages two tables: listings and market_values.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "scout.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS listings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                price_jpy   REAL    NOT NULL,
                price_usd   REAL    NOT NULL,
                url         TEXT    NOT NULL UNIQUE,
                thumbnail   TEXT,
                keyword     TEXT    NOT NULL,
                seen_at     TEXT    NOT NULL,
                alerted     INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS market_values (
                keyword         TEXT    PRIMARY KEY,
                estimated_usd   REAL    NOT NULL,
                updated_at      TEXT    NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_listings_keyword
                ON listings (keyword);

            CREATE INDEX IF NOT EXISTS idx_listings_seen_at
                ON listings (seen_at);
        """)
    logger.info("Database initialised at %s", DB_PATH)


def listing_exists(url: str) -> bool:
    """Return True if a listing URL is already in the database."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM listings WHERE url = ?", (url,)
        ).fetchone()
        return row is not None


def insert_listing(
    title: str,
    price_jpy: float,
    price_usd: float,
    url: str,
    thumbnail: Optional[str],
    keyword: str,
    alerted: bool = False,
) -> int:
    """Insert a new listing and return its row id."""
    seen_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO listings
                (title, price_jpy, price_usd, url, thumbnail, keyword, seen_at, alerted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, price_jpy, price_usd, url, thumbnail, keyword, seen_at, int(alerted)),
        )
        return cursor.lastrowid


def mark_alerted(url: str) -> None:
    """Mark a listing as having triggered a Telegram alert."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE listings SET alerted = 1 WHERE url = ?", (url,)
        )


def get_recent_stats(minutes: int = 15) -> dict:
    """Return counts of listings checked and alerted in the last N minutes."""
    cutoff = datetime.utcnow()
    cutoff_str = cutoff.isoformat()
    # subtract minutes manually to avoid importing timedelta here
    from datetime import timedelta
    cutoff_str = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()

    with get_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM listings WHERE seen_at >= ?", (cutoff_str,)
        ).fetchone()[0]
        alerted = conn.execute(
            "SELECT COUNT(*) FROM listings WHERE seen_at >= ? AND alerted = 1",
            (cutoff_str,),
        ).fetchone()[0]
    return {"checked": total, "alerted": alerted, "window_minutes": minutes}


# ── Market values ──────────────────────────────────────────────────────────────

def get_market_value(keyword: str) -> Optional[float]:
    """Return the estimated USD market value for a keyword, or None."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT estimated_usd FROM market_values WHERE keyword = ?",
            (keyword.lower(),),
        ).fetchone()
        return float(row["estimated_usd"]) if row else None


def set_market_value(keyword: str, estimated_usd: float) -> None:
    """Upsert a market value estimate for a keyword."""
    updated_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO market_values (keyword, estimated_usd, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(keyword) DO UPDATE SET
                estimated_usd = excluded.estimated_usd,
                updated_at    = excluded.updated_at
            """,
            (keyword.lower(), estimated_usd, updated_at),
        )
    logger.info("Market value updated: %s → $%.2f", keyword, estimated_usd)


def get_all_market_values() -> list[dict]:
    """Return all market value rows as a list of dicts."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT keyword, estimated_usd, updated_at FROM market_values ORDER BY keyword"
        ).fetchall()
        return [dict(r) for r in rows]


def seed_market_values(values: dict[str, float]) -> None:
    """Seed market values from a dict without overwriting existing entries."""
    with get_connection() as conn:
        updated_at = datetime.utcnow().isoformat()
        conn.executemany(
            """
            INSERT OR IGNORE INTO market_values (keyword, estimated_usd, updated_at)
            VALUES (?, ?, ?)
            """,
            [(k.lower(), v, updated_at) for k, v in values.items()],
        )
    logger.debug("Seeded %d market value entries", len(values))
