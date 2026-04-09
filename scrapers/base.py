"""
scrapers/base.py — Shared types and abstract marketplace interface for FlipScout.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


# ── Shared data models ─────────────────────────────────────────────────────────

@dataclass
class Listing:
    title: str
    price_jpy: float
    price_usd: float          # kept for backward compat; margin engine uses EUR
    url: str
    keyword: str
    thumbnail: Optional[str] = None
    category: str = "general"   # tech | fashion | pokemon | general
    marketplace: str = "zenmarket"
    condition: Optional[str] = None   # mint | good | fair | junk
    weight_g: Optional[float] = None  # estimated item weight in grams


@dataclass
class SpanishListing:
    """A listing found on a Spanish resale platform (Wallapop, Vinted, eBay ES)."""
    title: str
    price_eur: float
    url: str
    platform: str             # wallapop | vinted | ebay_es
    condition: Optional[str] = None
    location: Optional[str] = None


@dataclass
class MarginResult:
    """Full profit margin calculation for a Japanese listing."""
    listing: Listing
    jp_price_eur: float
    shipping_eur: float
    platform_fee_eur: float
    spanish_resale_eur: float        # median of comparables
    comparable_count: int            # how many Spanish listings found
    gross_margin_eur: float
    margin_pct: float
    is_risky: bool                   # True if shipping > 40% of gross margin
    confidence: str                  # high | medium | low


# ── Abstract marketplace interface ─────────────────────────────────────────────

class BaseMarketplace(ABC):
    """
    Every Japanese or Spanish marketplace scraper must implement this interface.
    This allows the main job runner to iterate over all sources uniformly.
    """

    name: str = "base"
    rate_limit_ms: int = 3000   # minimum ms between requests

    @abstractmethod
    def search(
        self,
        query: str,
        category: str = "general",
        max_price_usd: float = 999,
        max_pages: int = 1,
    ) -> list[Listing]:
        """
        Search for listings matching `query`.
        Returns a list of Listing objects.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
