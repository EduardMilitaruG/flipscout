"""
bot_telegram.py — Full PTB v21 async Telegram bot for FlipScout.
Replaces bot.py. Uses inline keyboard menus with state stored in
context.user_data["action"] instead of ConversationHandler.
"""

import logging

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import db
from bot_core import build_alert_text, save_config
from pricer import ScoredListing

logger = logging.getLogger(__name__)


# ── Menu builders ──────────────────────────────────────────────────────────────

def _main_menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Keywords & Prices", callback_data="menu:keywords"),
            InlineKeyboardButton("⚙️ Settings", callback_data="menu:settings"),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data="menu:stats"),
            InlineKeyboardButton("❌ Close", callback_data="menu:close"),
        ],
    ])


def _main_menu_text() -> str:
    return "📦 *FlipScout Dashboard*"


def _keywords_menu_text() -> str:
    values = db.get_all_market_values()
    lines = ["*📋 Keywords & Market Values*", ""]
    if values:
        for row in values:
            lines.append(f"• `{row['keyword']}` — ~${row['estimated_usd']:.0f} USD")
    else:
        lines.append("_No keywords configured yet._")
    return "\n".join(lines)


def _keywords_menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Keyword", callback_data="kw:add"),
            InlineKeyboardButton("🗑 Remove", callback_data="kw:remove_list"),
        ],
        [
            InlineKeyboardButton("💰 Edit Price", callback_data="kw:edit_list"),
            InlineKeyboardButton("◀ Back", callback_data="menu:main"),
        ],
    ])


def _settings_menu_text(cfg: dict) -> str:
    return (
        "*⚙️ Settings*\n\n"
        f"💵 Max price: `${cfg.get('max_price_usd', '—')} USD`\n"
        f"📊 Deal threshold: `{cfg.get('deal_threshold_pct', '—')}%`\n"
        f"⏱ Check interval: `{cfg.get('check_interval_minutes', '—')} min`"
    )


def _settings_menu_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Max Price", callback_data="settings:max_price_usd")],
        [InlineKeyboardButton("📊 Deal Threshold %", callback_data="settings:deal_threshold_pct")],
        [InlineKeyboardButton("⏱ Check Interval", callback_data="settings:check_interval_minutes")],
        [InlineKeyboardButton("◀ Back", callback_data="menu:main")],
    ])


def _keyword_buttons(action_prefix: str) -> InlineKeyboardMarkup:
    values = db.get_all_market_values()
    rows = []
    for row in values:
        kw = row["keyword"]
        rows.append([InlineKeyboardButton(kw, callback_data=f"{action_prefix}:{kw}")])
    rows.append([InlineKeyboardButton("◀ Back", callback_data="menu:keywords")])
    return InlineKeyboardMarkup(rows)


# ── Command handlers ───────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 *FlipScout* is running\\.\n\n"
        "Use /manage to open the dashboard\\.",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def cmd_manage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.pop("action", None)
    await update.message.reply_text(
        _main_menu_text(),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=_main_menu_markup(),
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    stats = db.get_recent_stats(minutes=60)
    text = (
        f"📈 *Last 60 minutes*\n"
        f"Listings checked: {stats['checked']}\n"
        f"Alerts sent: {stats['alerted']}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


# ── Callback query handler ─────────────────────────────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    cfg: dict = context.bot_data.get("cfg", {})

    # ── Main menu navigation ──────────────────────────────────────────────────
    if data == "menu:main":
        context.user_data.pop("action", None)
        await query.edit_message_text(
            _main_menu_text(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_main_menu_markup(),
        )

    elif data == "menu:keywords":
        context.user_data.pop("action", None)
        await query.edit_message_text(
            _keywords_menu_text(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_keywords_menu_markup(),
        )

    elif data == "menu:settings":
        context.user_data.pop("action", None)
        await query.edit_message_text(
            _settings_menu_text(cfg),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_settings_menu_markup(),
        )

    elif data == "menu:stats":
        context.user_data.pop("action", None)
        stats = db.get_recent_stats(60)
        text = (
            f"📊 *Stats (last 60 min)*\n\n"
            f"Listings checked: `{stats['checked']}`\n"
            f"Alerts sent: `{stats['alerted']}`"
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀ Back", callback_data="menu:main")]
            ]),
        )

    elif data == "menu:close":
        context.user_data.pop("action", None)
        await query.delete_message()

    # ── Keyword actions ───────────────────────────────────────────────────────
    elif data == "kw:add":
        context.user_data["action"] = "kw:add:keyword"
        context.user_data["kw_message_id"] = query.message.message_id
        await query.edit_message_text(
            "✏️ Send me the keyword to add:",
            parse_mode=ParseMode.MARKDOWN,
        )

    elif data == "kw:remove_list":
        context.user_data.pop("action", None)
        await query.edit_message_text(
            "🗑 *Remove keyword* — tap to delete:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_keyword_buttons("kw:remove"),
        )

    elif data.startswith("kw:remove:"):
        keyword = data[len("kw:remove:"):]
        db.set_market_value.__module__  # ensure db is available
        # Remove from market_values table
        with db.get_connection() as conn:
            conn.execute("DELETE FROM market_values WHERE keyword = ?", (keyword,))
        # Remove from cfg keywords list
        keywords = cfg.get("keywords", [])
        cfg["keywords"] = [k for k in keywords if k.lower() != keyword.lower()]
        save_config(cfg)
        await query.edit_message_text(
            f"✅ Removed `{keyword}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◀ Back", callback_data="menu:keywords")]
            ]),
        )

    elif data == "kw:edit_list":
        context.user_data.pop("action", None)
        await query.edit_message_text(
            "💰 *Edit market price* — tap a keyword:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_keyword_buttons("kw:edit"),
        )

    elif data.startswith("kw:edit:"):
        keyword = data[len("kw:edit:"):]
        context.user_data["action"] = "kw:edit:price"
        context.user_data["pending_keyword"] = keyword
        context.user_data["kw_message_id"] = query.message.message_id
        await query.edit_message_text(
            f"💰 Send new market price (USD) for `{keyword}`:",
            parse_mode=ParseMode.MARKDOWN,
        )

    # ── Settings actions ──────────────────────────────────────────────────────
    elif data.startswith("settings:"):
        setting_key = data[len("settings:"):]
        context.user_data["action"] = f"settings:{setting_key}"
        context.user_data["kw_message_id"] = query.message.message_id
        labels = {
            "max_price_usd": "max price (USD)",
            "deal_threshold_pct": "deal threshold (%)",
            "check_interval_minutes": "check interval (minutes)",
        }
        label = labels.get(setting_key, setting_key)
        current = cfg.get(setting_key, "—")
        await query.edit_message_text(
            f"⚙️ Send new value for *{label}*\nCurrent: `{current}`",
            parse_mode=ParseMode.MARKDOWN,
        )


# ── Message handler (chat-reply state machine) ────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    action = context.user_data.get("action")
    if not action:
        return

    cfg: dict = context.bot_data.get("cfg", {})
    text = update.message.text.strip()

    # ── Add keyword flow ──────────────────────────────────────────────────────
    if action == "kw:add:keyword":
        context.user_data["pending_keyword"] = text.lower()
        context.user_data["action"] = "kw:add:price"
        await update.message.reply_text(
            f"💰 Now send the market price (USD) for `{text}`:",
            parse_mode=ParseMode.MARKDOWN,
        )

    elif action == "kw:add:price":
        keyword = context.user_data.pop("pending_keyword", None)
        context.user_data.pop("action", None)
        if not keyword:
            await update.message.reply_text("⚠️ Something went wrong. Use /manage to restart.")
            return
        try:
            price = float(text)
        except ValueError:
            await update.message.reply_text("⚠️ That's not a valid number. Use /manage to try again.")
            return

        db.set_market_value(keyword, price)
        keywords = cfg.get("keywords", [])
        if keyword not in [k.lower() for k in keywords]:
            cfg.setdefault("keywords", []).append(keyword)
        save_config(cfg)
        await update.message.reply_text(
            f"✅ Added `{keyword}` with market value `${price:.2f} USD`.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_main_menu_markup(),
        )

    # ── Edit price flow ───────────────────────────────────────────────────────
    elif action == "kw:edit:price":
        keyword = context.user_data.pop("pending_keyword", None)
        context.user_data.pop("action", None)
        if not keyword:
            await update.message.reply_text("⚠️ Something went wrong. Use /manage to restart.")
            return
        try:
            price = float(text)
        except ValueError:
            await update.message.reply_text("⚠️ That's not a valid number. Use /manage to try again.")
            return

        db.set_market_value(keyword, price)
        # update cfg market_values too
        cfg.setdefault("market_values", {})[keyword] = price
        save_config(cfg)
        await update.message.reply_text(
            f"✅ Updated `{keyword}` market value to `${price:.2f} USD`.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_main_menu_markup(),
        )

    # ── Settings flow ─────────────────────────────────────────────────────────
    elif action.startswith("settings:"):
        setting_key = action[len("settings:"):]
        context.user_data.pop("action", None)

        int_keys = {"check_interval_minutes", "max_pages"}
        try:
            value = int(text) if setting_key in int_keys else float(text)
        except ValueError:
            await update.message.reply_text("⚠️ That's not a valid number. Use /manage to try again.")
            return

        cfg[setting_key] = value
        save_config(cfg)
        await update.message.reply_text(
            f"✅ `{setting_key}` updated to `{value}`.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=_main_menu_markup(),
        )


# ── Alert sender (called from scheduler) ──────────────────────────────────────

async def send_deal_alert(bot: Bot, chat_id: str, scored: ScoredListing) -> bool:
    text = build_alert_text(scored)
    try:
        if scored.listing.thumbnail:
            try:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=scored.listing.thumbnail,
                    caption=text,
                    parse_mode=ParseMode.MARKDOWN,
                )
                return True
            except TelegramError as exc:
                logger.warning("Photo send failed (%s); falling back to text", exc)

        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
        return True
    except TelegramError as exc:
        logger.error("Failed to send Telegram alert: %s", exc)
        return False


# ── Application factory ────────────────────────────────────────────────────────

def build_application(token: str, cfg: dict) -> Application:
    app = Application.builder().token(token).build()
    app.bot_data["cfg"] = cfg

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("manage", cmd_manage))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app


def get_bot(token: str) -> Bot:
    return Bot(token=token)
