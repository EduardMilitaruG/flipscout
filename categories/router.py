"""
categories/router.py — Category detection router for FlipScout.

Tries each registered category in priority order. Returns a CategoryMatch
with the first matching category, or a generic fallback.
"""

from __future__ import annotations

import logging
from typing import Optional

from categories.base import BaseCategory, CategoryMatch
from categories.tech import TechCategory
from categories.fashion import FashionCategory
from categories.pokemon import PokemonCategory
from scrapers.base import Listing

logger = logging.getLogger(__name__)

# Priority order: more specific first
_REGISTRY: list[BaseCategory] = [
    PokemonCategory(),   # Most specific — check before fashion
    TechCategory(),
    FashionCategory(),
]


def detect_category(listing: Listing) -> CategoryMatch:
    """
    Run the listing title through all registered categories.
    Returns the first match, or a generic CategoryMatch as fallback.
    """
    for category in _REGISTRY:
        if category.matches(listing.title):
            match = category.parse(listing)
            logger.debug(
                "Category detected: %s → query_es='%s' [%s]",
                match.category, match.search_query_es, listing.title[:50]
            )
            return match

    # Generic fallback: use first 4 words of title
    words = [w for w in listing.title.split() if len(w) > 2][:4]
    query = " ".join(words)
    logger.debug("No category match for '%s' → generic query '%s'", listing.title[:50], query)

    return CategoryMatch(
        category="general",
        search_query_es=query,
        condition=None,
        extra={},
        weight_g=400.0,
    )


def enrich_listing(listing: Listing) -> Listing:
    """
    Run the listing through the category router and update its fields in-place.
    Returns the same listing object with category, condition, and weight set.
    """
    match = detect_category(listing)
    listing.category = match.category
    if match.condition and not listing.condition:
        listing.condition = match.condition
    if match.weight_g and not listing.weight_g:
        listing.weight_g = match.weight_g
    return listing
