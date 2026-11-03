from dataclasses import asdict
from io import BytesIO
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quant_engine.analysis import analyze, run_evidence
from quant_engine.charts import price_chart
from quant_engine.data import completed_weeks, load_bars, validate_daily
from quant_engine.indicators import indicators, wilder
from quant_engine.models import Settings
from quant_engine.patterns import candle_events, double_patterns, swings
from quant_engine.strategy import backtest, breakout_signals, current_setup, size_position

ROOT = Path(__file__).resolve().parents[1]


def raw_bars(n=80, price=100):
    return pd.DataFrame({"date": pd.bdate_range("2024-01-01", periods=n),
                         "open": float(price), "high": float(price + 1),
                         "low": float(price - 1), "close": float(price), "volume": 100_000.0})


def demo():
    return load_bars((ROOT / "data" / "synthetic_daily.csv").read_bytes(), "demo.csv")


@pytest.mark.parametrize("mutation,match", [
    (lambda f: f.assign(close=np.nan), "finite"),
    (lambda f: f.assign(volume=-1), "nonnegative"),
    (lambda f: f.assign(high=50), "OHLC"),
    (lambda f: f.assign(open=0), "positive"),
    (lambda f: f.assign(close=np.inf), "finite"),
    (lambda f: f.assign(date="2024-01-01"), "Duplicate"),
    (lambda f: f.assign(date="01/02/2024"), "YYYY-MM-DD"),
    (lambda f: f.assign(date=45200), "Numeric"),
    (lambda f: f.assign(date="2024-01-01T09:15:00"), "YYYY-MM-DD"),
    (lambda f: f.assign(symbol=["A", "B"] * 40), "one symbol"),
])
def test_bad_data_is_rejected(mutation, match):
    with pytest.raises(ValueError, match=match):
        validate_daily(mutation(raw_bars()))


def test_sort_is_disclosed_and_no_missing_rows_filled():
    raw = raw_bars().drop(index=5).iloc[::-1]
    data = validate_daily(raw)
    assert len(data.bars) == 79
    assert data.bars.index.is_monotonic_increasing
    assert any("sorted" in w for w in data.warnings)


def test_xlsx_and_csv_agree_and_hash_is_exact():
    from hashlib import sha256
    raw = raw_bars()
    buffer = BytesIO()
    raw.to_excel(buffer, index=False)
    content = buffer.getvalue()
    xlsx = load_bars(content, "bars.xlsx")
    csv = load_bars(raw.to_csv(index=False).encode(), "bars.csv")
    pd.testing.assert_frame_equal(xlsx.bars, csv.bars)
    assert xlsx.source_hash == sha256(content).hexdigest()


def test_weekly_aggregation_excludes_latest_calendar_week():
    raw = raw_bars(8)
    raw.loc[:4, "volume"] = [10, 20, 30, 40, 50]
    raw.loc[0, "open"] = 99.5
    raw.loc[4, "close"] = 100.5
    weeks = completed_weeks(validate_daily(raw).bars)
    assert len(weeks) == 1
    assert weeks.iloc[0].to_dict() == {"open": 99.5, "high": 101, "low": 99, "close": 100.5, "volume": 150}
    assert weeks.index[0] == pd.Timestamp("2024-01-05")


def test_wilder_arithmetic_seed_then_recursion():
    result = wilder(pd.Series([np.nan, 1.0, 2.0, 3.0, 6.0]), 3)
    assert result.iloc[:3].isna().all()
    assert result.iloc[3] == 2
    assert result.iloc[4] == pytest.approx(10 / 3)


def test_rsi_matches_published_wilder_example_and_atr_seed():
    # Classic Wilder close sequence; independently hand-calculated seed RSI = 70.4641.
    closes = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
              45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28]
    raw = raw_bars(len(closes)).assign(open=closes, close=closes,
                                      high=np.array(closes) + 1, low=np.array(closes) - 1)
    features = indicators(validate_daily(raw).bars)
    assert features.rsi_14.iloc[:14].isna().all()
    assert features.rsi_14.iloc[14] == pytest.approx(70.464135, abs=1e-5)
    assert features.atr_14.iloc[13] == pytest.approx(2)


def test_flat_and_monotonic_series_have_defined_rsi():
    flat = indicators(validate_daily(raw_bars()).bars)
    assert flat.rsi_14.iloc[-1] == 50
    assert flat.atr_14.iloc[-1] == 2
    raw = raw_bars()
    prices = 100 + np.arange(len(raw))
    up = indicators(validate_daily(raw.assign(open=prices, high=prices + 1, low=prices - 1, close=prices)).bars)
    assert up.rsi_14.iloc[-1] == 100
    assert np.isfinite(up.rsi_14.iloc[-1])


def test_future_append_cannot_change_indicators_signals_or_known_events():
    data = demo()
    full = indicators(data.bars)
    full_pivots = swings(full)
    full_events = double_patterns(full, full_pivots)
    for length in (40, 80, 150, 300, 450):
        prefix = indicators(data.bars.iloc[:length])
        pd.testing.assert_frame_equal(prefix, full.iloc[:length])
        pd.testing.assert_series_equal(breakout_signals(prefix, Settings()), breakout_signals(full, Settings()).iloc[:length])
        pivots = swings(prefix)
        assert [asdict(p) for p in pivots] == [asdict(p) for p in full_pivots if p.confirmed_at < length]
        events = double_patterns(prefix, pivots)
        assert events == [e for e in full_events if e["index"] < length]


def test_pivot_confirmation_delay():
    raw = raw_bars(9)
    raw.loc[4, "high"] = 110
    features = indicators(validate_daily(raw).bars)
    assert not swings(features.iloc[:7], 3)
    pivot = swings(features.iloc[:8], 3)[0]
    assert pivot.index == 4 and pivot.confirmed_at == 7
    assert pivot.detected_at == features.index[7].date().isoformat()


def test_double_bottom_coordinates_and_knowledge_time():
    n = 40
    prices = np.interp(np.arange(n), [0, 4, 10, 18, 25, 31, 39], [100, 105, 90, 105, 90.2, 104, 110])
    raw = raw_bars(n).assign(open=prices, close=prices, high=prices + 0.5, low=prices - 0.5)
    features = indicators(validate_daily(raw).bars)
    features["atr_14"] = 2.0
    events = [e for e in double_patterns(features, swings(features, 2)) if e["name"] == "Double bottom"]
    assert events[0]["status"] == "Developing"
    assert events[0]["index"] == 27
    assert events[0]["coordinates"][0] == [features.index[10].date().isoformat(), 89.5]
    assert any(e["status"] == "Confirmed" for e in events)
    for length in range(26, n + 1):
        partial = features.iloc[:length]
        assert double_patterns(partial, swings(partial, 2)) == [e for e in double_patterns(features, swings(features, 2)) if e["index"] < length]


def test_engulfing_is_observation_not_trade_probability():
    raw = raw_bars(3)
    raw.loc[0, ["open", "high", "low", "close"]] = [101, 102, 98, 99]
    raw.loc[1, ["open", "high", "low", "close"]] = [98.5, 102.5, 98, 102]
    events = candle_events(validate_daily(raw).bars)
    assert any(e["name"] == "Bullish engulfing" and e["index"] == 1 for e in events)


def simulator_fixture():
    frame = indicators(validate_daily(raw_bars()).bars)
    # Explicit feature fixture isolates the execution model from indicator tests.
    frame["ema_50"] = 200.0
    frame["relative_volume"] = 1.0
    frame["atr_14"] = 2.0
    frame.iloc[60, frame.columns.get_loc("close")] = 102
    frame.iloc[60, frame.columns.get_loc("high")] = 103
    frame.iloc[60, frame.columns.get_loc("ema_50")] = 99
    frame.iloc[60, frame.columns.get_loc("relative_volume")] = 2
    frame.iloc[61, frame.columns.get_loc("open")] = 104
    frame.iloc[61, frame.columns.get_loc("high")] = 105
    frame.iloc[61, frame.columns.get_loc("low")] = 103
    frame.iloc[61, frame.columns.get_loc("close")] = 104
    return frame


def test_cost_aware_position_sizing_and_caps():
    settings = Settings(fee_bps=10, slippage_bps=5)
    size = size_position(100_000, 100, 95, 1_000_000, settings)
    expected_loss = 100 - 95 * 0.9995 + 0.001 * (100 + 95 * 0.9995)
    assert size["loss_per_unit_with_costs"] == pytest.approx(expected_loss)
    assert size["quantity"] == int(1000 // expected_loss)
    assert size["planned_loss_with_costs"] <= 1000
    assert size["cash_required"] <= 100_000
    assert size_position(100_000, 100, 95, 50, settings)["quantity"] == 0


def test_entry_is_next_open_and_costs_are_charged_both_sides():
    frame = simulator_fixture()
    frame.iloc[62, frame.columns.get_loc("open")] = 105
    frame.iloc[62, frame.columns.get_loc("low")] = 101
    frame.iloc[62, frame.columns.get_loc("high")] = 120
    settings = Settings()
    result = backtest(frame, settings)
    trade = result.trades.iloc[0]
    assert len(result.trades) == 1
    assert trade.entry_index == 61
    assert trade.entry == pytest.approx(104 * 1.0005)
    assert trade.exit == pytest.approx(trade.target * 0.9995)
    assert trade.pnl == pytest.approx(trade.quantity * (trade.exit * 0.999 - trade.entry * 1.001))
    assert result.metrics["final_equity"] == pytest.approx(settings.capital + trade.pnl)


def test_same_bar_ambiguity_uses_stop_first():
    frame = simulator_fixture()
    frame.iloc[61, frame.columns.get_loc("low")] = 90
    frame.iloc[61, frame.columns.get_loc("high")] = 120
    trade = backtest(frame, Settings()).trades.iloc[0]
    assert "both touched" in trade.reason
    assert trade.pnl < 0


def test_gap_can_exceed_planned_risk():
    frame = simulator_fixture()
    frame.iloc[62, frame.columns.get_loc("open")] = 80
    trade = backtest(frame, Settings()).trades.iloc[0]
    assert trade.reason == "Gap through stop"
    assert trade.exit == pytest.approx(80 * 0.9995)
    assert -trade.pnl > trade.planned_risk


def test_drawdown_uses_marked_equity_and_no_trade_case_is_defined():
    frame = indicators(validate_daily(raw_bars()).bars)
    result = backtest(frame, Settings())
    assert result.metrics["trades"] == 0
    assert result.metrics["total_return"] == 0
    assert result.metrics["max_drawdown"] == 0
    assert result.metrics["historical_win_fraction"] is None
    assert current_setup(frame, Settings())["probability"] is None


def test_analysis_export_chart_and_weekly_use_same_numerical_evidence():
    data = demo()
    analysis = analyze(data, Settings())
    evidence = run_evidence(analysis, data, Settings(), "SYNTHETIC", "Synthetic")
    assert json.loads(json.dumps(evidence, allow_nan=False))["probability"] is None
    figure = price_chart(analysis, True)
    assert list(figure.data[0].close) == list(analysis.frame.close.iloc[-250:])
    assert analysis.weekly["last_session"] < analysis.frame.index[-1].date().isoformat()


@pytest.mark.parametrize("kwargs", [{"capital": -1}, {"risk_fraction": 1}, {"max_hold": 1.5}, {"fee_bps": -1}, {"capital": float("nan")}])
def test_invalid_settings_rejected(kwargs):
    with pytest.raises(ValueError):
        Settings(**kwargs)
