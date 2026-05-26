"""Configuration du logging structuré pour la pipeline."""

from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path


def setup_logging(log_dir: Path, snapshot: date | None = None, level: int = logging.INFO) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("deribit_pipeline")
    logger.setLevel(level)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    suffix = snapshot.isoformat() if snapshot else "general"
    file_handler = logging.FileHandler(log_dir / f"pipeline_{suffix}.log", encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger
