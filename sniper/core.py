"""
sniper/core.py — Sniper orchestration engine for FlipScout.

Polls Wallapop and Vinted for active snipe targets, runs margin checks,
and triggers actions (message / auto-buy / alert).

Safety guardrails:
  - auto_buy must be explicitly set per target
  - Global kill switch: set SNIPER_PAUSED=1 in env or call pause_all()
  - Daily spend limit enforced via DB audit log
  - Every action logged to snipe_events (append-only)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from typing import Optional

import db
from margin import calculate_margin, jpy_to_eur
from scrapers.base import SpanishListing
from scrapers.wallapop_es import search_wallapop
from scrapers.vinted_es import search_vinted
from sniper import wallapop as wp_sniper
from sniper import vinted as vt_sniper
from sniper.session_manager import session_manager

logger = logging.getLogger(__name__)

_POLL_INTERVAL_BASE = 90    # seconds
_POLL_JITTER = 30           # ±30s randomisation
_MAX_DAILY_SPEND_EUR = float(os.environ.get("SNIPER_MAX_DAILY_SPEND_EUR", "500"))
_KILL_SWITCH_ENV = "SNIPER_PAUSED"

# Global kill switch (also settable at runtime)
_paused = False


def pause_all() -> None:
    global _paused
    _paused = True
    logger.warning("SNIPER PAUSED — all polling stopped")


def resume_all() -> None:
    global _paused
    _paused = False
    logger.info("Sniper RESUMED")


def is_paused() -> bool:
    return _paused or os.environ.get(_KILL_SWITCH_ENV, "").strip() == "1"


def _daily_spend_eur() -> float:
    """Sum of auto-buy purchases in the last 24h from audit log."""
    today = (datetime.utcnow() - timedelta(days=1)).isoformat()
    with db.get_connection() as conn:
        row = conn.execute(
            """SELECT COALESCE(SUM(listing_price_eur), 0)
               FROM snipe_events
               WHERE action = 'auto_bought' AND occurred_at >= ?""",
            (today,),
        ).fetchone()
        return float(row[0])


def _within_spend_limit() -> bool:
    spent = _daily_spend_eur()
    if spent >= _MAX_DAILY_SPEND_EUR:
        logger.warning(
            "Daily spend limit reached: €%.2f / €%.2f — auto-buy suspended",
            spent, _MAX_DAILY_SPEND_EUR,
        )
        return False
    return True


async def process_snipe_target(
    target: dict,
    alert_callback,          # async fn(target, listing, action, margin_pct)
) -> None:
    """
    Process a single snipe target: poll → check margin → act.

    alert_callback is injected by main.py and handles Telegram/Discord alerts.
    """
    target_id = target["id"]
    query = target["query"]
    max_price = float(target["max_buy_price_eur"])
    min_margin = float(target["min_margin_pct"])
    auto_buy = bool(target["auto_buy"])
    reserve = bool(target["reserve_on_match"])
    platforms = json.loads(target["platform"])

    logger.info("Sniper polling target '%s' on %s", query, platforms)

    for platform in platforms:
        if is_paused():
            logger.info("Sniper paused — skipping target '%s'", query)
            return

        # Poll platform
        listings: list[SpanishListing] = []
        if platform == "wallapop":
            listings = wp_sniper.poll_wallapop(query, max_price)
        elif platform == "vinted":
            listings = vt_sniper.poll_vinted(query, max_price)

        for listing in listings:
            if db.snipe_listing_seen(target_id, listing.url):
                continue

            # Quick price filter before expensive margin calc
            if listing.price_eur > max_price:
                db.log_snipe_event(
                    target_id, listing.url, listing.title,
                    platform, listing.price_eur,
                    action="skipped", notes="above max price",
                )
                continue

            # Margin check: fetch comparables from the OTHER Spanish platforms
            # (we're buying THIS listing, so compare against other sellers)
            comparables: list[SpanishListing] = []
            try:
                comparables += search_wallapop(query, max_results=10)
                comparables += search_vinted(query, max_results=10)
                # Exclude the listing itself
                comparables = [c for c in comparables if c.url != listing.url]
            except Exception as exc:
                logger.debug("Comparable fetch failed for sniper: %s", exc)

            # Build a synthetic Listing for margin calc
            from scrapers.base import Listing as JpListing
            from categories.router import detect_category

            synth = JpListing(
                title=listing.title,
                price_jpy=listing.price_eur / 0.0062,  # approximate back to JPY for weight est
                price_usd=listing.price_eur / 0.92,
                url=listing.url,
                keyword=query,
                category=target.get("category", "general"),
            )
            match = detect_category(synth)
            synth.category = match.category
            synth.weight_g = match.weight_g

            margin = calculate_margin(synth, comparables) if comparables else None
            margin_pct = margin.margin_pct if margin else None

            # Decision logic
            if margin_pct is not None and margin_pct < min_margin:
                db.log_snipe_event(
                    target_id, listing.url, listing.title, platform,
                    listing.price_eur, action="skipped",
                    calc_margin_pct=margin_pct,
                    notes=f"margin {margin_pct:.1f}% < min {min_margin:.1f}%",
                )
                logger.debug(
                    "Sniper skip: margin %.1f%% < %.1f%% for '%s'",
                    margin_pct, min_margin, listing.title[:50],
                )
                continue

            # MATCH — take action
            action_taken = "alert_only"
            item_id = None

            if platform == "wallapop":
                item_id = wp_sniper.extract_item_id(listing.url)
            elif platform == "vinted":
                item_id = vt_sniper.extract_item_id(listing.url)

            if reserve and item_id:
                if platform == "wallapop":
                    wp_sniper.send_wallapop_message(item_id)
                    action_taken = "messaged"
                elif platform == "vinted":
                    vt_sniper.favourite_item(item_id)
                    vt_sniper.send_vinted_message(item_id)
                    action_taken = "messaged"

            if auto_buy and platform == "vinted" and item_id:
                if _within_spend_limit() and not is_paused():
                    success = vt_sniper.attempt_auto_buy(item_id, listing.title)
                    action_taken = "auto_bought" if success else "messaged"
                else:
                    logger.warning(
                        "Auto-buy blocked (paused=%s, spend_limit=%s)",
                        is_paused(), not _within_spend_limit(),
                    )

            db.log_snipe_event(
                target_id, listing.url, listing.title, platform,
                listing.price_eur, action=action_taken,
                calc_margin_pct=margin_pct,
            )

            # Fire alert
            await alert_callback(target, listing, action_taken, margin_pct)

            logger.info(
                "Sniper MATCH: '%s' on %s at €%.2f | action=%s | margin=%s%%",
                listing.title[:50], platform, listing.price_eur,
                action_taken, f"{margin_pct:.1f}" if margin_pct else "unknown",
            )


async def run_sniper_loop(alert_callback) -> None:
    """
    Main sniper loop. Runs indefinitely, polling all active targets
    at randomised intervals.
    """
    logger.info("Sniper loop started")

    while True:
        if is_paused():
            await asyncio.sleep(30)
            continue

        targets = db.get_active_snipe_targets()
        if not targets:
            await asyncio.sleep(60)
            continue

        for target in targets:
            try:
                await process_snipe_target(target, alert_callback)
            except Exception as exc:
                logger.error(
                    "Sniper error on target '%s': %s", target.get("query", "?"), exc
                )

        jitter = random.uniform(-_POLL_JITTER, _POLL_JITTER)
        sleep_sec = _POLL_INTERVAL_BASE + jitter
        logger.debug("Sniper sleeping %.0fs before next cycle", sleep_sec)
        await asyncio.sleep(sleep_sec)
