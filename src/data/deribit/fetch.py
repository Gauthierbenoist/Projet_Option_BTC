"""Téléchargement et sauvegarde des données brutes (JSON) par date."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from src.data.deribit.client import DeribitClient
from src.data.deribit.config import PATHS

logger = logging.getLogger("deribit_pipeline.fetch")


def fetch_active_btc_options(client: DeribitClient | None = None) -> dict[str, Any]:
    """
    Télécharge les options BTC actives + résumé de carnet.

    Retourne un envelope JSON versionné pour rejeu et audit.
    """
    client = client or DeribitClient()
    snapshot_ts = datetime.now(timezone.utc)

    logger.info("Récupération des instruments actifs…")
    instruments = client.get_active_option_instruments()
    instrument_names = {i["instrument_name"] for i in instruments}

    logger.info("Récupération du book summary…")
    book_summary = client.get_book_summary_options()
    active_summary = [row for row in book_summary if row.get("instrument_name") in instrument_names]

    logger.info(
        "Instruments actifs : %s | Lignes book summary filtrées : %s / %s",
        len(instrument_names),
        len(active_summary),
        len(book_summary),
    )

    return {
        "meta": {
            "source": "deribit",
            "currency": "BTC",
            "kind": "option",
            "snapshot_utc": snapshot_ts.isoformat(),
            "api_version": "v2",
            "record_count": len(active_summary),
        },
        "instruments": instruments,
        "book_summary": active_summary,
    }


def save_raw_json(payload: dict[str, Any], snapshot: date, path: Path | None = None) -> Path:
    """Sauvegarde atomique : écriture .tmp puis rename."""
    out = path or PATHS.raw_file(snapshot)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".json.tmp")

    with tmp.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    tmp.replace(out)
    logger.info("Données brutes sauvegardées : %s", out)
    return out


def load_raw_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)
