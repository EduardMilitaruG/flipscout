"""
categories/tech.py — Tech category logic for FlipScout.

Extracts model numbers, condition grades (Japanese A/B/C rank), and
storage/spec variants to build accurate Spanish resale search queries.
"""

from __future__ import annotations

import re
from typing import Optional

from categories.base import BaseCategory, CategoryMatch
from scrapers.base import Listing

# Model number patterns: iPhone, iPad, Samsung, PlayStation, Nintendo, GPU, etc.
_MODEL_PATTERNS = [
    # Apple
    re.compile(r"(iphone\s*\d+\s*(?:pro\s*max|pro|plus|mini)?)", re.I),
    re.compile(r"(ipad\s*(?:pro|air|mini)?\s*\d*(?:th\s*gen)?)", re.I),
    re.compile(r"(macbook\s*(?:pro|air|mini)?\s*\d*(?:inch)?)", re.I),
    re.compile(r"(airpods?\s*(?:pro|max)?)", re.I),
    # Gaming
    re.compile(r"(ps\s*[1-5](?:\s*pro)?|playstation\s*[1-5])", re.I),
    re.compile(r"(nintendo\s*switch\s*(?:lite|oled)?)", re.I),
    re.compile(r"(game\s*boy\s*(?:advance|color|pocket|sp)?)", re.I),
    re.compile(r"(xbox\s*(?:one|series\s*[xs])?)", re.I),
    # GPUs
    re.compile(r"(rtx\s*\d{4}\s*(?:ti|super)?)", re.I),
    re.compile(r"(gtx\s*\d{4}\s*(?:ti)?)", re.I),
    re.compile(r"(rx\s*\d{4}\s*(?:xt)?)", re.I),
    # Samsung
    re.compile(r"(galaxy\s*s\d+\s*(?:ultra|plus)?)", re.I),
    # Sony
    re.compile(r"(sony\s*wh[-\s]*\w+|sony\s*wf[-\s]*\w+)", re.I),
    # Generic model pattern: letter+digits (e.g. A2345, X100V)
    re.compile(r"\b([A-Z]{1,3}\d{3,6}[A-Z]?)\b"),
]

# Storage capacity
_STORAGE_PATTERN = re.compile(r"\b(\d+\s*(?:gb|tb))\b", re.I)

# Japanese condition grades → standard scale
_JP_CONDITION_MAP = {
    "s": "mint",           # S rank = like new
    "a": "mint",           # A rank = excellent
    "b": "good",           # B rank = good
    "c": "fair",           # C rank = fair
    "d": "junk",           # D rank = junk
    "ジャンク": "junk",
    "junk": "junk",
    "未使用": "mint",      # Unused
    "新品": "mint",        # New
}

_JUNK_KEYWORDS = ["ジャンク", "junk", "for parts", "broken", "not working"]

# Keywords that indicate this is a tech listing
_TECH_TRIGGERS = [
    "iphone", "ipad", "macbook", "airpods", "playstation", "ps5", "ps4", "ps3",
    "nintendo", "switch", "game boy", "gameboy", "xbox", "rtx", "gtx", "gpu",
    "samsung", "galaxy", "sony", "laptop", "pc", "computer", "monitor", "keyboard",
    "camera", "lens", "fujifilm", "nikon", "canon", "sony alpha",
]


class TechCategory(BaseCategory):
    name = "tech"

    def matches(self, title: str) -> bool:
        title_lower = title.lower()
        return any(t in title_lower for t in _TECH_TRIGGERS)

    def parse(self, listing: Listing) -> CategoryMatch:
        title = listing.title
        title_lower = title.lower()

        # Extract model
        model: Optional[str] = None
        for pattern in _MODEL_PATTERNS:
            m = pattern.search(title)
            if m:
                model = m.group(1).strip()
                break

        # Extract storage
        storage_m = _STORAGE_PATTERN.search(title)
        storage = storage_m.group(1).upper() if storage_m else None

        # Extract condition
        condition: Optional[str] = None
        for jp_grade, std_grade in _JP_CONDITION_MAP.items():
            # Look for patterns like "Aランク", "A rank", "B grade"
            if re.search(rf"\b{re.escape(jp_grade)}\b", title_lower):
                condition = std_grade
                break
            if re.search(rf"\b{re.escape(jp_grade)}[\s\-_]*(rank|ランク|grade)", title_lower, re.I):
                condition = std_grade
                break

        if condition is None and any(k in title_lower for k in _JUNK_KEYWORDS):
            condition = "junk"

        # Build Spanish search query
        query_parts = []
        if model:
            query_parts.append(model)
        if storage:
            query_parts.append(storage)
        if not query_parts:
            # Fall back to first 4 meaningful words of title
            words = [w for w in title.split() if len(w) > 2][:4]
            query_parts = words

        search_query_es = " ".join(query_parts)

        return CategoryMatch(
            category=self.name,
            search_query_es=search_query_es,
            condition=condition,
            extra={
                "model": model,
                "storage": storage,
            },
            weight_g=300.0,   # Default tech weight; overridden per-item if known
        )
