"""
sniper/wallapop.py — Wallapop sniper actions for FlipScout.

Polls Wallapop for new listings matching a snipe target,
then messages the seller and/or sends a high-priority alert.
Auto-buy is NOT supported on Wallapop (no API endpoint exists).
"""

from __future__ import annotations

import logging
import random
import time
from typing import Optional

from curl_cffi import requests as cffi_requests

from scrapers.base import SpanishListing
from sniper.session_manager import session_manager

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://api.wallapop.com/api/v3/general/search"
_CHAT_URL = "https://api.wallapop.com/api/v3/conversations"

# Opening message sent to seller on match
_OPENER_MESSAGE = (
    "Hola, estoy muy interesado en tu artículo. "
    "¿Podrías reservármelo? Puedo pagar ahora mismo. Gracias 🙏"
)


def _polite_sleep(lo: float = 1.5, hi: float = 3.5) -> None:
    time.sleep(random.uniform(lo, hi))


def poll_wallapop(
    query: str,
    max_price_eur: float,
    max_results: int = 30,
) -> list[SpanishListing]:
    """
    Poll Wallapop for the newest listings matching query.
    Results sorted by newest first (most likely unseen).
    """
    params = {
        "keywords": query,
        "language": "es_ES",
        "order_by": "newest",
        "country_code": "ES",
        "max_sale_price": int(max_price_eur * 100),
        "filters_source": "search_box",
    }

    headers = session_manager.get_wallapop_headers()

    try:
        _polite_sleep(1.0, 2.5)
        resp = cffi_requests.get(
            _SEARCH_URL,
            params=params,
            headers=headers,
            impersonate="chrome120",
            timeout=15,
        )

        if resp.status_code == 429:
            logger.warning("Wallapop sniper: rate limited, backing off 60s")
            time.sleep(60)
            return []

        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Wallapop poll failed for '%s': %s", query, exc)
        return []

    results: list[SpanishListing] = []
    items = data.get("data", {}).get("section", {}).get("payload", {}).get("items", [])

    for item in items[:max_results]:
        try:
            content = item.get("content", {})
            price_raw = content.get("price", {})
            price_eur = (
                float(price_raw.get("amount", 0)) / 100
                if isinstance(price_raw, dict)
                else float(price_raw)
            )
            if price_eur <= 0:
                continue

            item_id = content.get("id", "")
            slug = content.get("web_slug", item_id)

            results.append(SpanishListing(
                title=content.get("title", ""),
                price_eur=price_eur,
                url=f"https://es.wallapop.com/item/{slug}",
                platform="wallapop",
                condition=content.get("condition"),
                location=content.get("location", {}).get("city"),
            ))
        except (KeyError, TypeError, ValueError):
            continue

    return results


def send_wallapop_message(item_id: str, message: str = _OPENER_MESSAGE) -> bool:
    """
    Send an opening message to a Wallapop seller via the chat API.
    Requires WALLAPOP_AUTH_TOKEN to be set in .env.

    Returns True on success, False on failure.
    """
    token = session_manager.get_wallapop_token()
    if not token:
        logger.warning(
            "Wallapop messaging skipped — WALLAPOP_AUTH_TOKEN not set in .env"
        )
        return False

    payload = {
        "item_id": item_id,
        "message": message,
        "type": "text",
    }

    try:
        _polite_sleep(0.5, 1.5)
        resp = cffi_requests.post(
            _CHAT_URL,
            json=payload,
            headers=session_manager.get_wallapop_headers(),
            impersonate="chrome120",
            timeout=15,
        )
        if resp.status_code in (200, 201):
            logger.info("Wallapop message sent to seller of item %s", item_id)
            return True
        logger.warning(
            "Wallapop message failed for item %s: HTTP %d", item_id, resp.status_code
        )
        return False
    except Exception as exc:
        logger.warning("Wallapop message error for item %s: %s", item_id, exc)
        return False


def extract_item_id(wallapop_url: str) -> Optional[str]:
    """Extract the item ID from a Wallapop listing URL."""
    # URLs like: https://es.wallapop.com/item/some-slug-12345678
    parts = wallapop_url.rstrip("/").split("/")
    if parts:
        slug = parts[-1]
        # Item ID is often embedded at the end of the slug after last dash
        return slug
    return None
