# FlipScout

**Japanese arbitrage profit calculator.** Monitors Yahoo Auctions Japan and Mercari JP for underpriced tech, Pokemon cards, and fashion — calculates real EUR margins including shipping and platform fees — and snipers Wallapop/Vinted for matching resale listings.

**Live demo:** https://dashboard-two-pearl-54.vercel.app   
**User:** admin123  
**Password:** admin123

---

## What it does

1. **Scans** Japanese marketplaces for items in configured categories (tech, Pokemon, fashion)
2. **Calculates** profit margin: `JP buy price + EMS shipping + platform fee` vs `Spanish resale median`
3. **Ranks** deals by gross margin % and surfaces the best opportunities in the dashboard
4. **Snipers** Wallapop and Vinted for listings below target prices, auto-messages sellers on match

---

## Dashboard

React 19 + Vite + Tailwind CSS frontend with a FastAPI backend.

| Page | Features |
|---|---|
| Deals | Live deal feed, filter by category/marketplace/margin/confidence, expandable cost breakdown |
| Sniper | Manage snipe targets, pause/resume engine, event audit log |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, Uvicorn, SQLite (WAL mode) |
| Scraping | `curl_cffi` Chrome TLS impersonation (Cloudflare bypass) |
| Margin engine | EMS weight-tier shipping estimator, per-category fee logic |
| Sniper | Async Wallapop + Vinted polling, kill switch, daily spend limit |
| Deployment | Vercel (frontend) + Railway (API) |
| Tests | Playwright E2E — 48 tests, 100% pass rate |

---

## Architecture

```
dashboard/          ← React frontend (this repo)
api/                ← FastAPI REST server (private)
scrapers/           ← Yahoo Auctions JP + Mercari JP (private)
sniper/             ← Wallapop + Vinted sniper engine (private)
margin.py           ← Profit calculation engine (private)
db.py               ← SQLite schema + queries (private)
```

The scraping and sniper logic lives in a private repository. This repo contains the dashboard and API schema.

---

## License

Copyright © 2026 Eduard Militaru. All rights reserved. See [LICENSE](LICENSE).
