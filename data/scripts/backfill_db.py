#!/usr/bin/env python
"""
Recharge PostgreSQL (Neon ou local) depuis les snapshots raw existants.

Usage:
    python data/scripts/backfill_db.py
    python data/scripts/backfill_db.py --date 2026-05-21
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.deribit.config import PATHS, POSTGRES  # noqa: E402
from src.data.deribit.db import init_schema  # noqa: E402
from src.data.deribit.pipeline import run_daily_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Backfill btc_options depuis data/raw/")
    p.add_argument("--date", action="append", help="Date YYYY-MM-DD (répétable)")
    return p.parse_args()


def discover_dates() -> list[date]:
    dates: list[date] = []
    for path in sorted(PATHS.raw.glob("*/*.json")):
        day = path.parent.name
        try:
            dates.append(date.fromisoformat(day))
        except ValueError:
            continue
    return sorted(set(dates))


def main() -> int:
    if not POSTGRES.is_configured:
        print("PostgreSQL non configuré (.env ou secrets GitHub).", file=sys.stderr)
        return 1

    args = parse_args()
    dates = [date.fromisoformat(d) for d in args.date] if args.date else discover_dates()
    if not dates:
        print("Aucun fichier raw trouvé dans data/raw/", file=sys.stderr)
        return 1

    init_schema()
    for snap in dates:
        print(f"Backfill {snap.isoformat()}...")
        report = run_daily_pipeline(snapshot=snap, skip_fetch=True, scheduled=True)
        print(f"  -> {report.get('rows')} lignes, postgres={report['steps'].get('postgres')}")

    print("Backfill terminé.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
