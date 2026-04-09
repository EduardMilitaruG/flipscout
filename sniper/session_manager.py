"""
sniper/session_manager.py — Auth session management for Wallapop and Vinted.

Stores session tokens in environment variables (never in code or git).
Runs health checks on startup and every 6 hours.
Sends alerts via Discord/Telegram if session expires.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

from curl_cffi import requests as cffi_requests

logger = logging.getLogger(__name__)

_HEALTH_CHECK_INTERVAL = 6 * 3600   # 6 hours in seconds


@dataclass
class SessionHealth:
    platform: str
    is_valid: bool
    checked_at: float
    error: Optional[str] = None


class SessionManager:
    """
    Manages authenticated sessions for Wallapop and Vinted.
    Sessions are loaded from environment variables and validated periodically.
    """

    def __init__(self) -> None:
        self._last_check: dict[str, float] = {}
        self._health: dict[str, SessionHealth] = {}

    # ── Wallapop ───────────────────────────────────────────────────────────────

    def get_wallapop_token(self) -> Optional[str]:
        return os.environ.get("WALLAPOP_AUTH_TOKEN")

    def get_wallapop_headers(self) -> dict:
        token = self.get_wallapop_token()
        headers = {
            "Accept": "application/json",
            "Accept-Language": "es-ES,es;q=0.9",
            "Origin": "https://es.wallapop.com",
            "Referer": "https://es.wallapop.com/",
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
            ),
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def check_wallapop_session(self) -> SessionHealth:
        """Validate Wallapop auth token by hitting the profile endpoint."""
        token = self.get_wallapop_token()
        if not token:
            health = SessionHealth("wallapop", False, time.time(), "No WALLAPOP_AUTH_TOKEN in env")
            self._health["wallapop"] = health
            return health

        try:
            resp = cffi_requests.get(
                "https://api.wallapop.com/api/v3/users/me",
                headers=self.get_wallapop_headers(),
                impersonate="chrome120",
                timeout=10,
            )
            is_valid = resp.status_code == 200
            error = None if is_valid else f"HTTP {resp.status_code}"
        except Exception as exc:
            is_valid = False
            error = str(exc)

        health = SessionHealth("wallapop", is_valid, time.time(), error)
        self._health["wallapop"] = health
        self._last_check["wallapop"] = time.time()

        if not is_valid:
            logger.warning("Wallapop session invalid: %s", error)
        else:
            logger.info("Wallapop session OK")
        return health

    # ── Vinted ─────────────────────────────────────────────────────────────────

    def get_vinted_cookie(self) -> Optional[str]:
        return os.environ.get("VINTED_SESSION_COOKIE")

    def get_vinted_headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Accept-Language": "es-ES,es;q=0.9",
            "Origin": "https://www.vinted.es",
            "Referer": "https://www.vinted.es/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
        }

    def get_vinted_cookies(self) -> dict:
        cookie = self.get_vinted_cookie()
        return {"_vinted_fr_session": cookie} if cookie else {}

    def check_vinted_session(self) -> SessionHealth:
        """Validate Vinted session by hitting the users/me endpoint."""
        cookie = self.get_vinted_cookie()
        if not cookie:
            health = SessionHealth("vinted", False, time.time(), "No VINTED_SESSION_COOKIE in env")
            self._health["vinted"] = health
            return health

        try:
            resp = cffi_requests.get(
                "https://www.vinted.es/api/v2/users/me",
                headers=self.get_vinted_headers(),
                cookies=self.get_vinted_cookies(),
                impersonate="chrome120",
                timeout=10,
            )
            is_valid = resp.status_code == 200
            error = None if is_valid else f"HTTP {resp.status_code}"
        except Exception as exc:
            is_valid = False
            error = str(exc)

        health = SessionHealth("vinted", is_valid, time.time(), error)
        self._health["vinted"] = health
        self._last_check["vinted"] = time.time()

        if not is_valid:
            logger.warning("Vinted session invalid: %s", error)
        else:
            logger.info("Vinted session OK")
        return health

    # ── Health check scheduler ─────────────────────────────────────────────────

    def run_health_checks(self) -> list[SessionHealth]:
        """Run health checks for all configured platforms. Returns results."""
        results = []
        for platform, check_fn in [
            ("wallapop", self.check_wallapop_session),
            ("vinted", self.check_vinted_session),
        ]:
            last = self._last_check.get(platform, 0)
            if time.time() - last > _HEALTH_CHECK_INTERVAL:
                results.append(check_fn())
        return results

    def needs_reauth(self, platform: str) -> bool:
        health = self._health.get(platform)
        return health is not None and not health.is_valid

    def get_health_summary(self) -> dict:
        return {
            platform: {
                "valid": h.is_valid,
                "checked_at": h.checked_at,
                "error": h.error,
            }
            for platform, h in self._health.items()
        }


# Global singleton
session_manager = SessionManager()
