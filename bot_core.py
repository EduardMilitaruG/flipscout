"""
bot_core.py — Shared formatting logic for Telegram and Discord bots.
"""

import logging
from pathlib import Path

import yaml

from pricer import ScoredListing, format_deal_score

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "config.yaml"

SAFE_KEYS = {
    "keywords",
    "max_price_usd",
    "deal_threshold_pct",
    "check_interval_minutes",
    "max_pages",
    "exclude_terms",
    "market_values",
}


def _escape_md(text: str) -> str:
    reserved = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in reserved else c for c in text)


def build_alert_text(scored: ScoredListing) -> str:
    listing = scored.listing
    deal_label = format_deal_score(scored.discount_pct)

    lines = [
        f"*{_escape_md(listing.title)}*",
        "",
        f"💴 *{listing.price_jpy:,.0f} JPY*  ·  *${listing.price_usd:.2f} USD*",
        f"📊 Market value: ~${scored.market_value_usd:.0f} USD",
        f"🏷 Deal score: {deal_label}",
        f"🔍 Keyword: `{_escape_md(listing.keyword)}`",
        "",
        f"[View listing →]({listing.url})",
    ]
    return "\n".join(lines)


def build_alert_embed_data(scored: ScoredListing) -> dict:
    listing = scored.listing
    deal_label = format_deal_score(scored.discount_pct)
    color = 0xFEE75C if scored.discount_pct >= 40 else 0x5865F2

    return {
        "title": listing.title,
        "url": listing.url,
        "color": color,
        "fields": [
            {
                "name": "Price",
                "value": f"¥{listing.price_jpy:,.0f} / ${listing.price_usd:.2f} USD",
                "inline": True,
            },
            {
                "name": "Market Value",
                "value": f"~${scored.market_value_usd:.0f} USD",
                "inline": True,
            },
            {
                "name": "Deal Score",
                "value": deal_label,
                "inline": True,
            },
            {
                "name": "Keyword",
                "value": listing.keyword,
                "inline": True,
            },
        ],
        "thumbnail": listing.thumbnail,
    }


def save_config(cfg: dict) -> None:
    """Write safe keys from cfg back to config.yaml, preserving comments."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        existing = yaml.safe_load(f) or {}

    for key in SAFE_KEYS:
        if key in cfg:
            existing[key] = cfg[key]

    # Remove any secret keys that might have leaked in
    for secret in ("telegram_bot_token", "telegram_chat_id",
                   "discord_bot_token", "discord_channel_id"):
        existing.pop(secret, None)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(existing, f, allow_unicode=True, sort_keys=False)

    logger.info("Config saved to %s", CONFIG_PATH)
