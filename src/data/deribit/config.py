"""Configuration centralisée (chemins, seuils, PostgreSQL via variables d'environnement)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

# Racine projet = parent de src/
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Paths:
    raw: Path = DATA_DIR / "raw"
    cleaned: Path = DATA_DIR / "cleaned"
    scripts: Path = DATA_DIR / "scripts"
    logs: Path = DATA_DIR / "logs"

    def raw_file(self, snapshot: date) -> Path:
        return self.raw / snapshot.isoformat() / f"btc_options_{snapshot.isoformat()}.json"

    def cleaned_csv(self, snapshot: date) -> Path:
        return self.cleaned / f"btc_options_{snapshot.isoformat()}.csv"


@dataclass(frozen=True)
class DeribitConfig:
    base_url: str = os.getenv("DERIBIT_API_URL", "https://www.deribit.com/api/v2")
    currency: str = "BTC"
    request_timeout: int = int(os.getenv("DERIBIT_TIMEOUT", "30"))
    max_retries: int = int(os.getenv("DERIBIT_MAX_RETRIES", "3"))
    retry_backoff: float = float(os.getenv("DERIBIT_RETRY_BACKOFF", "1.5"))


@dataclass(frozen=True)
class CleanConfig:
    min_open_interest: float = float(os.getenv("CLEAN_MIN_OPEN_INTEREST", "0.01"))
    min_volume_24h: float = float(os.getenv("CLEAN_MIN_VOLUME_24H", "0"))
    max_relative_spread: float = float(os.getenv("CLEAN_MAX_REL_SPREAD", "0.5"))
    iv_min: float = float(os.getenv("CLEAN_IV_MIN", "0.01"))
    iv_max: float = float(os.getenv("CLEAN_IV_MAX", "5.0"))
    min_time_to_expiry_days: float = float(os.getenv("CLEAN_MIN_TTE_DAYS", "0"))


@dataclass(frozen=True)
class PostgresConfig:
    """Neon : préférer DATABASE_URL (avec ?sslmode=require) depuis le dashboard."""

    database_url: str = os.getenv("DATABASE_URL", "")
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    db: str = os.getenv("POSTGRES_DB", "deribit_quant")
    user: str = os.getenv("POSTGRES_USER", "postgres")
    password: str = os.getenv("POSTGRES_PASSWORD", "")
    sslmode: str = os.getenv("POSTGRES_SSLMODE", "prefer")
    schema: str = os.getenv("POSTGRES_SCHEMA", "public")

    @property
    def dsn(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.db} "
            f"user={self.user} password={self.password} sslmode={self.sslmode}"
        )

    @property
    def is_configured(self) -> bool:
        if self.database_url:
            return True
        return bool(self.password and self.password != "changeme")


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default).lower()).lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class ScheduleConfig:
    """Planification et comportement des exécutions automatiques."""

    skip_db: bool = _env_bool("PIPELINE_SKIP_DB")
    schedule_hour: int = int(os.getenv("PIPELINE_SCHEDULE_HOUR", "0"))
    schedule_minute: int = int(os.getenv("PIPELINE_SCHEDULE_MINUTE", "15"))
    task_name: str = os.getenv("PIPELINE_TASK_NAME", "DeribitBTCOptionsDaily")

    @property
    def schedule_time(self) -> str:
        return f"{self.schedule_hour:02d}:{self.schedule_minute:02d}"


PATHS = Paths()
DERIBIT = DeribitConfig()
CLEAN = CleanConfig()
POSTGRES = PostgresConfig()
SCHEDULE = ScheduleConfig()
