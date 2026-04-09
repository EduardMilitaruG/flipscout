"""
db.py — SQLite database layer for FlipScout.

Tables:
  listings        — Japanese marketplace listings found
  market_values   — Estimated USD market value per keyword
  deals           — Enriched listings with full margin calculations
  snipe_targets   — User-configured snipe targets (Wallapop / Vinted)
  snipe_events    — Audit log of every sniper action taken
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "flipscout.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create all tables and indexes if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            -- ── Japanese marketplace listings ────────────────────────────────
            CREATE TABLE IF NOT EXISTS listings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                price_jpy   REAL    NOT NULL,
                price_usd   REAL    NOT NULL,
                url         TEXT    NOT NULL UNIQUE,
                thumbnail   TEXT,
                keyword     TEXT    NOT NULL,
                category    TEXT    NOT NULL DEFAULT 'general',
                marketplace TEXT    NOT NULL DEFAULT 'zenmarket',
                condition   TEXT,
                seen_at     TEXT    NOT NULL,
                alerted     INTEGER NOT NULL DEFAULT 0
            );

            -- ── Market value references (USD) ─────────────────────────────
            CREATE TABLE IF NOT EXISTS market_values (
                keyword         TEXT    PRIMARY KEY,
                estimated_usd   REAL    NOT NULL,
                updated_at      TEXT    NOT NULL
            );

            -- ── Enriched deals with full margin data ──────────────────────
            CREATE TABLE IF NOT EXISTS deals (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                listing_url         TEXT    NOT NULL REFERENCES listings(url) ON DELETE CASCADE,
                jp_price_eur        REAL    NOT NULL,
                shipping_eur        REAL    NOT NULL,
                platform_fee_eur    REAL    NOT NULL,
                spanish_resale_eur  REAL    NOT NULL,
                comparable_count    INTEGER NOT NULL DEFAULT 0,
                gross_margin_eur    REAL    NOT NULL,
                margin_pct          REAL    NOT NULL,
                is_risky            INTEGER NOT NULL DEFAULT 0,
                confidence          TEXT    NOT NULL DEFAULT 'low',
                created_at          TEXT    NOT NULL
            );

            -- ── Snipe targets ─────────────────────────────────────────────
            CREATE TABLE IF NOT EXISTS snipe_targets (
                id                  TEXT    PRIMARY KEY,
                query               TEXT    NOT NULL,
                category            TEXT    NOT NULL DEFAULT 'general',
                platform            TEXT    NOT NULL,   -- JSON array: ["wallapop","vinted"]
                max_buy_price_eur   REAL    NOT NULL,
                min_margin_pct      REAL    NOT NULL DEFAULT 20.0,
                auto_buy            INTEGER NOT NULL DEFAULT 0,
                reserve_on_match    INTEGER NOT NULL DEFAULT 1,
                active              INTEGER NOT NULL DEFAULT 1,
                created_at          TEXT    NOT NULL,
                updated_at          TEXT    NOT NULL
            );

            -- ── Sniper audit log (append-only) ────────────────────────────
            CREATE TABLE IF NOT EXISTS snipe_events (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id       TEXT    NOT NULL REFERENCES snipe_targets(id),
                listing_url     TEXT    NOT NULL,
                listing_title   TEXT    NOT NULL,
                platform        TEXT    NOT NULL,
                listing_price_eur REAL  NOT NULL,
                calc_margin_pct REAL,
                action          TEXT    NOT NULL,  -- messaged | auto_bought | alert_only | skipped
                notes           TEXT,
                occurred_at     TEXT    NOT NULL
            );

            -- ── Indexes ───────────────────────────────────────────────────
            CREATE INDEX IF NOT EXISTS idx_listings_keyword  ON listings (keyword);
            CREATE INDEX IF NOT EXISTS idx_listings_seen_at  ON listings (seen_at);
            CREATE INDEX IF NOT EXISTS idx_listings_category ON listings (category);
            CREATE INDEX IF NOT EXISTS idx_deals_margin      ON deals (margin_pct DESC);
            CREATE INDEX IF NOT EXISTS idx_snipe_active      ON snipe_targets (active);
            CREATE INDEX IF NOT EXISTS idx_snipe_events_time ON snipe_events (occurred_at);
        """)
    logger.info("Database initialised at %s", DB_PATH)


# ── Listings ───────────────────────────────────────────────────────────────────

def listing_exists(url: str) -> bool:
    with get_connection() as conn:
        row = conn.execute("SELECT 1 FROM listings WHERE url = ?", (url,)).fetchone()
        return row is not None


def insert_listing(
    title: str,
    price_jpy: float,
    price_usd: float,
    url: str,
    thumbnail: Optional[str],
    keyword: str,
    category: str = "general",
    marketplace: str = "zenmarket",
    condition: Optional[str] = None,
    alerted: bool = False,
) -> int:
    seen_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO listings
                (title, price_jpy, price_usd, url, thumbnail, keyword,
                 category, marketplace, condition, seen_at, alerted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, price_jpy, price_usd, url, thumbnail, keyword,
             category, marketplace, condition, seen_at, int(alerted)),
        )
        return cursor.lastrowid or 0


def mark_alerted(url: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE listings SET alerted = 1 WHERE url = ?", (url,))


def get_recent_stats(minutes: int = 60) -> dict:
    cutoff = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()
    with get_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM listings WHERE seen_at >= ?", (cutoff,)
        ).fetchone()[0]
        alerted = conn.execute(
            "SELECT COUNT(*) FROM listings WHERE seen_at >= ? AND alerted = 1", (cutoff,)
        ).fetchone()[0]
        best = conn.execute(
            """SELECT l.title, d.gross_margin_eur, d.margin_pct
               FROM deals d JOIN listings l ON l.url = d.listing_url
               WHERE d.created_at >= ?
               ORDER BY d.margin_pct DESC LIMIT 1""",
            (cutoff,),
        ).fetchone()
    return {
        "checked": total,
        "alerted": alerted,
        "window_minutes": minutes,
        "best_deal": dict(best) if best else None,
    }


# ── Market values ──────────────────────────────────────────────────────────────

def get_market_value(keyword: str) -> Optional[float]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT estimated_usd FROM market_values WHERE keyword = ?",
            (keyword.lower(),),
        ).fetchone()
        return float(row["estimated_usd"]) if row else None


def set_market_value(keyword: str, estimated_usd: float) -> None:
    updated_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO market_values (keyword, estimated_usd, updated_at)
               VALUES (?, ?, ?)
               ON CONFLICT(keyword) DO UPDATE SET
                   estimated_usd = excluded.estimated_usd,
                   updated_at    = excluded.updated_at""",
            (keyword.lower(), estimated_usd, updated_at),
        )


def get_all_market_values() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT keyword, estimated_usd, updated_at FROM market_values ORDER BY keyword"
        ).fetchall()
        return [dict(r) for r in rows]


def seed_market_values(values: dict[str, float]) -> None:
    with get_connection() as conn:
        updated_at = datetime.utcnow().isoformat()
        conn.executemany(
            """INSERT OR IGNORE INTO market_values (keyword, estimated_usd, updated_at)
               VALUES (?, ?, ?)""",
            [(k.lower(), v, updated_at) for k, v in values.items()],
        )


# ── Deals ──────────────────────────────────────────────────────────────────────

def insert_deal(
    listing_url: str,
    jp_price_eur: float,
    shipping_eur: float,
    platform_fee_eur: float,
    spanish_resale_eur: float,
    comparable_count: int,
    gross_margin_eur: float,
    margin_pct: float,
    is_risky: bool,
    confidence: str,
) -> int:
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT OR REPLACE INTO deals
               (listing_url, jp_price_eur, shipping_eur, platform_fee_eur,
                spanish_resale_eur, comparable_count, gross_margin_eur,
                margin_pct, is_risky, confidence, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (listing_url, jp_price_eur, shipping_eur, platform_fee_eur,
             spanish_resale_eur, comparable_count, gross_margin_eur,
             margin_pct, int(is_risky), confidence, created_at),
        )
        return cursor.lastrowid or 0


def get_deals(
    category: Optional[str] = None,
    min_margin: float = 0.0,
    marketplace: Optional[str] = None,
    high_confidence_only: bool = False,
    limit: int = 100,
) -> list[dict]:
    query = """
        SELECT l.title, l.url, l.thumbnail, l.price_jpy, l.category,
               l.marketplace, l.condition, l.seen_at,
               d.jp_price_eur, d.shipping_eur, d.platform_fee_eur,
               d.spanish_resale_eur, d.comparable_count,
               d.gross_margin_eur, d.margin_pct, d.is_risky, d.confidence
        FROM deals d
        JOIN listings l ON l.url = d.listing_url
        WHERE d.margin_pct >= ?
    """
    params: list = [min_margin]

    if category:
        query += " AND l.category = ?"
        params.append(category)
    if marketplace:
        query += " AND l.marketplace = ?"
        params.append(marketplace)
    if high_confidence_only:
        query += " AND d.confidence = 'high'"

    query += " ORDER BY d.margin_pct DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def get_today_stats() -> dict:
    today = datetime.utcnow().date().isoformat()
    with get_connection() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM deals WHERE created_at >= ?", (today,)
        ).fetchone()[0]
        avg_margin = conn.execute(
            "SELECT AVG(margin_pct) FROM deals WHERE created_at >= ?", (today,)
        ).fetchone()[0] or 0.0
        best = conn.execute(
            """SELECT l.title, d.gross_margin_eur, d.margin_pct
               FROM deals d JOIN listings l ON l.url = d.listing_url
               WHERE d.created_at >= ?
               ORDER BY d.margin_pct DESC LIMIT 1""",
            (today,),
        ).fetchone()
    return {
        "total_deals_today": total,
        "avg_margin_pct": round(avg_margin, 1),
        "best_deal": dict(best) if best else None,
    }


# ── Snipe targets ──────────────────────────────────────────────────────────────

def upsert_snipe_target(
    target_id: str,
    query: str,
    category: str,
    platform: str,          # JSON-encoded list
    max_buy_price_eur: float,
    min_margin_pct: float,
    auto_buy: bool,
    reserve_on_match: bool,
    active: bool = True,
) -> None:
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO snipe_targets
               (id, query, category, platform, max_buy_price_eur, min_margin_pct,
                auto_buy, reserve_on_match, active, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                   query = excluded.query,
                   category = excluded.category,
                   platform = excluded.platform,
                   max_buy_price_eur = excluded.max_buy_price_eur,
                   min_margin_pct = excluded.min_margin_pct,
                   auto_buy = excluded.auto_buy,
                   reserve_on_match = excluded.reserve_on_match,
                   active = excluded.active,
                   updated_at = excluded.updated_at""",
            (target_id, query, category, platform, max_buy_price_eur,
             min_margin_pct, int(auto_buy), int(reserve_on_match),
             int(active), now, now),
        )


def get_active_snipe_targets() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM snipe_targets WHERE active = 1 ORDER BY created_at"
        ).fetchall()
        return [dict(r) for r in rows]


def set_snipe_target_active(target_id: str, active: bool) -> None:
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            "UPDATE snipe_targets SET active = ?, updated_at = ? WHERE id = ?",
            (int(active), now, target_id),
        )


def delete_snipe_target(target_id: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM snipe_targets WHERE id = ?", (target_id,))


# ── Snipe event audit log ──────────────────────────────────────────────────────

def log_snipe_event(
    target_id: str,
    listing_url: str,
    listing_title: str,
    platform: str,
    listing_price_eur: float,
    action: str,
    calc_margin_pct: Optional[float] = None,
    notes: Optional[str] = None,
) -> None:
    """Append-only audit log — never update or delete."""
    occurred_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO snipe_events
               (target_id, listing_url, listing_title, platform,
                listing_price_eur, calc_margin_pct, action, notes, occurred_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (target_id, listing_url, listing_title, platform,
             listing_price_eur, calc_margin_pct, action, notes, occurred_at),
        )


def snipe_listing_seen(target_id: str, listing_url: str) -> bool:
    """Return True if this listing was already processed for this snipe target."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM snipe_events WHERE target_id = ? AND listing_url = ?",
            (target_id, listing_url),
        ).fetchone()
        return row is not None
