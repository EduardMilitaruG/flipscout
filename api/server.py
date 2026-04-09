"""
api/server.py — FastAPI REST server for the FlipScout dashboard.

Runs alongside the bot on port 8000 (configurable via API_PORT env var).
No auth required for MVP — assumes private/local use.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FlipScout API",
    description="Deal data and sniper management for the FlipScout dashboard",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Deals ──────────────────────────────────────────────────────────────────────

@app.get("/api/deals")
def list_deals(
    category: Optional[str] = Query(None),
    min_margin: float = Query(0.0),
    marketplace: Optional[str] = Query(None),
    high_confidence: bool = Query(False),
    limit: int = Query(100, le=500),
):
    """List deals with optional filters. Sorted by margin % descending."""
    return db.get_deals(
        category=category,
        min_margin=min_margin,
        marketplace=marketplace,
        high_confidence_only=high_confidence,
        limit=limit,
    )


@app.get("/api/deals/{deal_id}")
def get_deal(deal_id: int):
    """Get a single deal by ID with full detail."""
    with db.get_connection() as conn:
        row = conn.execute(
            """SELECT l.*, d.*
               FROM deals d
               JOIN listings l ON l.url = d.listing_url
               WHERE d.id = ?""",
            (deal_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Deal not found")
    return dict(row)


@app.get("/api/stats/today")
def today_stats():
    """Stats for the current day: deal count, avg margin, best deal."""
    return db.get_today_stats()


# ── Snipe targets ──────────────────────────────────────────────────────────────

class SnipeTargetCreate(BaseModel):
    id: str
    query: str
    category: str = "general"
    platform: list[str]
    max_buy_price_eur: float
    min_margin_pct: float = 20.0
    auto_buy: bool = False
    reserve_on_match: bool = True
    active: bool = True


@app.get("/api/sniper/targets")
def list_snipe_targets():
    """List all snipe targets."""
    with db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM snipe_targets ORDER BY created_at DESC").fetchall()
        targets = []
        for row in rows:
            t = dict(row)
            t["platform"] = json.loads(t["platform"])
            targets.append(t)
        return targets


@app.post("/api/sniper/targets", status_code=201)
def create_snipe_target(target: SnipeTargetCreate):
    """Create or update a snipe target."""
    db.upsert_snipe_target(
        target_id=target.id,
        query=target.query,
        category=target.category,
        platform=json.dumps(target.platform),
        max_buy_price_eur=target.max_buy_price_eur,
        min_margin_pct=target.min_margin_pct,
        auto_buy=target.auto_buy,
        reserve_on_match=target.reserve_on_match,
        active=target.active,
    )
    return {"status": "ok", "id": target.id}


@app.patch("/api/sniper/targets/{target_id}/toggle")
def toggle_snipe_target(target_id: str, active: bool):
    """Pause or resume a snipe target."""
    db.set_snipe_target_active(target_id, active)
    return {"status": "ok", "id": target_id, "active": active}


@app.delete("/api/sniper/targets/{target_id}", status_code=204)
def delete_snipe_target(target_id: str):
    """Delete a snipe target."""
    db.delete_snipe_target(target_id)


@app.get("/api/sniper/events")
def sniper_events(limit: int = Query(50, le=200)):
    """Recent sniper events (audit log)."""
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM snipe_events ORDER BY occurred_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


@app.post("/api/sniper/pause-all")
def pause_sniper():
    """Global kill switch — pause all sniper polling."""
    from sniper.core import pause_all
    pause_all()
    return {"status": "paused"}


@app.post("/api/sniper/resume-all")
def resume_sniper():
    """Resume sniper polling after a pause."""
    from sniper.core import resume_all
    resume_all()
    return {"status": "resumed"}


@app.get("/api/sniper/status")
def sniper_status():
    """Sniper status: paused state, session health, daily spend."""
    from sniper.core import is_paused, _daily_spend_eur, _MAX_DAILY_SPEND_EUR
    from sniper.session_manager import session_manager
    return {
        "paused": is_paused(),
        "daily_spend_eur": _daily_spend_eur(),
        "daily_limit_eur": _MAX_DAILY_SPEND_EUR,
        "sessions": session_manager.get_health_summary(),
    }


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "flipscout"}


def start_api_server() -> None:
    """Start the FastAPI server. Call from main.py as an asyncio task."""
    import uvicorn
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
