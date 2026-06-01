"""Nettoyage et validation des snapshots Deribit → DataFrame pandas."""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

from src.data.deribit.config import CLEAN

logger = logging.getLogger("deribit_pipeline.clean")

_INSTRUMENT_RE = re.compile(
    r"^(?P<currency>[A-Z]+)-(?P<expiry>\d{1,2}[A-Z]{3}\d{2})-(?P<strike>\d+(?:\.\d+)?)-(?P<type>[CP])$"
)


def _parse_instrument(name: str) -> dict[str, Any]:
    m = _INSTRUMENT_RE.match(name)
    if not m:
        return {"strike": np.nan, "option_type": None, "expiry_code": None}
    opt = "call" if m.group("type") == "C" else "put"
    return {
        "strike": float(m.group("strike")),
        "option_type": opt,
        "expiry_code": m.group("expiry"),
    }


def raw_to_dataframe(payload: dict[str, Any]) -> pd.DataFrame:
    """Convertit le JSON brut en DataFrame plat (une ligne par instrument)."""
    rows = payload.get("book_summary", [])
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    meta = payload.get("meta", {})
    snapshot_utc = pd.to_datetime(meta.get("snapshot_utc"), utc=True, errors="coerce")
    df["snapshot_utc"] = snapshot_utc

    parsed = df["instrument_name"].apply(_parse_instrument).apply(pd.Series)
    df = pd.concat([df, parsed], axis=1)

    df["maturity_date"] = pd.to_datetime(df["expiry_code"], format="%d%b%y", errors="coerce", utc=True)
    df["time_to_expiry_years"] = (
        (df["maturity_date"] - df["snapshot_utc"]).dt.total_seconds() / (365.25 * 24 * 3600)
    )

    if "mark_iv" in df.columns:
        df["mark_iv"] = pd.to_numeric(df["mark_iv"], errors="coerce") / 100.0

    for col in ("bid_price", "ask_price", "mark_price", "underlying_price", "open_interest", "volume"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def clean_options(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Applique les règles de qualité données.

    Returns:
        (df_clean, stats) avec compteurs de lignes supprimées par règle.
    """
    stats: dict[str, int] = {"initial": len(df)}
    if df.empty:
        return df, stats

    out = df.copy()

    required = ["instrument_name", "strike", "underlying_price", "mark_iv", "maturity_date"]
    before = len(out)
    out = out.dropna(subset=[c for c in required if c in out.columns])
    stats["dropped_nan_required"] = before - len(out)

    before = len(out)
    out = out[out["time_to_expiry_years"] > CLEAN.min_time_to_expiry_days / 365.25]
    stats["dropped_expired_or_near"] = before - len(out)

    if "open_interest" in out.columns:
        before = len(out)
        out = out[out["open_interest"].fillna(0) >= CLEAN.min_open_interest]
        stats["dropped_illiquid_oi"] = before - len(out)

    if "volume" in out.columns and CLEAN.min_volume_24h > 0:
        before = len(out)
        out = out[out["volume"].fillna(0) >= CLEAN.min_volume_24h]
        stats["dropped_illiquid_volume"] = before - len(out)

    before = len(out)
    has_bid = out["bid_price"].notna() if "bid_price" in out.columns else pd.Series(False, index=out.index)
    has_ask = out["ask_price"].notna() if "ask_price" in out.columns else pd.Series(False, index=out.index)
    both = has_bid & has_ask
    invalid_spread = both & (out["bid_price"] > out["ask_price"])
    out = out[~invalid_spread]
    stats["dropped_bid_ask_incoherent"] = before - len(out)

    if "mid_price" in out.columns:
        before = len(out)
        rel_spread = (out["ask_price"] - out["bid_price"]) / out["mid_price"].replace(0, np.nan)
        wide = both & (rel_spread > CLEAN.max_relative_spread)
        out = out[~wide.fillna(False)]
        stats["dropped_wide_spread"] = before - len(out)

    before = len(out)
    out = out[out["mark_iv"].between(CLEAN.iv_min, CLEAN.iv_max, inclusive="both")]
    stats["dropped_iv_aberrant"] = before - len(out)

    stats["final"] = len(out)
    logger.info("Nettoyage terminé : %s", stats)
    return out, stats


def to_clean_schema(df: pd.DataFrame, snapshot: datetime | None = None) -> pd.DataFrame:
    """Colonnes normalisées pour PostgreSQL."""
    snap = snapshot or datetime.now(timezone.utc)
    snapshot_date = snap.date() if hasattr(snap, "date") else pd.Timestamp(snap).date()

    columns = [
        "snapshot_date",
        "snapshot_utc",
        "instrument_name",
        "expiry_code",
        "maturity_date",
        "strike",
        "option_type",
        "underlying_price",
        "bid_price",
        "ask_price",
        "mid_price",
        "mark_price",
        "mark_iv",
        "open_interest",
        "volume_24h",
        "time_to_expiry_years",
        "creation_timestamp",
    ]

    out = df.copy()
    out["snapshot_date"] = snapshot_date
    if "snapshot_utc" not in out.columns:
        out["snapshot_utc"] = snap
    if "volume" in out.columns and "volume_24h" not in out.columns:
        out["volume_24h"] = out["volume"]

    available = [c for c in columns if c in out.columns]
    return out[available].sort_values(["maturity_date", "strike", "option_type"]).reset_index(drop=True)
