"""
shipping.py — Japan → Spain shipping cost estimator for FlipScout.

Costs are based on EMS (Express Mail Service) Japan Post weight tiers,
plus ZenMarket service and domestic Japan shipping fees.
All values are stored in config, not hardcoded — update config.yaml to
adjust rates without touching this file.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parent / "config.yaml"


def _load_shipping_config() -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg.get("shipping", _default_shipping_config())


def _default_shipping_config() -> dict:
    """Fallback config if shipping section is missing from config.yaml."""
    return {
        "zenmarket_service_fee_jpy": 500,
        "domestic_japan_shipping_jpy": 900,
        "ems_tiers_jpy": [
            {"max_g": 500,  "cost_jpy": 2800},
            {"max_g": 1000, "cost_jpy": 3800},
            {"max_g": 2000, "cost_jpy": 5400},
            {"max_g": 5000, "cost_jpy": 8000},
            {"max_g": 10000, "cost_jpy": 12000},
        ],
        "risky_shipping_ratio": 0.40,
        "default_weights_g": {
            "pokemon_raw":   5,
            "pokemon_slab":  70,
            "tech":          300,
            "fashion":       500,
            "general":       400,
        },
    }


def estimate_weight_g(category: str, title: str = "") -> float:
    """
    Estimate item weight in grams based on category and optional title hints.
    Falls back to config defaults.
    """
    cfg = _load_shipping_config()
    weights = cfg.get("default_weights_g", _default_shipping_config()["default_weights_g"])

    title_lower = title.lower()

    # Pokemon-specific: PSA slabs are heavier than raw cards
    if category == "pokemon":
        if any(kw in title_lower for kw in ("psa", "bgs", "cgc", "graded", "slab")):
            return float(weights.get("pokemon_slab", 70))
        return float(weights.get("pokemon_raw", 5))

    return float(weights.get(category, weights.get("general", 400)))


def ems_cost_jpy(weight_g: float) -> float:
    """Return the EMS Japan → Spain cost in JPY for the given weight."""
    cfg = _load_shipping_config()
    tiers = cfg.get("ems_tiers_jpy", _default_shipping_config()["ems_tiers_jpy"])

    for tier in sorted(tiers, key=lambda t: t["max_g"]):
        if weight_g <= tier["max_g"]:
            return float(tier["cost_jpy"])

    # Heavier than all tiers — use the heaviest tier as minimum and warn
    max_tier = max(tiers, key=lambda t: t["max_g"])
    logger.warning(
        "Item weight %.0fg exceeds all EMS tiers (max %.0fg); using max tier",
        weight_g, max_tier["max_g"],
    )
    return float(max_tier["cost_jpy"])


def total_shipping_jpy(weight_g: float) -> float:
    """
    Total Japan → Spain shipping cost in JPY.
    = ZenMarket service fee + domestic Japan shipping + EMS international
    """
    cfg = _load_shipping_config()
    service_fee = cfg.get("zenmarket_service_fee_jpy", 500)
    domestic = cfg.get("domestic_japan_shipping_jpy", 900)
    ems = ems_cost_jpy(weight_g)
    total = service_fee + domestic + ems
    logger.debug(
        "Shipping estimate: service=¥%d + domestic=¥%d + EMS=¥%d = ¥%d (%.0fg)",
        service_fee, domestic, ems, total, weight_g,
    )
    return float(total)


def estimate_shipping_eur(
    weight_g: float,
    jpy_to_eur_rate: float,
) -> float:
    """
    Return estimated total shipping cost in EUR.

    Args:
        weight_g: item weight in grams
        jpy_to_eur_rate: 1 JPY = X EUR (live rate from currency module)
    """
    jpy = total_shipping_jpy(weight_g)
    eur = round(jpy * jpy_to_eur_rate, 2)
    logger.debug("Shipping: ¥%.0f → €%.2f (rate=%.6f)", jpy, eur, jpy_to_eur_rate)
    return eur


def is_risky_shipping(shipping_eur: float, gross_margin_eur: float) -> bool:
    """
    Return True if shipping costs exceed the configured ratio of gross margin.
    Default: shipping > 40% of gross margin is flagged as risky.
    """
    if gross_margin_eur <= 0:
        return True
    cfg = _load_shipping_config()
    ratio = cfg.get("risky_shipping_ratio", 0.40)
    return (shipping_eur / gross_margin_eur) > ratio
