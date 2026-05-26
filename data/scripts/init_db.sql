-- Schéma PostgreSQL pour les snapshots d'options BTC Deribit
-- Exécution : psql -U postgres -d deribit_quant -f data/scripts/init_db.sql

CREATE TABLE IF NOT EXISTS btc_options (
    id BIGSERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    snapshot_utc TIMESTAMPTZ NOT NULL,
    instrument_name VARCHAR(64) NOT NULL,
    expiry_code VARCHAR(16),
    maturity_date TIMESTAMPTZ,
    strike DOUBLE PRECISION NOT NULL,
    option_type VARCHAR(8) NOT NULL CHECK (option_type IN ('call', 'put')),
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

COMMENT ON TABLE btc_options IS 'Snapshots journaliers des options BTC actives (Deribit)';
COMMENT ON COLUMN btc_options.mark_iv IS 'Volatilité implicite mark (décimal, ex: 0.65 = 65%)';
