"""
sniper/vinted.py — Vinted sniper actions for FlipScout.

Polls Vinted España for new listings matching a snipe target.
Actions: favourite item, send message to seller, optional auto-buy.

IMPORTANT: auto_buy=True requires an active Vinted session with a saved
payment method. Every auto-purchase is logged to the audit log.
A global kill switch and daily spend limit are enforced in sniper/core.py.
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

_SEARCH_URL = "https://www.vinted.es/api/v2/catalog/items"
_FAVOURITE_URL = "https://www.vinted.es/api/v2/items/{item_id}/favourite"
_MESSAGE_URL = "https://www.vinted.es/api/v2/conversations"
_BUY_URL = "https://www.vinted.es/api/v2/transactions"

_OPENER_MESSAGE = (
    "Hola, me interesa mucho tu artículo. "
    "¿Podrías reservármelo? Puedo comprarlo hoy mismo 😊"
)


def _polite_sleep(lo: float = 1.5, hi: float = 3.0) -> None:
    time.sleep(random.uniform(lo, hi))


def poll_vinted(
    query: str,
    max_price_eur: float,
    max_results: int = 30,
) -> list[SpanishListing]:
    """Poll Vinted España for newest listings matching query."""
    params = {
        "search_text": query,
        "order": "newest_first",
        "per_page": min(max_results, 96),
        "page": 1,
        "price_to": max_price_eur,
    }

    try:
        _polite_sleep(1.5, 3.0)
        resp = cffi_requests.get(
            _SEARCH_URL,
            params=params,
            headers=session_manager.get_vinted_headers(),
            cookies=session_manager.get_vinted_cookies(),
            impersonate="chrome120",
            timeout=15,
        )

        if resp.status_code == 401:
            logger.warning("Vinted sniper: 401 — session expired or missing")
            return []
        if resp.status_code == 429:
            logger.warning("Vinted sniper: rate limited, backing off 60s")
            time.sleep(60)
            return []

        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Vinted poll failed for '%s': %s", query, exc)
        return []

    results: list[SpanishListing] = []
    for item in data.get("items", [])[:max_results]:
        try:
            price_eur = float(item.get("price", 0))
            if price_eur <= 0:
                continue
            item_id = item.get("id", "")
            results.append(SpanishListing(
                title=item.get("title", ""),
                price_eur=price_eur,
                url=item.get("url") or f"https://www.vinted.es/items/{item_id}",
                platform="vinted",
                condition=None,
                location=item.get("city"),
            ))
        except (KeyError, TypeError, ValueError):
            continue

    return results


def favourite_item(item_id: str) -> bool:
    """Add item to favourites (signals interest to seller)."""
    try:
        _polite_sleep(0.5, 1.0)
        resp = cffi_requests.post(
            _FAVOURITE_URL.format(item_id=item_id),
            headers=session_manager.get_vinted_headers(),
            cookies=session_manager.get_vinted_cookies(),
            impersonate="chrome120",
            timeout=10,
        )
        success = resp.status_code in (200, 201)
        if success:
            logger.info("Vinted: favourited item %s", item_id)
        else:
            logger.debug("Vinted favourite failed for %s: HTTP %d", item_id, resp.status_code)
        return success
    except Exception as exc:
        logger.debug("Vinted favourite error for %s: %s", item_id, exc)
        return False


def send_vinted_message(item_id: str, message: str = _OPENER_MESSAGE) -> bool:
    """Send an opening message to the item seller via Vinted conversations API."""
    payload = {
        "item_id": item_id,
        "body": message,
    }
    try:
        _polite_sleep(0.5, 1.5)
        resp = cffi_requests.post(
            _MESSAGE_URL,
            json=payload,
            headers=session_manager.get_vinted_headers(),
            cookies=session_manager.get_vinted_cookies(),
            impersonate="chrome120",
            timeout=15,
        )
        success = resp.status_code in (200, 201)
        if success:
            logger.info("Vinted message sent to seller of item %s", item_id)
        else:
            logger.warning(
                "Vinted message failed for item %s: HTTP %d", item_id, resp.status_code
            )
        return success
    except Exception as exc:
        logger.warning("Vinted message error for item %s: %s", item_id, exc)
        return False


def attempt_auto_buy(item_id: str, listing_title: str) -> bool:
    """
    Attempt to trigger Vinted checkout for an item.

    SAFETY: This function should only be called when:
    1. The snipe target explicitly has auto_buy=True
    2. The global kill switch is NOT active
    3. The daily spend limit has NOT been reached

    All preconditions are enforced in sniper/core.py — NOT here.
    Uses the existing saved payment method in the active Vinted session.
    """
    payload = {
        "item_id": item_id,
        "payment_method": "saved",    # Uses saved card in Vinted account
    }
    try:
        _polite_sleep(0.3, 0.8)
        resp = cffi_requests.post(
            _BUY_URL,
            json=payload,
            headers=session_manager.get_vinted_headers(),
            cookies=session_manager.get_vinted_cookies(),
            impersonate="chrome120",
            timeout=20,
        )
        success = resp.status_code in (200, 201)
        if success:
            logger.info(
                "Vinted AUTO-BUY SUCCESS: item_id=%s title='%s'",
                item_id, listing_title[:60],
            )
        else:
            logger.error(
                "Vinted auto-buy FAILED: item_id=%s HTTP %d body=%s",
                item_id, resp.status_code, resp.text[:200],
            )
        return success
    except Exception as exc:
        logger.error("Vinted auto-buy exception for item %s: %s", item_id, exc)
        return False


def extract_item_id(vinted_url: str) -> Optional[str]:
    """Extract Vinted item ID from a listing URL."""
    # URLs like: https://www.vinted.es/items/12345678-title
    parts = vinted_url.rstrip("/").split("/")
    for part in reversed(parts):
        if part and part[0].isdigit():
            return part.split("-")[0]
    return None
