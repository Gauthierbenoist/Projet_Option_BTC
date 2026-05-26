"""État de la dernière exécution planifiée (monitoring local)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.data.deribit.config import PATHS

LAST_RUN_FILE = PATHS.logs / "last_run.json"


def write_last_run(report: dict[str, Any], *, success: bool, error: str | None = None) -> Path:
    PATHS.logs.mkdir(parents=True, exist_ok=True)
    payload = {
        "success": success,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "error": error,
        "report": report,
    }
    tmp = LAST_RUN_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    tmp.replace(LAST_RUN_FILE)
    return LAST_RUN_FILE
