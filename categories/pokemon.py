"""
categories/pokemon.py — Pokemon card category logic for FlipScout.

Detects PSA/BGS/CGC grades, raw vs graded condition, extracts card names
and sets, and queries Cardmarket for current market prices.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from categories.base import BaseCategory, CategoryMatch
from scrapers.base import Listing

logger = logging.getLogger(__name__)

# PSA grade detection
_PSA_PATTERN = re.compile(r"\b(?:psa|bgs|cgc|sgc)\s*(\d+(?:\.\d+)?)\b", re.I)
_GRADED_KEYWORDS = ["psa", "bgs", "cgc", "sgc", "graded", "slab"]
_RAW_KEYWORDS = ["raw", "ungraded", "nm", "nm-mt", "ex", "vg", "poor"]

# Common Pokemon set keywords
_SETS = [
    "base set", "jungle", "fossil", "team rocket", "gym heroes", "gym challenge",
    "neo genesis", "neo discovery", "neo revelation", "neo destiny",
    "expedition", "aquapolis", "skyridge",
    "ex ruby sapphire", "ex sandstorm", "ex dragon", "ex team magma",
    "diamond pearl", "platinum", "heartgold soulsilver",
    "black white", "xy", "sun moon", "sword shield",
    "scarlet violet",
    "japanese", "holo", "1st edition", "shadowless",
]

_POKEMON_TRIGGERS = [
    "pokemon", "pokémon", "charizard", "pikachu", "mewtwo", "blastoise",
    "venusaur", "gengar", "umbreon", "espeon", "lugia", "ho-oh",
    "psa", "bgs", "cgc",  # graded card identifiers
    "holo rare", "full art", "secret rare", "rainbow rare", "vmax", "vstar",
]

_CARD_NAME_PATTERN = re.compile(
    r"(charizard|pikachu|mewtwo|blastoise|venusaur|gengar|umbreon|espeon|"
    r"lugia|ho-oh|rayquaza|mew|darkrai|alakazam|machamp|ninetales|"
    r"gyarados|lapras|eevee|snorlax|dragonite|articuno|zapdos|moltres)",
    re.I
)


def _query_cardmarket(card_name: str, set_name: Optional[str] = None) -> Optional[float]:
    """
    Fetch the current market price (trend price) from Cardmarket for a card.
    Returns EUR price or None on failure.
    NOTE: Cardmarket has rate limits; use sparingly.
    """
    try:
        query = card_name
        if set_name:
            query = f"{card_name} {set_name}"

        url = (
            f"https://www.cardmarket.com/en/Pokemon/Products/Search"
            f"?searchString={requests.utils.quote(query)}&sortBy=price_asc"
        )
        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=15,
        )
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        # Cardmarket shows trend price in the product card
        price_el = soup.select_one(".price-container .color-primary")
        if price_el:
            price_text = price_el.get_text(strip=True).replace(",", ".").replace("€", "").strip()
            return float(price_text)
    except Exception as exc:
        logger.debug("Cardmarket lookup failed for '%s': %s", card_name, exc)

    return None


class PokemonCategory(BaseCategory):
    name = "pokemon"

    def matches(self, title: str) -> bool:
        title_lower = title.lower()
        return any(t in title_lower for t in _POKEMON_TRIGGERS)

    def parse(self, listing: Listing) -> CategoryMatch:
        title = listing.title
        title_lower = title.lower()

        # Detect grading
        psa_m = _PSA_PATTERN.search(title)
        is_graded = bool(psa_m) or any(kw in title_lower for kw in _GRADED_KEYWORDS)
        grade: Optional[float] = None
        grading_company: Optional[str] = None

        if psa_m:
            try:
                grade = float(psa_m.group(1))
            except ValueError:
                pass
            # Identify grading company
            match_text = psa_m.group(0).lower()
            for company in ["psa", "bgs", "cgc", "sgc"]:
                if company in match_text:
                    grading_company = company.upper()
                    break

        # Condition
        if is_graded and grade is not None:
            if grade >= 9:
                condition = "mint"
            elif grade >= 7:
                condition = "good"
            else:
                condition = "fair"
        elif any(kw in title_lower for kw in _RAW_KEYWORDS):
            condition = "good"
        else:
            condition = None

        # Card name
        card_m = _CARD_NAME_PATTERN.search(title)
        card_name = card_m.group(1).title() if card_m else None

        # Set name
        set_name: Optional[str] = None
        for s in _SETS:
            if s in title_lower:
                set_name = s
                break

        # Edition detection
        is_first_edition = "1st edition" in title_lower or "1st ed" in title_lower

        # Build Spanish search query
        query_parts = []
        if grading_company and grade is not None:
            query_parts.append(f"{grading_company} {int(grade)}")
        if card_name:
            query_parts.append(card_name)
        if set_name:
            query_parts.append(set_name)
        if is_first_edition:
            query_parts.append("1st edition")

        if not query_parts:
            words = [w for w in title.split() if len(w) > 3][:4]
            query_parts = words

        search_query_es = " ".join(query_parts) + " pokemon"

        # Weight: PSA slabs are ~70g, raw cards ~5g
        weight_g = 70.0 if is_graded else 5.0

        return CategoryMatch(
            category=self.name,
            search_query_es=search_query_es,
            condition=condition,
            extra={
                "card_name": card_name,
                "set_name": set_name,
                "grading_company": grading_company,
                "grade": grade,
                "is_graded": is_graded,
                "is_first_edition": is_first_edition,
            },
            weight_g=weight_g,
        )
