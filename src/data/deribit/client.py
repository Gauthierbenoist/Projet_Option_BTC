"""Client HTTP Deribit (REST public) avec retries et gestion d'erreurs."""

from __future__ import annotations

import json
import logging
import platform
import subprocess
import time
from typing import Any
from urllib.parse import urlencode

import requests

from src.data.deribit.config import DERIBIT

logger = logging.getLogger("deribit_pipeline.client")


class DeribitAPIError(Exception):
    """Erreur API Deribit (HTTP, JSON-RPC ou réseau)."""


class DeribitClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or DERIBIT.base_url).rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def _build_url(self, method: str, params: dict[str, Any] | None = None) -> str:
        query = urlencode(params or {})
        base = f"{self.base_url}/public/{method}"
        return f"{base}?{query}" if query else base

    def _request_curl(self, url: str) -> dict[str, Any]:
        """Fallback Windows : évite les conflits OpenSSL de certaines installs Python."""
        curl_args = ["curl.exe", "-sS", "--max-time", str(DERIBIT.request_timeout)]
        if platform.system() == "Windows":
            curl_args.append("--ssl-no-revoke")
        proc = subprocess.run(
            [*curl_args, url],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise DeribitAPIError(proc.stderr or f"curl exit {proc.returncode}")
        return json.loads(proc.stdout)

    def _request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        url = self._build_url(method, params)
        use_curl = platform.system() == "Windows"
        last_error: Exception | None = None

        for attempt in range(1, DERIBIT.max_retries + 1):
            try:
                if use_curl:
                    payload = self._request_curl(url)
                else:
                    resp = self._session.get(url, timeout=DERIBIT.request_timeout)
                    resp.raise_for_status()
                    payload = resp.json()
            except (requests.RequestException, ValueError, DeribitAPIError, json.JSONDecodeError, OSError) as exc:
                last_error = exc
                wait = DERIBIT.retry_backoff ** (attempt - 1)
                logger.warning(
                    "Tentative %s/%s échouée pour %s : %s",
                    attempt,
                    DERIBIT.max_retries,
                    method,
                    exc,
                )
                if attempt < DERIBIT.max_retries:
                    time.sleep(wait)
                continue

            if "error" in payload:
                raise DeribitAPIError(payload["error"])

            return payload.get("result", payload)

        raise DeribitAPIError(f"Échec après {DERIBIT.max_retries} tentatives : {last_error}") from last_error

    def get_active_option_instruments(self) -> list[dict[str, Any]]:
        """Liste des options BTC non expirées."""
        instruments = self._request(
            "get_instruments",
            {"currency": DERIBIT.currency, "kind": "option", "expired": "false"},
        )
        return [i for i in instruments if i.get("is_active", True)]

    def get_book_summary_options(self) -> list[dict[str, Any]]:
        """Résumé marché (bid/ask, IV, OI, volume) pour toutes les options BTC."""
        return self._request(
            "get_book_summary_by_currency",
            {"currency": DERIBIT.currency, "kind": "option"},
        )
