from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import quant_engine.providers as providers
from quant_engine.scanner import NIFTY_50, parse_watchlist, scan, short_alignment

ROOT = Path(__file__).resolve().parents[1]


def fake_history(ticker, period):
    bars = pd.read_csv(ROOT / "data" / "synthetic_daily.csv", parse_dates=["date"]).set_index("date")
    if ticker.startswith("BAD"):
        raise RuntimeError("HTTP 404 Not Found")
    if ticker.startswith("UP"):  # make a distinct, rising series
        bars = bars.iloc[::-1].reset_index(drop=True).set_index(bars.index)
    bars.index = bars.index.tz_localize("Asia/Kolkata")
    return bars.rename(columns=str.title)


def test_watchlist_parsing_and_default_list():
    assert parse_watchlist("tcs, infy\nTCS  m&m;BAJAJ-AUTO") == ["TCS", "INFY", "M&M", "BAJAJ-AUTO"]
    assert len(NIFTY_50) == 50 == len(set(NIFTY_50)) and "BSE" in NIFTY_50 and "WIPRO" not in NIFTY_50
    for symbol in NIFTY_50:
        providers.provider_symbol(symbol, "NSE")  # every default symbol is accepted


def test_scan_rows_match_single_stock_analysis_and_isolate_failures():
    rows = scan(["AAA", "BAD", "UPX"], history=fake_history, workers=2)
    by = {r["Symbol"]: r for r in rows}
    assert by["BAD"]["Error"] and "AAA" in by and by["AAA"]["Error"] == ""
    from quant_engine.analysis import analyze
    from quant_engine.data import load_bars
    from quant_engine.market_read import market_read
    from quant_engine.models import Settings
    direct = market_read(analyze(load_bars((ROOT / "data" / "synthetic_daily.csv").read_bytes(), "s.csv"), Settings()))
    assert by["AAA"]["Market read"] == direct["verdict"] and by["AAA"]["Up votes"] == direct["bullish"]
    assert by["AAA"]["Market read"] != by["UPX"]["Market read"] or by["AAA"]["Close"] != by["UPX"]["Close"]


@pytest.mark.parametrize("higher,daily,label", [(1, 1, "Aligned up"), (-1, 1, "Counter-trend (larger down)"),
                                               (1, 0, "Pause in uptrend"), (0, 1, "No larger trend"), (None, 1, "n/a")])
def test_short_alignment(higher, daily, label):
    assert short_alignment(higher, daily) == label


def test_scanner_page_runs_and_opens_a_stock_in_analyze(monkeypatch):
    monkeypatch.setattr(providers, "_yahoo_history", fake_history)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run()
    app.radio(key="workspace_page").set_value("Scanner").run()
    assert not app.exception and app.title[0].value == "Scanner"
    app.segmented_control(key="scan_preset").set_value("Custom list").run()
    app.text_area(key="scan_text_Custom list").set_value("AAA, UPX, BAD").run()
    next(b for b in app.button if b.label == "Scan 3").click().run()
    assert not app.exception
    assert any("1 symbol(s) could not be analyzed" in e.label for e in app.expander)
    table = next(d for d in app.dataframe if "Market read" in d.value.columns)
    assert set(table.value["Symbol"]) == {"AAA", "UPX"}
    # "Open in Analyze" sets exactly these keys; the Analyze page must then load that ticker.
    import streamlit as st
    from quant_engine import scanner_ui
    captured = {}
    monkeypatch.setattr(scanner_ui.st, "session_state", captured)
    scanner_ui._open_in_analyze("UPX", "NSE")
    assert captured == {"workspace_page": "Analyze", "data_source": "Fetch by ticker", "ticker_symbol": "UPX", "ticker_exchange": "NSE"}
    monkeypatch.undo()
    monkeypatch.setattr(providers, "_yahoo_history", fake_history)
    for k, v in captured.items():
        app.session_state[k] = v
    app.run()
    assert not app.exception
    assert any('class="hdr"' in m.value and "UPX" in m.value for m in app.markdown)
