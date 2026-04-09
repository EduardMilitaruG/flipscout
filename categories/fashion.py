"""
categories/fashion.py — Fashion category logic for FlipScout.

Handles Japanese → EU size conversion, brand/era detection,
and builds optimised Spanish resale search queries.
Size conversion tables live in config.yaml so they can be updated without code changes.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from categories.base import BaseCategory, CategoryMatch
from scrapers.base import Listing

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


def _load_size_tables() -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg.get("size_conversion", _default_size_tables())


def _default_size_tables() -> dict:
    return {
        "jp_to_eu_letter": {
            "XS": "XS",
            "S": "XS",
            "M": "S",
            "L": "M",
            "XL": "L",
            "XXL": "XL",
        },
        "jp_to_eu_numeric": {
            "34": "XS", "36": "XS",
            "38": "S",  "40": "S",
            "42": "M",  "44": "M",
            "46": "L",  "48": "L",
            "50": "XL", "52": "XL",
        },
    }


_FASHION_TRIGGERS = [
    "jacket", "coat", "shirt", "trousers", "pants", "jeans", "denim",
    "sweater", "hoodie", "blazer", "vest", "parka", "anorak", "bomber",
    "undercover", "number nine", "kapital", "issey miyake", "yohji yamamoto",
    "comme des garcons", "cdg", "needles", "engineered garments", "visvim",
    "nanamica", "wtaps", "neighborhood", "human made", "bape", "a bathing ape",
    "stone island", "cp company", "ralph lauren", "polo", "vintage",
]

# Era keywords for archive fashion
_ERA_KEYWORDS = ["vintage", "90s", "y2k", "2000s", "archive", "early", "ss", "aw", "fw"]

_SIZE_LETTER_PATTERN = re.compile(r"\b(XXS|XS|S|M|L|XL|XXL)\b", re.I)
_SIZE_NUMERIC_PATTERN = re.compile(r"\bsize\s*(\d{2})\b|\b(\d{2})サイズ\b", re.I)


class FashionCategory(BaseCategory):
    name = "fashion"

    def matches(self, title: str) -> bool:
        title_lower = title.lower()
        return any(t in title_lower for t in _FASHION_TRIGGERS)

    def parse(self, listing: Listing) -> CategoryMatch:
        title = listing.title
        title_lower = title.lower()
        tables = _load_size_tables()

        # Detect Japanese size labels and convert to EU
        eu_size: Optional[str] = None

        letter_m = _SIZE_LETTER_PATTERN.search(title)
        if letter_m:
            jp_size = letter_m.group(1).upper()
            eu_size = tables["jp_to_eu_letter"].get(jp_size, jp_size)

        if eu_size is None:
            num_m = _SIZE_NUMERIC_PATTERN.search(title)
            if num_m:
                num = num_m.group(1) or num_m.group(2)
                eu_size = tables["jp_to_eu_numeric"].get(num)

        # Extract brand from known list
        brand: Optional[str] = None
        for trigger in _FASHION_TRIGGERS:
            if trigger in title_lower and len(trigger) > 5:
                brand = trigger.title()
                break

        # Detect era
        era: Optional[str] = None
        for kw in _ERA_KEYWORDS:
            if kw in title_lower:
                era = kw
                break

        # Build Spanish search query
        query_parts = []
        if brand:
            query_parts.append(brand)
        if era:
            query_parts.append(era)
        if eu_size:
            query_parts.append(f"talla {eu_size}")   # "talla M" is how size is searched in Spain

        if not query_parts:
            words = [w for w in title.split() if len(w) > 3][:4]
            query_parts = words

        search_query_es = " ".join(query_parts)

        return CategoryMatch(
            category=self.name,
            search_query_es=search_query_es,
            condition=None,
            extra={
                "brand": brand,
                "era": era,
                "jp_size": letter_m.group(1) if letter_m else None,
                "eu_size": eu_size,
            },
            weight_g=500.0,
        )
