"""Orchestration ETL journalière Deribit."""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from pathlib import Path

from src.data.deribit.clean import clean_options, raw_to_dataframe, to_clean_schema
from src.data.deribit.client import DeribitAPIError, DeribitClient
from src.data.deribit.config import PATHS, POSTGRES, SCHEDULE
from src.data.deribit.schedule_status import write_last_run
from src.data.deribit.fetch import fetch_active_btc_options, load_raw_json, save_raw_json
from src.data.deribit.logging_setup import setup_logging

logger = logging.getLogger("deribit_pipeline")


class PipelineError(Exception):
    """Erreur bloquante dans la pipeline."""


def _should_skip_db(skip_db: bool) -> bool:
    if skip_db or SCHEDULE.skip_db:
        return True
    return not POSTGRES.is_configured


def run_daily_pipeline(
    snapshot: date | None = None,
    *,
    skip_fetch: bool = False,
    skip_db: bool = False,
    raw_path: Path | None = None,
    scheduled: bool = False,
) -> dict:
    """
    Exécute la pipeline complète pour une date (UTC).

    Étapes : fetch → raw JSON → clean → PostgreSQL
    """
    snapshot = snapshot or datetime.now(timezone.utc).date()
    setup_logging(PATHS.logs, snapshot)
    PATHS.raw.mkdir(parents=True, exist_ok=True)

    report: dict = {"snapshot": snapshot.isoformat(), "steps": {}}

    try:
        if skip_fetch and raw_path:
            payload = load_raw_json(raw_path)
            report["steps"]["fetch"] = "skipped (fichier existant)"
        elif skip_fetch:
            raw_file = PATHS.raw_file(snapshot)
            if not raw_file.exists():
                raise PipelineError(f"Fichier raw introuvable : {raw_file}")
            payload = load_raw_json(raw_file)
            report["steps"]["fetch"] = "skipped"
        else:
            client = DeribitClient()
            payload = fetch_active_btc_options(client)
            raw_file = save_raw_json(payload, snapshot)
            report["steps"]["fetch"] = str(raw_file)

        df = raw_to_dataframe(payload)
        df_clean, clean_stats = clean_options(df)
        snapshot_utc = _snapshot_datetime(payload)
        df_out = to_clean_schema(df_clean, snapshot_utc)

        report["clean_stats"] = clean_stats
        report["rows"] = len(df_out)

        skip_db_effective = _should_skip_db(skip_db)
        if skip_db_effective:
            report["steps"]["postgres"] = "skipped"
        else:
            from src.data.deribit.db import init_schema, insert_dataframe

            try:
                init_schema()
                inserted = insert_dataframe(df_out)
                report["steps"]["postgres"] = inserted
            except Exception as exc:
                if scheduled:
                    logger.error("PostgreSQL non disponible (exécution planifiée) : %s", exc)
                    report["steps"]["postgres"] = f"failed: {exc}"
                else:
                    raise

        write_last_run(report, success=True)
        logger.info("Pipeline terminée avec succès pour %s", snapshot)
        return report

    except DeribitAPIError as exc:
        logger.exception("Erreur API Deribit")
        write_last_run(report, success=False, error=str(exc))
        raise PipelineError(f"API Deribit : {exc}") from exc
    except Exception as exc:
        logger.exception("Échec pipeline")
        write_last_run(report, success=False, error=str(exc))
        raise PipelineError(str(exc)) from exc


def _snapshot_datetime(payload: dict) -> datetime:
    raw = payload.get("meta", {}).get("snapshot_utc")
    if raw:
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(timezone.utc)
