"""Export des données nettoyées en CSV."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import pandas as pd

from src.data.deribit.config import PATHS

logger = logging.getLogger("deribit_pipeline.export")


def export_clean_csv(df: pd.DataFrame, snapshot: date, path: Path | None = None) -> Path:
    out = path or PATHS.cleaned_csv(snapshot)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, float_format="%.8f")
    logger.info("CSV propre exporté : %s (%s lignes)", out, len(df))
    return out
