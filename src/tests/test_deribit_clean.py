"""Tests unitaires des règles de nettoyage Deribit."""

import pandas as pd

from src.data.deribit.clean import _parse_instrument, clean_options


def test_parse_instrument_call():
    parsed = _parse_instrument("BTC-28MAR25-100000-C")
    assert parsed["strike"] == 100000.0
    assert parsed["option_type"] == "call"
    assert parsed["expiry_code"] == "28MAR25"


def test_clean_drops_incoherent_bid_ask():
    df = pd.DataFrame(
        {
            "instrument_name": ["BTC-28MAR25-90000-C"],
            "strike": [90000.0],
            "underlying_price": [90000.0],
            "mark_iv": [0.5],
            "maturity_date": [pd.Timestamp("2025-03-28", tz="UTC")],
            "time_to_expiry_years": [0.1],
            "open_interest": [1.0],
            "bid_price": [0.05],
            "ask_price": [0.04],
            "mid_price": [0.045],
            "volume": [10.0],
        }
    )
    clean, stats = clean_options(df)
    assert len(clean) == 0
    assert stats["dropped_bid_ask_incoherent"] == 1
