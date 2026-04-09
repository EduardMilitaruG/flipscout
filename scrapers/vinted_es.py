"""
scrapers/vinted_es.py — Vinted España resale price fetcher.

Uses Vinted's semi-public catalog API. A session cookie is required for
authenticated requests — set VINTED_SESSION_COOKIE in .env.
Unauthenticated requests are attempted first as a fallback.
"""

from __future__ import annotations

import logging
import os
import random
import time
from typing import Optional

from curl_cffi import requests as cffi_requests

from scrapers.base import SpanishListing

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://www.vinted.es/api/v2/catalog/items"

_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.vinted.es/",
    "Origin": "https://www.vinted.es",
}

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
]

_CONDITION_MAP = {
    "6": "mint",
    "5": "good",
    "4": "good",
    "3": "fair",
    "2": "fair",
    "1": "junk",
}


def _polite_sleep(lo: float = 1.5, hi: float = 3.0) -> None:
    time.sleep(random.uniform(lo, hi))


def _get_session_cookie() -> Optional[str]:
    return os.environ.get("VINTED_SESSION_COOKIE")


def search_vinted(
    query: str,
    max_price_eur: Optional[float] = None,
    max_results: int = 20,
) -> list[SpanishListing]:
    """
    Search Vinted España for listings matching `query`.

    Args:
        query: Search term
        max_price_eur: Optional price ceiling
        max_results: Maximum results to return

    Returns:
        List of SpanishListing objects.
    """
    params: dict = {
        "search_text": query,
        "order": "price_low_to_high",
        "per_page": min(max_results, 96),
        "page": 1,
    }
    if max_price_eur is not None:
        params["price_to"] = max_price_eur

    headers = {**_HEADERS, "User-Agent": random.choice(_USER_AGENTS)}

    # Attach session cookie if available
    cookie = _get_session_cookie()
    cookies = {"_vinted_fr_session": cookie} if cookie else {}

    try:
        _polite_sleep(1.5, 3.0)
        resp = cffi_requests.get(
            _SEARCH_URL,
            params=params,
            headers=headers,
            cookies=cookies,
            impersonate="chrome120",
            timeout=15,
        )

        if resp.status_code == 401:
            logger.warning(
                "Vinted: 401 Unauthorized — set VINTED_SESSION_COOKIE in .env"
            )
            return []

        if resp.status_code == 429:
            logger.warning("Vinted: rate limited, backing off 60s")
            time.sleep(60)
            return []

        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Vinted search failed for '%s': %s", query, exc)
        return []

    results: list[SpanishListing] = []
    items = data.get("items", [])

    for item in items[:max_results]:
        try:
            price_eur = float(item.get("price", 0))
            if price_eur <= 0:
                continue

            item_id = item.get("id", "")
            url = item.get("url") or f"https://www.vinted.es/items/{item_id}"

            condition_id = str(item.get("status_id", ""))
            condition = _CONDITION_MAP.get(condition_id)

            results.append(SpanishListing(
                title=item.get("title", ""),
                price_eur=price_eur,
                url=url,
                platform="vinted",
                condition=condition,
                location=item.get("city"),
            ))
        except (KeyError, TypeError, ValueError) as exc:
            logger.debug("Skipping malformed Vinted item: %s", exc)
            continue

    logger.info("Vinted: found %d listings for '%s'", len(results), query)
    return results
