#!/usr/bin/env python
"""
Point d'entrée CLI pour la pipeline Deribit (cron / Airflow / exécution manuelle).

Usage:
    python data/scripts/run_daily_pipeline.py
    python data/scripts/run_daily_pipeline.py --date 2025-05-21
    python data/scripts/run_daily_pipeline.py --skip-db
    python data/scripts/run_daily_pipeline.py --skip-fetch --raw data/raw/2025-05-21/btc_options_2025-05-21.json
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.deribit.pipeline import PipelineError, run_daily_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Pipeline ETL Deribit BTC options")
    p.add_argument("--date", type=str, help="Date snapshot YYYY-MM-DD (défaut: aujourd'hui UTC)")
    p.add_argument("--skip-fetch", action="store_true", help="Relire le JSON raw existant")
    p.add_argument("--skip-db", action="store_true", help="Ne pas écrire en PostgreSQL (JSON raw seulement)")
    p.add_argument("--raw", type=str, help="Chemin JSON raw (avec --skip-fetch)")
    p.add_argument(
        "--scheduled",
        action="store_true",
        help="Mode planificateur : ne pas échouer si PostgreSQL est indisponible",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = date.fromisoformat(args.date) if args.date else None
    raw_path = Path(args.raw) if args.raw else None

    try:
        report = run_daily_pipeline(
            snapshot=snapshot,
            skip_fetch=args.skip_fetch,
            skip_db=args.skip_db,
            raw_path=raw_path,
            scheduled=args.scheduled,
        )
        print("Pipeline OK:", report)
        return 0
    except PipelineError as exc:
        print(f"Pipeline ERREUR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
