from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from quant_engine.data import load_bars
from quant_engine.providers import IST, fetch_daily, normalize_history, provider_symbol


def fake_history(rows=30, start="2026-10-01", tz="Asia/Kolkata", gaps=()):
    index = pd.bdate_range(start, periods=rows, tz=tz)
    close = np.linspace(100, 130, rows)
    frame = pd.DataFrame({"Open": close - 1, "High": close + 2, "Low": close - 2,
                          "Close": close, "Adj Close": close * .98, "Volume": np.arange(rows) * 1000 + 5000}, index=index)
    for i in gaps:
        frame.iloc[i, :4] = np.nan
    return frame


@pytest.mark.parametrize("typed,exchange,expected", [
    ("reliance", "NSE", "RELIANCE.NS"), (" tcs ", "BSE", "TCS.BO"), ("INFY.NS", "BSE", "INFY.NS"),
    ("^NSEI", "NSE", "^NSEI"), ("aapl", "As typed", "AAPL"), ("M&M", "NSE", None)])
def test_symbol_mapping(typed, exchange, expected):
    if expected is None:
        with pytest.raises(ValueError):
            provider_symbol(typed, exchange)
    else:
        assert provider_symbol(typed, exchange) == expected


def test_fetch_produces_validated_bars_and_drops_blank_rows():
    after_close = datetime(2026, 12, 31, 20, 0, tzinfo=IST)
    result = fetch_daily("reliance", "NSE", "1 year", history=lambda t, p: fake_history(gaps=(3,)), now=after_close)
    assert result.provider_symbol == "RELIANCE.NS" and result.display_symbol == "RELIANCE"
    assert result.rows == 29 and any("dropped, not filled" in n for n in result.notes)
    data = load_bars(result.csv_bytes, "RELIANCE.NS.csv")
    assert len(data.bars) == 29 and data.bars.index.tz is None
    assert list(data.bars.columns) == ["open", "high", "low", "close", "volume"]


def test_forming_session_excluded_before_cutoff_but_kept_after():
    raw = fake_history(rows=5, start="2026-11-09")  # Mon..Fri, last row 2026-11-13
    during = datetime(2026, 11, 13, 11, 0, tzinfo=IST)
    frame, notes = normalize_history(raw, during)
    assert frame.index[-1] == pd.Timestamp("2026-11-12") and "still forming" in notes[-1]
    frame, notes = normalize_history(raw, datetime(2026, 11, 13, 18, 30, tzinfo=IST))
    assert frame.index[-1] == pd.Timestamp("2026-11-13") and not notes


def test_provider_errors_are_explained():
    def boom(t, p):
        raise RuntimeError("HTTP 404")
    with pytest.raises(ValueError, match="Could not fetch XYZ.NS"):
        fetch_daily("xyz", history=boom)
    with pytest.raises(ValueError, match="no daily rows"):
        fetch_daily("xyz", history=lambda t, p: pd.DataFrame())


def test_rounding_only_ohlc_repair_is_tiny_and_disclosed():
    raw = fake_history(rows=5)
    raw.iloc[2, raw.columns.get_loc("High")] = raw.iloc[2]["Close"] * (1 - 1e-7)
    raw.iloc[2, raw.columns.get_loc("Open")] = raw.iloc[2]["Close"] - 1
    frame, notes = normalize_history(raw, datetime(2030, 1, 1, tzinfo=IST))
    assert frame.high.iloc[2] == pytest.approx(raw.iloc[2]["Close"]) and "rounding" in notes[0]
    # A real inconsistency is left for validation to reject.
    raw.iloc[3, raw.columns.get_loc("High")] = raw.iloc[3]["Close"] * 0.9
    frame, _ = normalize_history(raw, datetime(2030, 1, 1, tzinfo=IST))
    with pytest.raises(ValueError):
        load_bars(frame.reset_index().assign(date=lambda f: f.date.dt.strftime("%Y-%m-%d")).to_csv(index=False).encode(), "x.csv")


def _fake_yahoo(ticker, period):
    from pathlib import Path
    bars = pd.read_csv(Path(__file__).parents[1] / "data" / "synthetic_daily.csv", parse_dates=["date"]).set_index("date")
    if ticker.startswith("ICICI"):
        bars = bars * [1.1, 1.1, 1.1, 1.1, 2]
    bars.index = bars.index.tz_localize("Asia/Kolkata")
    return bars.rename(columns=str.title)


def test_analyze_page_with_fetched_ticker(monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    import quant_engine.providers as providers
    monkeypatch.setattr(providers, "_yahoo_history", _fake_yahoo)
    app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=60).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Fetch by ticker").run()
    assert not app.exception
    app.text_input(key="ticker_symbol").set_value("tcs").run()
    assert not app.exception
    assert any('class="hdr"' in m.value and "TCS" in m.value for m in app.markdown)
    assert len(app.metric) == 4 and app.metric[1].label == "Market read"
    assert any("Market read" in m.value for m in app.markdown)
    assert any("Yahoo Finance" in m.value for m in list(app.markdown) + list(app.caption))


def test_failed_fetch_offers_demo(monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    import quant_engine.providers as providers
    def offline(t, p):
        raise OSError("network unreachable")
    monkeypatch.setattr(providers, "_yahoo_history", offline)
    app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=60).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Fetch by ticker").run()
    assert not app.exception and any("Couldn't load" in e.value for e in app.error)
    next(b for b in app.button if b.label == "Try the demo data instead").click().run()
    assert not app.exception and len(app.metric) == 4


def test_compare_two_fetched_tickers(monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    import quant_engine.providers as providers
    monkeypatch.setattr(providers, "_yahoo_history", _fake_yahoo)
    app = AppTest.from_file(str(Path(__file__).parents[1] / "app.py"), default_timeout=60).run()
    app.radio(key="workspace_page").set_value("Compare stocks").run()
    app.radio(key="comparison_mode").set_value("Fetch two tickers").run()
    assert not app.exception
    assert any(m.label.startswith("Return correlation") for m in app.metric)
