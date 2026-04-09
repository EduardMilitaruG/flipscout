"""
scrapers/mercari_jp.py — Mercari Japan scraper for FlipScout.

Mercari Japan has a high volume of Pokemon cards and tech listings.
Uses Mercari's unofficial search API with Chrome TLS impersonation.
"""

from __future__ import annotations

import logging
import random
import time
from typing import Optional

from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup

from scrapers.base import BaseMarketplace, Listing

logger = logging.getLogger(__name__)

_SEARCH_URL = "https://jp.mercari.com/search"
_API_URL = "https://api.mercari.jp/v2/entities:search"

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
]

# Mercari condition codes → standard scale
_CONDITION_MAP = {
    "1": "mint",      # 新品、未使用
    "2": "good",      # 未使用に近い
    "3": "good",      # 目立った傷や汚れなし
    "4": "fair",      # やや傷や汚れあり
    "5": "fair",      # 傷や汚れあり
    "6": "junk",      # 全体的に状態が悪い
}


def _polite_sleep(lo: float = 2.0, hi: float = 5.0) -> None:
    time.sleep(random.uniform(lo, hi))


class MercariJPScraper(BaseMarketplace):
    """
    Scraper for Mercari Japan marketplace.
    Uses Mercari's internal search API with Chrome fingerprint.
    """

    name = "mercari_jp"
    rate_limit_ms = 3000

    def __init__(self) -> None:
        self._session = cffi_requests.Session()
        self._warmed_up = False

    def _warm_up(self) -> None:
        """Visit Mercari homepage to establish a valid session."""
        if self._warmed_up:
            return
        try:
            _polite_sleep(1.0, 2.0)
            self._session.get(
                "https://jp.mercari.com/",
                headers={"User-Agent": random.choice(_USER_AGENTS)},
                impersonate="chrome120",
                timeout=15,
            )
            self._warmed_up = True
            logger.debug("Mercari JP session warmed up")
        except Exception as exc:
            logger.warning("Mercari warmup failed: %s", exc)

    def search(
        self,
        query: str,
        category: str = "general",
        max_price_usd: float = 999,
        max_pages: int = 1,
    ) -> list[Listing]:
        """
        Search Mercari Japan for listings matching query.
        max_price_usd is used as a soft filter post-fetch (JPY conversion applied).
        """
        from margin import jpy_to_usd  # avoid circular import at module level

        self._warm_up()

        payload = {
            "searchSessionId": "",
            "indexRouting": "INDEX_ROUTING_UNSPECIFIED",
            "thumbnailTypes": [],
            "searchCondition": {
                "keyword": query,
                "excludeKeyword": "",
                "sort": "SORT_SCORE",
                "order": "ORDER_DESC",
                "status": ["STATUS_ON_SALE"],
                "categoryId": [],
            },
            "defaultDatasets": [],
            "serviceFrom": "suruga",
            "withItemBrand": True,
            "withItemSize": False,
            "withItemPromotions": False,
            "withItemGroups": False,
            "useDynamicAttribute": False,
            "pageSize": 30,
        }

        headers = {
            "User-Agent": random.choice(_USER_AGENTS),
            "Accept": "application/json",
            "Accept-Language": "ja,en;q=0.9",
            "Origin": "https://jp.mercari.com",
            "Referer": f"https://jp.mercari.com/search?keyword={query}",
            "X-Platform": "web",
        }

        results: list[Listing] = []

        for page in range(max_pages):
            if page > 0:
                _polite_sleep()

            try:
                resp = self._session.post(
                    _API_URL,
                    json=payload,
                    headers=headers,
                    impersonate="chrome120",
                    timeout=20,
                )

                if resp.status_code == 429:
                    logger.warning("Mercari JP: rate limited, backing off 60s")
                    time.sleep(60)
                    break

                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                logger.warning("Mercari JP search failed for '%s': %s", query, exc)
                break

            items = data.get("items", [])
            if not items:
                break

            for item in items:
                try:
                    price_jpy = float(item.get("price", 0))
                    if price_jpy <= 0:
                        continue

                    price_usd = jpy_to_usd(price_jpy)
                    if price_usd > max_price_usd:
                        continue

                    item_id = item.get("id", "")
                    url = f"https://jp.mercari.com/item/{item_id}"
                    thumbnail = item.get("thumbnails", [None])[0]
                    condition_id = str(item.get("itemConditionId", ""))

                    results.append(Listing(
                        title=item.get("name", ""),
                        price_jpy=price_jpy,
                        price_usd=price_usd,
                        url=url,
                        keyword=query,
                        thumbnail=thumbnail,
                        category=category,
                        marketplace=self.name,
                        condition=_CONDITION_MAP.get(condition_id),
                    ))
                except (KeyError, TypeError, ValueError) as exc:
                    logger.debug("Skipping malformed Mercari item: %s", exc)
                    continue

            # Mercari API returns a pageToken for pagination
            next_token = data.get("meta", {}).get("nextPageToken")
            if not next_token:
                break
            payload["pageToken"] = next_token

        logger.info(
            "Mercari JP: found %d listings for '%s' across %d page(s)",
            len(results), query, page + 1,
        )
        return results
