"""
categories/base.py — Abstract base for category-specific logic in FlipScout.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from scrapers.base import Listing


@dataclass
class CategoryMatch:
    """Result of running category-specific parsing on a listing title."""
    category: str
    search_query_es: str          # Optimised query to use on Spanish resale platforms
    condition: Optional[str]      # mint | good | fair | junk (if extractable)
    extra: dict                   # Category-specific metadata (model, grade, size, etc.)
    weight_g: Optional[float]     # Estimated weight if category provides it


class BaseCategory(ABC):
    """
    Each category implements title parsing and query building for Spanish resale.
    Categories are stateless — all methods are pure functions of the input.
    """

    name: str = "general"

    @abstractmethod
    def matches(self, title: str) -> bool:
        """Return True if this category's logic applies to the given title."""
        ...

    @abstractmethod
    def parse(self, listing: Listing) -> CategoryMatch:
        """
        Extract structured data from the listing title and build an optimised
        Spanish resale search query.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
