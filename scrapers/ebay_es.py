"""
scrapers/ebay_es.py — eBay España resale price fetcher.

Uses eBay's official Finding API (free, requires API key).
Set EBAY_APP_ID in .env. Falls back to scraping completed listings
if no API key is present.
"""

from __future__ import annotations

import logging
import os
import random
import time
from typing import Optional
from xml.etree import ElementTree as ET

import requests

from scrapers.base import SpanishListing

logger = logging.getLogger(__name__)

_FINDING_API_URL = "https://svcs.ebay.com/services/search/FindingService/v1"
_GLOBAL_ID = "EBAY-ES"


def _get_app_id() -> Optional[str]:
    return os.environ.get("EBAY_APP_ID")


def _polite_sleep() -> None:
    time.sleep(random.uniform(1.0, 2.5))


def _search_via_api(
    query: str,
    max_price_eur: Optional[float],
    max_results: int,
) -> list[SpanishListing]:
    """Use the eBay Finding API (requires EBAY_APP_ID env var)."""
    app_id = _get_app_id()
    if not app_id:
        return []

    params: dict = {
        "OPERATION-NAME": "findItemsByKeywords",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": app_id,
        "RESPONSE-DATA-FORMAT": "XML",
        "REST-PAYLOAD": "",
        "keywords": query,
        "GLOBAL-ID": _GLOBAL_ID,
        "paginationInput.entriesPerPage": min(max_results, 100),
        "sortOrder": "PricePlusShippingLowest",
        "itemFilter(0).name": "ListingType",
        "itemFilter(0).value(0)": "FixedPrice",
        "itemFilter(0).value(1)": "AuctionWithBIN",
        "itemFilter(1).name": "Condition",
        "itemFilter(1).value(0)": "Used",
        "itemFilter(1).value(1)": "Like New",
    }

    if max_price_eur is not None:
        params["itemFilter(2).name"] = "MaxPrice"
        params["itemFilter(2).value"] = max_price_eur
        params["itemFilter(2).paramName"] = "Currency"
        params["itemFilter(2).paramValue"] = "EUR"

    try:
        _polite_sleep()
        resp = requests.get(_FINDING_API_URL, params=params, timeout=15)
        resp.raise_for_status()
    except Exception as exc:
        logger.warning("eBay Finding API failed for '%s': %s", query, exc)
        return []

    results: list[SpanishListing] = []

    try:
        ns = "http://www.ebay.com/marketplace/search/v1/services"
        root = ET.fromstring(resp.text)

        for item in root.findall(f".//{{{ns}}}item")[:max_results]:
            def text(tag: str) -> str:
                el = item.find(f".//{{{ns}}}{tag}")
                return el.text if el is not None and el.text else ""

            title = text("title")
            url = text("viewItemURL")
            price_str = text("currentPrice")
            condition = text("conditionDisplayName").lower() or None

            try:
                price_eur = float(price_str)
            except ValueError:
                continue

            if price_eur <= 0 or not url:
                continue

            results.append(SpanishListing(
                title=title,
                price_eur=price_eur,
                url=url,
                platform="ebay_es",
                condition=condition,
            ))
    except ET.ParseError as exc:
        logger.warning("eBay XML parse error: %s", exc)

    logger.info("eBay ES (API): found %d listings for '%s'", len(results), query)
    return results


def search_ebay_es(
    query: str,
    max_price_eur: Optional[float] = None,
    max_results: int = 20,
) -> list[SpanishListing]:
    """
    Search eBay España for comparable listings.
    Uses the Finding API if EBAY_APP_ID is set, otherwise returns empty list.
    """
    return _search_via_api(query, max_price_eur, max_results)
