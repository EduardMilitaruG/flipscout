"""
margin.py — Profit margin engine for FlipScout.

Transforms a Japanese listing + Spanish resale comparables into a full
MarginResult showing gross profit and margin % after all costs.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Optional

import requests

from scrapers.base import Listing, MarginResult, SpanishListing
from shipping import estimate_shipping_eur, estimate_weight_g, is_risky_shipping

logger = logging.getLogger(__name__)

# ── Currency rates ─────────────────────────────────────────────────────────────

_rate_cache: dict = {}
_rate_lock = threading.Lock()

PLATFORM_FEE_PCT = {
    "wallapop": 0.00,   # Wallapop: no buyer fee (seller pays ~7%)
    "vinted":   0.00,   # Vinted: buyer pays small protection fee ~3-5%
    "ebay_es":  0.00,   # eBay: buyer no fee
}

RESALE_PLATFORM_SELLER_FEE_PCT = {
    "wallapop": 0.08,   # ~8% for the seller when we resell
    "vinted":   0.05,
    "ebay_es":  0.12,
}


def _fetch_rates() -> dict:
    """Fetch EUR and USD rates for JPY. Returns {USD: float, EUR: float}."""
    try:
        resp = requests.get(
            "https://api.exchangerate-api.com/v4/latest/JPY",
            timeout=10,
        )
        resp.raise_for_status()
        rates = resp.json().get("rates", {})
        return {
            "USD": float(rates.get("USD", 0.0067)),
            "EUR": float(rates.get("EUR", 0.0062)),
            "fetched_at": time.time(),
        }
    except Exception as exc:
        logger.warning("Currency fetch failed (%s); using fallback rates", exc)
        return {"USD": 0.0067, "EUR": 0.0062, "fetched_at": 0}


def get_rates(max_age_seconds: int = 14400) -> dict:
    """Return cached rates, refreshing if older than max_age_seconds (default 4h)."""
    with _rate_lock:
        if not _rate_cache or (time.time() - _rate_cache.get("fetched_at", 0)) > max_age_seconds:
            new_rates = _fetch_rates()
            _rate_cache.update(new_rates)
            logger.info(
                "Currency rates refreshed: 1 JPY = $%.6f USD / €%.6f EUR",
                _rate_cache["USD"], _rate_cache["EUR"],
            )
        return dict(_rate_cache)


def jpy_to_eur(jpy: float) -> float:
    return round(jpy * get_rates()["EUR"], 2)


def jpy_to_usd(jpy: float) -> float:
    return round(jpy * get_rates()["USD"], 2)


# ── Margin calculation ─────────────────────────────────────────────────────────

def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def _confidence(count: int) -> str:
    if count >= 5:
        return "high"
    if count >= 2:
        return "medium"
    return "low"


def calculate_margin(
    listing: Listing,
    spanish_listings: list[SpanishListing],
    resale_platform: str = "wallapop",
) -> Optional[MarginResult]:
    """
    Calculate the full flip margin for a Japanese listing.

    Args:
        listing: The Japanese marketplace listing.
        spanish_listings: Comparable listings found on Spanish resale platforms.
        resale_platform: The platform we intend to resell on (affects seller fee).

    Returns:
        MarginResult, or None if there are no Spanish comparables.
    """
    if not spanish_listings:
        logger.debug("No Spanish comparables for '%s' — skipping margin calc", listing.title[:50])
        return None

    rates = get_rates()
    jpy_to_eur_rate = rates["EUR"]

    # 1. Japanese buy cost in EUR
    jp_price_eur = round(listing.price_jpy * jpy_to_eur_rate, 2)

    # 2. Estimated shipping
    weight_g = listing.weight_g or estimate_weight_g(listing.category, listing.title)
    shipping_eur = estimate_shipping_eur(weight_g, jpy_to_eur_rate)

    # 3. Platform fee when reselling (e.g. Wallapop takes ~8% from seller)
    spanish_prices = [s.price_eur for s in spanish_listings]
    spanish_median = _median(spanish_prices)
    seller_fee_pct = RESALE_PLATFORM_SELLER_FEE_PCT.get(resale_platform, 0.08)
    platform_fee_eur = round(spanish_median * seller_fee_pct, 2)

    # 4. Gross margin
    gross_margin_eur = round(
        spanish_median - (jp_price_eur + shipping_eur + platform_fee_eur), 2
    )
    margin_pct = round(
        (gross_margin_eur / spanish_median * 100) if spanish_median > 0 else 0.0, 1
    )

    risky = is_risky_shipping(shipping_eur, gross_margin_eur)

    logger.info(
        "Margin: '%s' | JP=€%.2f + ship=€%.2f + fee=€%.2f | ES=€%.2f | "
        "gross=€%.2f (%.1f%%) | risky=%s | n=%d",
        listing.title[:50],
        jp_price_eur, shipping_eur, platform_fee_eur,
        spanish_median,
        gross_margin_eur, margin_pct,
        risky, len(spanish_listings),
    )

    return MarginResult(
        listing=listing,
        jp_price_eur=jp_price_eur,
        shipping_eur=shipping_eur,
        platform_fee_eur=platform_fee_eur,
        spanish_resale_eur=round(spanish_median, 2),
        comparable_count=len(spanish_listings),
        gross_margin_eur=gross_margin_eur,
        margin_pct=margin_pct,
        is_risky=risky,
        confidence=_confidence(len(spanish_listings)),
    )
