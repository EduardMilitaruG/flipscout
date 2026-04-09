"""
pricer.py — Price intelligence layer for Archive Scout.

Determines whether a listing is "underpriced" relative to the
estimated market value stored in the database, and calculates
a "deal score" (percentage below market value).
"""

import logging
from dataclasses import dataclass
from typing import Optional

from db import get_market_value, seed_market_values
from scrapers.base import Listing

logger = logging.getLogger(__name__)


@dataclass
class ScoredListing:
    listing: Listing
    market_value_usd: float
    discount_pct: float          # positive = cheaper than market
    is_deal: bool


def score_listing(listing: Listing, deal_threshold_pct: float) -> Optional[ScoredListing]:
    """
    Score a single listing against the stored market value for its keyword.

    Returns a ScoredListing if the market value is known, or None if there
    is no reference price to compare against.

    A listing is flagged as a "deal" when:
        discount_pct >= deal_threshold_pct
    """
    market_value = get_market_value(listing.keyword)
    if market_value is None or market_value <= 0:
        logger.debug(
            "No market value for keyword '%s' — skipping score", listing.keyword
        )
        return None

    discount_pct = ((market_value - listing.price_usd) / market_value) * 100
    is_deal = discount_pct >= deal_threshold_pct

    if is_deal:
        logger.info(
            "DEAL FOUND: '%s' at $%.2f (%.1f%% below $%.2f market value)",
            listing.title[:60],
            listing.price_usd,
            discount_pct,
            market_value,
        )
    else:
        logger.debug(
            "Not a deal: '%s' at $%.2f (%.1f%% vs $%.2f market)",
            listing.title[:60],
            listing.price_usd,
            discount_pct,
            market_value,
        )

    return ScoredListing(
        listing=listing,
        market_value_usd=market_value,
        discount_pct=round(discount_pct, 1),
        is_deal=is_deal,
    )


def score_listings(
    listings: list[Listing],
    deal_threshold_pct: float,
) -> tuple[list[ScoredListing], list[ScoredListing]]:
    """
    Score all listings.

    Returns:
        (deals, non_deals) — both lists contain only listings where a
        market value reference exists. Listings without a reference price
        are silently dropped.
    """
    deals: list[ScoredListing] = []
    non_deals: list[ScoredListing] = []

    for listing in listings:
        scored = score_listing(listing, deal_threshold_pct)
        if scored is None:
            continue
        if scored.is_deal:
            deals.append(scored)
        else:
            non_deals.append(scored)

    logger.info(
        "Scored %d listings: %d deals, %d non-deals",
        len(deals) + len(non_deals),
        len(deals),
        len(non_deals),
    )
    return deals, non_deals


def seed_from_config(market_values: dict[str, float]) -> None:
    """
    Populate the database with market value estimates from config.yaml.
    Existing entries are NOT overwritten (INSERT OR IGNORE semantics).
    """
    if not market_values:
        return
    seed_market_values(market_values)
    logger.info("Seeded %d market value entries from config", len(market_values))


def format_deal_score(discount_pct: float) -> str:
    """Return a human-readable deal score label."""
    if discount_pct >= 60:
        return f"🔥 {discount_pct:.1f}% below market"
    if discount_pct >= 40:
        return f"⚡ {discount_pct:.1f}% below market"
    return f"✅ {discount_pct:.1f}% below market"
