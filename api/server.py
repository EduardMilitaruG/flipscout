"""
api/server.py — FastAPI REST server for the FlipScout dashboard.

Auth model:
  - GET endpoints: public (demo visitors can browse deals)
  - POST/PATCH/DELETE sniper endpoints: require Bearer JWT
  - Login: POST /api/auth/login  →  { access_token, token_type }
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

import db

logger = logging.getLogger(__name__)

# ── Auth config ────────────────────────────────────────────────────────────────

SECRET_KEY  = os.environ.get("JWT_SECRET_KEY", "flipscout-dev-secret-change-in-production")
ALGORITHM   = "HS256"
TOKEN_TTL_H = 24

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "flipscout2026")   # override via env var

pwd_ctx    = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2     = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Hash the password at startup so we never store plaintext
_HASHED_PW = pwd_ctx.hash(ADMIN_PASSWORD)


def _create_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=TOKEN_TTL_H)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def _verify_token(token: str = Depends(oauth2)) -> str:
    """Dependency — validates JWT and returns username, or raises 401."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise ValueError
        return username
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── App ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="FlipScout API",
    description="Deal data and sniper management for the FlipScout dashboard",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth ───────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/api/auth/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    """Exchange username + password for a JWT access token."""
    if form.username != ADMIN_USERNAME or not pwd_ctx.verify(form.password, _HASHED_PW):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=_create_token(form.username))


# ── Deals (public) ─────────────────────────────────────────────────────────────

@app.get("/api/deals")
def list_deals(
    category: Optional[str] = Query(None),
    min_margin: float = Query(0.0),
    marketplace: Optional[str] = Query(None),
    high_confidence: bool = Query(False),
    limit: int = Query(100, le=500),
):
    return db.get_deals(
        category=category,
        min_margin=min_margin,
        marketplace=marketplace,
        high_confidence_only=high_confidence,
        limit=limit,
    )


@app.get("/api/deals/{deal_id}")
def get_deal(deal_id: int):
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT l.*, d.* FROM deals d JOIN listings l ON l.url = d.listing_url WHERE d.id = ?",
            (deal_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Deal not found")
    return dict(row)


@app.get("/api/stats/today")
def today_stats():
    return db.get_today_stats()


# ── Sniper targets ─────────────────────────────────────────────────────────────

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
    with db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM snipe_targets ORDER BY created_at DESC").fetchall()
        targets = []
        for row in rows:
            t = dict(row)
            t["platform"] = json.loads(t["platform"])
            targets.append(t)
        return targets


@app.post("/api/sniper/targets", status_code=201)
def create_snipe_target(target: SnipeTargetCreate, _: str = Depends(_verify_token)):
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
def toggle_snipe_target(target_id: str, active: bool, _: str = Depends(_verify_token)):
    db.set_snipe_target_active(target_id, active)
    return {"status": "ok", "id": target_id, "active": active}


@app.delete("/api/sniper/targets/{target_id}", status_code=204)
def delete_snipe_target(target_id: str, _: str = Depends(_verify_token)):
    db.delete_snipe_target(target_id)


@app.get("/api/sniper/events")
def sniper_events(limit: int = Query(50, le=200)):
    with db.get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM snipe_events ORDER BY occurred_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


@app.post("/api/sniper/pause-all")
def pause_sniper(_: str = Depends(_verify_token)):
    from sniper.core import pause_all
    pause_all()
    return {"status": "paused"}


@app.post("/api/sniper/resume-all")
def resume_sniper(_: str = Depends(_verify_token)):
    from sniper.core import resume_all
    resume_all()
    return {"status": "resumed"}


@app.get("/api/sniper/status")
def sniper_status():
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
    import uvicorn
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")
