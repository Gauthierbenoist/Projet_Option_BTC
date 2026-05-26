"""Schéma PostgreSQL et insertion des données nettoyées."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from src.data.deribit.config import PATHS, POSTGRES

if TYPE_CHECKING:
    import psycopg2.extensions

logger = logging.getLogger("deribit_pipeline.db")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS btc_options (
    id BIGSERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    snapshot_utc TIMESTAMPTZ NOT NULL,
    instrument_name VARCHAR(64) NOT NULL,
    expiry_code VARCHAR(16),
    maturity_date TIMESTAMPTZ,
    strike DOUBLE PRECISION NOT NULL,
    option_type VARCHAR(8) NOT NULL,
    underlying_price DOUBLE PRECISION,
    bid_price DOUBLE PRECISION,
    ask_price DOUBLE PRECISION,
    mid_price DOUBLE PRECISION,
    mark_price DOUBLE PRECISION,
    mark_iv DOUBLE PRECISION,
    open_interest DOUBLE PRECISION,
    volume_24h DOUBLE PRECISION,
    time_to_expiry_years DOUBLE PRECISION,
    creation_timestamp BIGINT,
    inserted_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (snapshot_date, instrument_name)
);
CREATE INDEX IF NOT EXISTS idx_btc_options_snapshot_date ON btc_options (snapshot_date);
CREATE INDEX IF NOT EXISTS idx_btc_options_maturity ON btc_options (maturity_date);
CREATE INDEX IF NOT EXISTS idx_btc_options_strike_type ON btc_options (strike, option_type);
"""


def get_connection():
    import psycopg2

    return psycopg2.connect(POSTGRES.dsn)


def init_schema(conn: "psycopg2.extensions.connection | None" = None) -> None:
    """Crée la table btc_options (idempotent)."""
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
        conn.commit()
        logger.info("Schéma PostgreSQL initialisé (table btc_options)")
    finally:
        if own_conn:
            conn.close()


def init_schema_from_file(sql_path: Path | None = None) -> None:
    path = sql_path or (PATHS.scripts / "init_db.sql")
    if path.exists():
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(path.read_text(encoding="utf-8"))
            conn.commit()
            logger.info("Schéma appliqué depuis %s", path)
        finally:
            conn.close()
    else:
        init_schema()


def _prepare_rows(df: pd.DataFrame) -> list[tuple]:
    rows = []
    for _, r in df.iterrows():
        rows.append(
            (
                r.get("snapshot_date"),
                r.get("snapshot_utc"),
                r.get("instrument_name"),
                r.get("expiry_code"),
                r.get("maturity_date"),
                float(r.get("strike")),
                r.get("option_type"),
                r.get("underlying_price"),
                r.get("bid_price"),
                r.get("ask_price"),
                r.get("mid_price"),
                r.get("mark_price"),
                r.get("mark_iv"),
                r.get("open_interest"),
                r.get("volume_24h") if "volume_24h" in r.index else r.get("volume"),
                r.get("time_to_expiry_years"),
                r.get("creation_timestamp"),
            )
        )
    return rows


INSERT_SQL = """
INSERT INTO btc_options (
    snapshot_date, snapshot_utc, instrument_name, expiry_code, maturity_date,
    strike, option_type, underlying_price, bid_price, ask_price, mid_price,
    mark_price, mark_iv, open_interest, volume_24h, time_to_expiry_years,
    creation_timestamp
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (snapshot_date, instrument_name) DO UPDATE SET
    snapshot_utc = EXCLUDED.snapshot_utc,
    underlying_price = EXCLUDED.underlying_price,
    bid_price = EXCLUDED.bid_price,
    ask_price = EXCLUDED.ask_price,
    mid_price = EXCLUDED.mid_price,
    mark_price = EXCLUDED.mark_price,
    mark_iv = EXCLUDED.mark_iv,
    open_interest = EXCLUDED.open_interest,
    volume_24h = EXCLUDED.volume_24h,
    time_to_expiry_years = EXCLUDED.time_to_expiry_years,
    creation_timestamp = EXCLUDED.creation_timestamp,
    inserted_at = NOW();
"""


def insert_dataframe(df: pd.DataFrame, conn: "psycopg2.extensions.connection | None" = None) -> int:
    if df.empty:
        logger.warning("Aucune ligne à insérer en base")
        return 0

    own_conn = conn is None
    conn = conn or get_connection()
    rows = _prepare_rows(df)

    try:
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, rows)
        conn.commit()
        logger.info("%s lignes upsertées dans btc_options", len(rows))
        return len(rows)
    finally:
        if own_conn:
            conn.close()


def delete_snapshot(snapshot: date, conn: "psycopg2.extensions.connection | None" = None) -> int:
    """Supprime un snapshot (rechargement complet)."""
    own_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM btc_options WHERE snapshot_date = %s", (snapshot,))
            deleted = cur.rowcount
        conn.commit()
        return deleted
    finally:
        if own_conn:
            conn.close()
