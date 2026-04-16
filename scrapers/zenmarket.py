"""
scrapers/zenmarket.py — ZenMarket scraper for FlipScout.

ZenMarket aggregates Yahoo Auctions Japan in English.
Search URL pattern: https://zenmarket.jp/en/yahoo.aspx?q=KEYWORD
"""

import logging
import random
import re
import time
from typing import Optional
from urllib.parse import quote_plus, urljoin

from curl_cffi import requests
from bs4 import BeautifulSoup

from scrapers.base import BaseMarketplace, Listing

logger = logging.getLogger(__name__)

ZENMARKET_SEARCH = "https://zenmarket.jp/en/yahoo.aspx?q={query}"
EXCHANGE_API = "https://api.exchangerate-api.com/v4/latest/JPY"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

EXCLUDE_TERMS_DEFAULT = ["replica", "fake", "inspired", "bootleg", "copy"]


def _random_headers(referer: str = "https://zenmarket.jp/en/") -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": referer,
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


def _polite_sleep(min_s: float = 2.0, max_s: float = 5.0) -> None:
    delay = random.uniform(min_s, max_s)
    logger.debug("Sleeping %.1fs", delay)
    time.sleep(delay)


# ── Exchange rate ──────────────────────────────────────────────────────────────

_rate_cache: dict = {}


def get_jpy_to_usd_rate() -> float:
    """Fetch live JPY→USD exchange rate. Caches for the process lifetime."""
    if _rate_cache.get("rate"):
        return _rate_cache["rate"]

    try:
        resp = requests.get(EXCHANGE_API, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rate = data["rates"]["USD"]  # 1 JPY = X USD
        _rate_cache["rate"] = rate
        logger.debug("Exchange rate: 1 JPY = %.6f USD", rate)
        return rate
    except Exception as exc:
        logger.warning("Exchange rate fetch failed (%s); using fallback 0.0067", exc)
        return 0.0067  # conservative fallback (~149 JPY/USD)


def jpy_to_usd(jpy: float) -> float:
    return round(jpy * get_jpy_to_usd_rate(), 2)


# ── Parsing helpers ────────────────────────────────────────────────────────────

def _parse_price_jpy(text: str) -> Optional[float]:
    """Extract a numeric JPY price from a string like '¥12,500' or '12500'."""
    cleaned = re.sub(r"[^\d]", "", text)
    return float(cleaned) if cleaned else None


def _contains_excluded(title: str, exclude_terms: list[str]) -> bool:
    title_lower = title.lower()
    return any(term.lower() in title_lower for term in exclude_terms)


# ── ZenMarket scraper ──────────────────────────────────────────────────────────

def scrape_zenmarket(
    keyword: str,
    max_price_usd: float,
    exclude_terms: Optional[list[str]] = None,
    max_pages: int = 3,
) -> list[Listing]:
    """
    Scrape ZenMarket Yahoo Auctions search results for a keyword.
    Returns Listing objects that pass price and exclusion filters.
    """
    if exclude_terms is None:
        exclude_terms = EXCLUDE_TERMS_DEFAULT

    listings: list[Listing] = []
    session = requests.Session(impersonate="chrome120")

    # Warm up the session with a homepage visit to get cookies
    try:
        session.get("https://zenmarket.jp/en/", headers=_random_headers(), timeout=15)
        _polite_sleep(1.0, 2.5)
    except Exception:
        pass

    for page in range(1, max_pages + 1):
        url = ZENMARKET_SEARCH.format(query=quote_plus(keyword))
        if page > 1:
            url += f"&p={page}"

        logger.info("Scraping ZenMarket page %d for '%s'", page, keyword)

        try:
            resp = session.get(
                url,
                headers=_random_headers(referer="https://zenmarket.jp/en/"),
                timeout=20,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("Request failed for '%s' page %d: %s", keyword, page, exc)
            break

        page_listings = _parse_zenmarket_page(resp.text, keyword, max_price_usd, exclude_terms)
        listings.extend(page_listings)
        logger.debug("Page %d: found %d matching listings", page, len(page_listings))

        if page < max_pages:
            _polite_sleep()

    logger.info("'%s' total: %d listings after filters", keyword, len(listings))
    return listings


def _parse_zenmarket_page(
    html: str,
    keyword: str,
    max_price_usd: float,
    exclude_terms: list[str],
) -> list[Listing]:
    soup = BeautifulSoup(html, "lxml")
    results: list[Listing] = []

    cards = soup.select("div.yahoo-search-result")
    if not cards:
        logger.warning("No listing cards found — ZenMarket markup may have changed")
        return results

    for card in cards:
        listing = _extract_listing_from_card(card, keyword, max_price_usd, exclude_terms)
        if listing:
            results.append(listing)

    return results


def _extract_listing_from_card(
    card,
    keyword: str,
    max_price_usd: float,
    exclude_terms: list[str],
) -> Optional[Listing]:
    try:
        # Title + URL: first a.auction-url in the translate div
        title_el = card.select_one("div.translate a.auction-url")
        if not title_el:
            return None
        title = title_el.get_text(strip=True)
        if not title:
            return None

        if _contains_excluded(title, exclude_terms):
            logger.debug("Excluded (term match): %s", title[:60])
            return None

        href = title_el.get("href", "")
        if not href:
            return None
        listing_url = href if href.startswith("http") else urljoin("https://zenmarket.jp/en/", href)

        # Price: span.amount has data-jpy and data-usd attributes
        amount_el = card.select_one("span.amount")
        if not amount_el:
            return None

        jpy_raw = amount_el.get("data-jpy", "")
        usd_raw = amount_el.get("data-usd", "")

        price_jpy = _parse_price_jpy(jpy_raw)
        if price_jpy is None or price_jpy <= 0:
            return None

        # Parse USD directly from attribute (format: "$1,234.56 USD")
        usd_clean = re.sub(r"[^\d.]", "", usd_raw.replace(",", ""))
        try:
            price_usd = float(usd_clean) if usd_clean else jpy_to_usd(price_jpy)
        except ValueError:
            price_usd = jpy_to_usd(price_jpy)

        if price_usd > max_price_usd:
            logger.debug("Filtered (price $%.2f > $%.2f): %s", price_usd, max_price_usd, title[:60])
            return None

        # Thumbnail
        img_el = card.select_one("div.img-wrap img")
        thumbnail = None
        if img_el:
            thumbnail = img_el.get("src") or img_el.get("data-src")
            if thumbnail and not thumbnail.startswith("http"):
                thumbnail = urljoin("https://zenmarket.jp", thumbnail)

        return Listing(
            title=title,
            price_jpy=price_jpy,
            price_usd=price_usd,
            url=listing_url,
            thumbnail=thumbnail,
            keyword=keyword,
        )

    except Exception as exc:
        logger.debug("Card parse error: %s", exc)
        return None


# ── Multi-keyword entry point ──────────────────────────────────────────────────

def run_scraper(
    keywords: list[str],
    max_price_usd: float,
    exclude_terms: Optional[list[str]] = None,
    max_pages: int = 2,
) -> list[Listing]:
    """
    Run the scraper for all keywords. Returns deduplicated Listing list
    (dedup by URL across keywords).
    """
    all_listings: list[Listing] = []
    seen_urls: set[str] = set()

    for keyword in keywords:
        try:
            results = scrape_zenmarket(
                keyword=keyword,
                max_price_usd=max_price_usd,
                exclude_terms=exclude_terms,
                max_pages=max_pages,
            )
            for listing in results:
                if listing.url not in seen_urls:
                    seen_urls.add(listing.url)
                    all_listings.append(listing)
        except Exception as exc:
            logger.error("Scraper error for keyword '%s': %s", keyword, exc)
        finally:
            _polite_sleep()  # always wait between keywords

    logger.info("Scraper complete. Total unique listings: %d", len(all_listings))
    return all_listings
