"""
scrapers/wallapop_es.py — Wallapop España resale price fetcher.

Uses Wallapop's unofficial REST API (reverse-engineered from web app network requests).
Returns Spanish comparable listings for margin calculation.
"""

from __future__ import annotations

import logging
import random
import time
from typing import Optional

from curl_cffi import requests as cffi_requests

from scrapers.base import SpanishListing

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.wallapop.com/api/v3/general/search"

_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://es.wallapop.com/",
    "Origin": "https://es.wallapop.com",
    "DeviceOS": "0",
}

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]


def _polite_sleep(lo: float = 1.5, hi: float = 3.5) -> None:
    time.sleep(random.uniform(lo, hi))


def search_wallapop(
    query: str,
    max_price_eur: Optional[float] = None,
    max_results: int = 20,
) -> list[SpanishListing]:
    """
    Search Wallapop España for listings matching `query`.

    Args:
        query: Search term (e.g. "iPhone 13 Pro 256gb")
        max_price_eur: Optional price ceiling
        max_results: Maximum number of results to return

    Returns:
        List of SpanishListing objects sorted by price ascending.
    """
    params: dict = {
        "keywords": query,
        "language": "es_ES",
        "order_by": "price_low_to_high",
        "country_code": "ES",
        "filters_source": "search_box",
    }
    if max_price_eur is not None:
        params["max_sale_price"] = int(max_price_eur * 100)  # Wallapop uses cents

    headers = {**_HEADERS, "User-Agent": random.choice(_USER_AGENTS)}

    try:
        _polite_sleep(1.0, 2.5)
        resp = cffi_requests.get(
            _BASE_URL,
            params=params,
            headers=headers,
            impersonate="chrome120",
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        logger.warning("Wallapop search failed for '%s': %s", query, exc)
        return []

    results: list[SpanishListing] = []
    items = data.get("data", {}).get("section", {}).get("payload", {}).get("items", [])

    for item in items[:max_results]:
        try:
            content = item.get("content", {})
            price_raw = content.get("price", {})
            # Price can be nested under "amount" or directly as a number
            if isinstance(price_raw, dict):
                price_eur = float(price_raw.get("amount", 0)) / 100
            else:
                price_eur = float(price_raw)

            if price_eur <= 0:
                continue

            item_id = content.get("id", "")
            slug = content.get("web_slug", item_id)
            url = f"https://es.wallapop.com/item/{slug}"

            results.append(SpanishListing(
                title=content.get("title", ""),
                price_eur=price_eur,
                url=url,
                platform="wallapop",
                condition=content.get("condition", None),
                location=content.get("location", {}).get("city", None),
            ))
        except (KeyError, TypeError, ValueError) as exc:
            logger.debug("Skipping malformed Wallapop item: %s", exc)
            continue

    logger.info("Wallapop: found %d listings for '%s'", len(results), query)
    return results
