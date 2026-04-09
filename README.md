# FlipScout

A Python automation tool that monitors Japanese secondhand marketplaces for underpriced archive fashion and sends real-time alerts to **Telegram** and **Discord**.

Japanese platforms like Yahoo Auctions Japan list pieces from Undercover, Number (N)ine, Kapital, Yohji Yamamoto, Comme des Garçons and Issey Miyake at a fraction of Western resale prices. The problem is you'd have to refresh listings manually, around the clock, across multiple platforms, in Japanese. FlipScout does that for you.

---

## Features

- **Real-time scraping** of ZenMarket (Yahoo Auctions Japan proxy) with Cloudflare bypass via TLS fingerprint impersonation
- **Deal scoring engine** — flags listings that are X% below your estimated market value
- **Dual-platform alerts** — sends photo + price + deal score to Telegram and Discord simultaneously
- **Interactive bot UI** — manage keywords, prices and settings directly from Telegram (inline keyboards) or Discord (slash commands + modals), no config file editing needed
- **Deduplication** — SQLite database ensures you never get alerted for the same listing twice, even across restarts
- **Scheduler** — runs on a configurable interval (default 15 min) with graceful error handling so it never crashes
- **Live JPY→USD conversion** pulled from a free exchange rate API, with USD also read directly from ZenMarket's data attributes as a fallback

---

## Tech Stack

| Layer | Technology |
|---|---|
| Scraping | `curl_cffi` (Chrome TLS impersonation), `BeautifulSoup4` |
| Telegram bot | `python-telegram-bot` v21 (async, PTB) |
| Discord bot | `discord.py` v2 (slash commands, modals, button views) |
| Database | SQLite via `sqlite3` (WAL mode) |
| Scheduling | `schedule` + `asyncio` |
| Config | `PyYAML` + `python-dotenv` |
| Runtime | Python 3.11+ / `asyncio` |

---

## Architecture

```
main.py              ← Scheduler + entry point, runs all tasks concurrently
├── scraper.py       ← ZenMarket scraper (Cloudflare bypass, price extraction)
├── pricer.py        ← Deal scoring logic (% below market value)
├── bot_core.py      ← Shared alert formatting for both platforms
├── bot_telegram.py  ← Telegram bot (inline keyboards, reply-based input)
├── bot_discord.py   ← Discord bot (slash commands, modals, button views)
└── db.py            ← SQLite layer (listings, market values, dedup)
```

Both bots run as concurrent `asyncio` tasks alongside the scraper scheduler. The scraper uses a `curl_cffi` session that impersonates Chrome's TLS handshake to bypass Cloudflare protection, then parses listing cards using BeautifulSoup with targeted CSS selectors. Prices are read directly from `data-jpy` / `data-usd` HTML attributes on the price element — no currency conversion needed.

---

## Setup

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/flipscout
cd flipscout
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Get a Telegram bot token

1. Open Telegram → search **@BotFather** → send `/newbot`
2. Copy the token (format: `123456789:AAH...`)
3. Send any message to your new bot, then open:
   ```
   https://api.telegram.org/botTOKEN/getUpdates
   ```
4. Find `"chat":{"id":XXXXXXX}` — that's your chat ID

### 3. Get a Discord bot token

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications) → New Application → Bot
2. Copy the token from the Bot tab
3. Under OAuth2 → URL Generator, select scopes: `bot` + `applications.commands`
4. Bot permissions: `Send Messages`, `Embed Links`, `Attach Files`
5. Use the generated URL to invite the bot to your server
6. Right-click your alerts channel → Copy Channel ID (requires Developer Mode in Discord settings)

### 4. Configure secrets

```bash
cp .env.example .env
```

Edit `.env`:
```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
DISCORD_BOT_TOKEN=your_token
DISCORD_CHANNEL_ID=your_channel_id
```

### 5. Edit `config.yaml`

Adjust keywords, price ceiling and deal threshold to your taste. Defaults are pre-filled with 10 archive fashion search terms and conservative market value estimates.

### 6. Run

```bash
python3 main.py
```

The tool immediately runs the first scrape, starts both bots, then repeats on the configured interval.

---

## Bot Commands

### Telegram — `/manage`

Opens an inline keyboard dashboard inside a single message, edited in-place as you navigate:

```
📦 FlipScout Dashboard
[📋 Keywords & Prices]  [⚙️ Settings]
[📊 Stats]              [❌ Close]
```

All text input (adding keywords, changing prices, updating settings) is handled via chat reply — no commands to memorise.

### Discord — `/manage`

Opens an ephemeral (private) button menu. All text input uses native Discord **modals** (pop-up dialogs). Changes reflect immediately.

| Command | Description |
|---|---|
| `/manage` | Open the full dashboard |
| `/status` | Listings checked and alerts sent in the last 60 minutes |

---

## Configuration Reference

```yaml
keywords:
  - "undercover jacket"
  - "number nine denim"

max_price_usd: 350          # Ignore listings above this price
deal_threshold_pct: 30      # Alert if 30%+ below market value estimate
check_interval_minutes: 15

exclude_terms:              # Case-insensitive, disqualifies a listing
  - replica
  - fake

market_values:              # Your estimated fair market value per keyword
  "undercover jacket": 480
  "number nine denim": 390
```

Market values are seeded from this file on first run (existing DB entries are not overwritten). After that, update them via `/manage` in either bot — no restart needed.

---

## Project Structure

```
flipscout/
├── main.py
├── scraper.py
├── pricer.py
├── bot_core.py
├── bot_telegram.py
├── bot_discord.py
├── db.py
├── config.yaml
├── .env.example
├── requirements.txt
└── README.md
```

---

## Notes

- ZenMarket HTML structure can change. If scraping breaks, inspect the live page and update `_parse_zenmarket_page` in `scraper.py`
- Browsing ZenMarket is unauthenticated — no account needed
- Rate limiting: 2–5 second random delays between requests and between keywords
- All secrets are loaded from `.env` — never hardcoded

---

## License

MIT
