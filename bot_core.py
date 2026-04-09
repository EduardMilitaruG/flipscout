"""
bot_core.py — Shared formatting logic for Telegram and Discord bots (FlipScout).
Now includes enriched margin data in all alert formats.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import yaml

from pricer import ScoredListing, format_deal_score
from scrapers.base import MarginResult

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
    "categories",
}


def _escape_md(text: str) -> str:
    reserved = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in reserved else c for c in text)


def _margin_color(margin_pct: float) -> str:
    if margin_pct >= 30:
        return "🟢"
    if margin_pct >= 15:
        return "🟡"
    return "🔴"


# ── Alert builders — classic mode (no margin data) ─────────────────────────────

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
            {"name": "Price", "value": f"¥{listing.price_jpy:,.0f} / ${listing.price_usd:.2f}", "inline": True},
            {"name": "Market Value", "value": f"~${scored.market_value_usd:.0f}", "inline": True},
            {"name": "Deal Score", "value": deal_label, "inline": True},
            {"name": "Keyword", "value": listing.keyword, "inline": True},
            {"name": "Category", "value": listing.category.title(), "inline": True},
            {"name": "Source", "value": listing.marketplace.replace("_", " ").title(), "inline": True},
        ],
        "thumbnail": listing.thumbnail,
    }


# ── Alert builders — enriched mode (with margin data) ─────────────────────────

def build_margin_alert_text(margin: MarginResult) -> str:
    """Full profit margin alert for Telegram (MarkdownV2)."""
    listing = margin.listing
    color = _margin_color(margin.margin_pct)
    risky_tag = "  ⚠️ _risky shipping_" if margin.is_risky else ""
    confidence_map = {"high": "🔵", "medium": "🟡", "low": "⚪"}
    conf_icon = confidence_map.get(margin.confidence, "⚪")

    lines = [
        f"*{_escape_md(listing.title[:80])}*",
        "",
        f"💴 Buy \\(JP\\): *¥{listing.price_jpy:,.0f}* \\(€{margin.jp_price_eur:.2f}\\)",
        f"🚢 Shipping: €{margin.shipping_eur:.2f}",
        f"📦 Platform fee: €{margin.platform_fee_eur:.2f}",
        f"🏷 ES resale \\(median\\): *€{margin.spanish_resale_eur:.2f}*"
        f"  {conf_icon} {margin.comparable_count} listings",
        "",
        f"{color} *Gross profit: €{margin.gross_margin_eur:.2f} \\({margin.margin_pct:.1f}%\\)*{risky_tag}",
        "",
        f"📂 {listing.category.title()} · {listing.marketplace.replace('_', ' ').title()}",
        f"🔍 `{_escape_md(listing.keyword)}`",
        "",
        f"[View listing →]({listing.url})",
    ]
    return "\n".join(lines)


def build_margin_embed_data(margin: MarginResult) -> dict:
    """Full profit margin embed for Discord."""
    listing = margin.listing
    risky_tag = " ⚠️ Risky" if margin.is_risky else ""

    if margin.margin_pct >= 30:
        color = 0x57F287   # green
    elif margin.margin_pct >= 15:
        color = 0xFEE75C   # yellow
    else:
        color = 0xED4245   # red

    return {
        "title": listing.title[:256],
        "url": listing.url,
        "color": color,
        "fields": [
            {
                "name": "🛒 Buy (Japan)",
                "value": f"¥{listing.price_jpy:,.0f}\n€{margin.jp_price_eur:.2f}",
                "inline": True,
            },
            {
                "name": "🚢 Total costs",
                "value": f"Ship: €{margin.shipping_eur:.2f}\nFee: €{margin.platform_fee_eur:.2f}",
                "inline": True,
            },
            {
                "name": "🏷️ ES Resale",
                "value": f"€{margin.spanish_resale_eur:.2f}\n({margin.comparable_count} comps, {margin.confidence})",
                "inline": True,
            },
            {
                "name": f"💰 Profit{risky_tag}",
                "value": f"**€{margin.gross_margin_eur:.2f}** ({margin.margin_pct:.1f}%)",
                "inline": True,
            },
            {
                "name": "📂 Category",
                "value": listing.category.title(),
                "inline": True,
            },
            {
                "name": "🔍 Keyword",
                "value": listing.keyword,
                "inline": True,
            },
        ],
        "thumbnail": listing.thumbnail,
    }


# ── Sniper alert ───────────────────────────────────────────────────────────────

def build_sniper_alert_text(
    target: dict,
    listing,        # SpanishListing
    action: str,
    margin_pct: Optional[float],
) -> str:
    """Telegram alert for a sniper match."""
    action_icons = {
        "messaged": "💬",
        "auto_bought": "🛍️",
        "alert_only": "🔔",
    }
    icon = action_icons.get(action, "🔔")
    margin_str = f"{margin_pct:.1f}%" if margin_pct is not None else "unknown"

    lines = [
        f"{icon} *SNIPER MATCH*",
        "",
        f"*{_escape_md(listing.title[:80])}*",
        f"💶 *€{listing.price_eur:.2f}*  ·  {listing.platform.title()}",
        f"📍 {listing.location or 'España'}",
        f"📊 Est\\. margin: *{_escape_md(margin_str)}*",
        f"🎯 Target: `{_escape_md(target['query'])}`",
        f"⚡ Action: {action.replace('_', ' ').title()}",
        "",
        f"[View listing →]({listing.url})",
    ]
    return "\n".join(lines)


# ── Config persistence ─────────────────────────────────────────────────────────

def save_config(cfg: dict) -> None:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        existing = yaml.safe_load(f) or {}

    for key in SAFE_KEYS:
        if key in cfg:
            existing[key] = cfg[key]

    for secret in ("telegram_bot_token", "telegram_chat_id",
                   "discord_bot_token", "discord_channel_id"):
        existing.pop(secret, None)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(existing, f, allow_unicode=True, sort_keys=False)

    logger.info("Config saved to %s", CONFIG_PATH)
