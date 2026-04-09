"""
main.py — Scheduler and entry point for Archive Scout.

Loads config.yaml, initialises the database, seeds market values,
then runs the scrape→score→alert pipeline on a configurable interval.
Both the Telegram and Discord bots run concurrently alongside the scheduler.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import schedule
import yaml
from dotenv import load_dotenv
from telegram.ext import Application

import db
from bot_telegram import build_application as build_tg_app
from bot_telegram import get_bot as get_tg_bot
from bot_telegram import send_deal_alert as tg_send_alert
from bot_discord import build_client as build_discord_client
from bot_discord import send_deal_alert as discord_send_alert
from pricer import score_listings, seed_from_config
from scraper import run_scraper

# ── Logging setup ──────────────────────────────────────────────────────────────

def setup_logging() -> None:
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        datefmt=datefmt,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("scout.log", encoding="utf-8"),
        ],
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("schedule").setLevel(logging.WARNING)
    logging.getLogger("discord").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)

# ── Config loader ──────────────────────────────────────────────────────────────

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        logger.error("config.yaml not found at %s", CONFIG_PATH)
        sys.exit(1)

    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    load_dotenv()

    # Telegram credentials from env
    cfg.setdefault("telegram_bot_token", os.getenv("TELEGRAM_BOT_TOKEN", ""))
    cfg.setdefault("telegram_chat_id", os.getenv("TELEGRAM_CHAT_ID", ""))
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        cfg["telegram_bot_token"] = os.getenv("TELEGRAM_BOT_TOKEN")
    if os.getenv("TELEGRAM_CHAT_ID"):
        cfg["telegram_chat_id"] = os.getenv("TELEGRAM_CHAT_ID")

    # Discord credentials from env
    cfg.setdefault("discord_bot_token", os.getenv("DISCORD_BOT_TOKEN", ""))
    cfg.setdefault("discord_channel_id", os.getenv("DISCORD_CHANNEL_ID", ""))
    if os.getenv("DISCORD_BOT_TOKEN"):
        cfg["discord_bot_token"] = os.getenv("DISCORD_BOT_TOKEN")
    if os.getenv("DISCORD_CHANNEL_ID"):
        cfg["discord_channel_id"] = os.getenv("DISCORD_CHANNEL_ID")

    _validate_config(cfg)
    return cfg


def _validate_config(cfg: dict) -> None:
    required = ["keywords", "max_price_usd", "deal_threshold_pct",
                "telegram_bot_token", "telegram_chat_id"]
    for key in required:
        if not cfg.get(key):
            logger.error("Missing required config key: %s", key)
            sys.exit(1)

    if not isinstance(cfg["keywords"], list) or not cfg["keywords"]:
        logger.error("'keywords' must be a non-empty list")
        sys.exit(1)


# ── Core scrape-score-alert job ────────────────────────────────────────────────

async def run_job(cfg: dict, tg_bot, discord_bot) -> None:
    logger.info("=== Starting scrape job ===")

    listings = run_scraper(
        keywords=cfg["keywords"],
        max_price_usd=cfg["max_price_usd"],
        exclude_terms=cfg.get("exclude_terms", []),
        max_pages=cfg.get("max_pages", 2),
    )

    new_listings = []
    for listing in listings:
        if not db.listing_exists(listing.url):
            db.insert_listing(
                title=listing.title,
                price_jpy=listing.price_jpy,
                price_usd=listing.price_usd,
                url=listing.url,
                thumbnail=listing.thumbnail,
                keyword=listing.keyword,
            )
            new_listings.append(listing)
        else:
            logger.debug("Already seen: %s", listing.url)

    logger.info("New listings this run: %d / %d total scraped", len(new_listings), len(listings))

    if not new_listings:
        logger.info("No new listings — nothing to score")
        return

    deals, _ = score_listings(new_listings, deal_threshold_pct=cfg["deal_threshold_pct"])

    if not deals:
        logger.info("No deals found in new listings")
        return

    chat_id = cfg["telegram_chat_id"]

    for scored in deals:
        # Send via Telegram
        tg_ok = await tg_send_alert(tg_bot, chat_id, scored)
        if tg_ok:
            db.mark_alerted(scored.listing.url)
            logger.info("Telegram alert sent for: %s", scored.listing.title[:60])
        else:
            logger.warning("Telegram alert failed for: %s", scored.listing.title[:60])

        # Send via Discord (only if connected and configured)
        if discord_bot and discord_bot.is_ready() and discord_bot.alert_channel_id:
            await discord_send_alert(discord_bot, scored)

    logger.info("=== Scrape job complete. Deals found: %d ===", len(deals))


# ── Bot runners ────────────────────────────────────────────────────────────────

async def run_telegram_bot(app: Application) -> None:
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    logger.info("Telegram bot polling started")

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        logger.info("Telegram bot stopped")


async def run_discord_bot(discord_bot, token: str) -> None:
    if not token:
        logger.info("Discord bot token not set — Discord bot disabled")
        return
    try:
        await discord_bot.start(token)
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        logger.error("Discord bot error: %s", exc, exc_info=True)
    finally:
        if not discord_bot.is_closed():
            await discord_bot.close()
        logger.info("Discord bot stopped")


# ── Main entry point ───────────────────────────────────────────────────────────

async def async_main() -> None:
    setup_logging()
    cfg = load_config()

    logger.info("Archive Scout starting up")
    logger.info("Keywords: %s", cfg["keywords"])
    logger.info("Max price: $%s USD | Deal threshold: %s%%",
                cfg["max_price_usd"], cfg["deal_threshold_pct"])

    db.init_db()
    if cfg.get("market_values"):
        seed_from_config(cfg["market_values"])

    interval_minutes = cfg.get("check_interval_minutes", 15)

    # Build both bots
    tg_app = build_tg_app(cfg["telegram_bot_token"], cfg)
    tg_bot = get_tg_bot(cfg["telegram_bot_token"])

    discord_token = cfg.get("discord_bot_token", "")
    discord_bot = build_discord_client(cfg) if discord_token else None

    # Run first job immediately
    await run_job(cfg, tg_bot, discord_bot)

    # Schedule recurring jobs using a sync wrapper that posts into the running loop
    loop = asyncio.get_event_loop()

    def _schedule_job():
        asyncio.run_coroutine_threadsafe(run_job(cfg, tg_bot, discord_bot), loop)

    schedule.every(interval_minutes).minutes.do(_schedule_job)
    logger.info("Scheduler armed: every %d minutes", interval_minutes)

    # Concurrent tasks
    tg_task = asyncio.create_task(run_telegram_bot(tg_app))

    discord_task = None
    if discord_bot and discord_token:
        discord_task = asyncio.create_task(run_discord_bot(discord_bot, discord_token))

    try:
        while True:
            schedule.run_pending()
            await asyncio.sleep(10)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Shutdown requested")
    finally:
        tg_task.cancel()
        try:
            await tg_task
        except asyncio.CancelledError:
            pass

        if discord_task is not None:
            discord_task.cancel()
            try:
                await discord_task
            except asyncio.CancelledError:
                pass

        logger.info("Archive Scout stopped")


def main() -> None:
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
