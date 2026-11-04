from dataclasses import asdict
from pathlib import Path
import json

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.analysis import analyze, run_evidence, report_markdown
from quant_engine.data import load_bars, validate_daily
from quant_engine.indicators import indicators
from quant_engine.models import Pivot, ResearchRules, Settings
from quant_engine.research import breakout_events, contextual_candles, chart_formations, momentum_analysis


def frame(n=80):
    raw = pd.DataFrame({"date": pd.bdate_range("2026-01-01", periods=n), "open": 100., "high": 101., "low": 99., "close": 100., "volume": 1000.})
    result = indicators(validate_daily(raw).bars)
    result["atr_14"], result["relative_volume"] = 2., 2.
    return result


def put(f, i, o, h, l, c):
    f.iloc[i, f.columns.get_indexer(["open", "high", "low", "close"])] = [o, h, l, c]


def breakout_fixture():
    f = frame(35)
    put(f, 20, 100, 104, 99, 103)
    put(f, 21, 103, 103, 101, 101.5)
    put(f, 22, 102, 107, 102, 106)
    return f


@pytest.mark.parametrize("direction", [1, -1])
def test_frozen_breakout_retest_continuation_and_mirror(direction):
    f = breakout_fixture()
    if direction == -1:
        before = f[["open", "high", "low", "close"]].copy()
        f["open"], f["close"] = 200 - before.open, 200 - before.close
        f["high"], f["low"] = 200 - before.low, 200 - before.high
    events = [e for e in breakout_events(f) if e["direction"] == direction and e["index"] <= 22]
    assert [e["status"] for e in events] == ["Breakout" if direction == 1 else "Breakdown", "Retest held", "Continuation"]
    assert [e["index"] for e in events] == [20, 21, 22]
    assert all(e["level"] == (101 if direction == 1 else 99) for e in events)
    assert events[0]["reference_end"] == str(f.index[19].date())
    assert all(e["reference_atr"] == 2 for e in events)


def test_failure_precedes_retest_and_expiry_is_explicit():
    f = breakout_fixture()
    put(f, 21, 103, 104, 98, 99)
    e = [e for e in breakout_events(f.iloc[:22]) if e["direction"] == 1]
    assert [x["status"] for x in e] == ["Breakout", "Failed"]
    f = breakout_fixture()
    for i in range(21, len(f)):
        put(f, i, 102, 103, 101.8, 102)
    e = [e for e in breakout_events(f, ResearchRules(retest_window=4)) if e["direction"] == 1]
    assert [x["status"] for x in e] == ["Breakout", "Expired without retest"]
    assert e[-1]["index"] == 24


def test_volume_and_warmup_guards_no_same_bar_retest():
    f = breakout_fixture().iloc[:21].copy()
    assert [e["status"] for e in breakout_events(f)] == ["Breakout"]
    f.iloc[20, f.columns.get_loc("relative_volume")] = .9
    assert not breakout_events(f)
    f.iloc[20, f.columns.get_loc("relative_volume")] = 2
    f.iloc[19, f.columns.get_loc("atr_14")] = np.nan
    assert not breakout_events(f)


@pytest.mark.parametrize("settings", [{"lookback": 1}, {"retest_window": 1}, {"candle_trend_bars": 1}, {"min_relative_volume": float("nan")}, {"breakout_buffer_atr": 2, "invalidation_atr": 1}])
def test_invalid_research_rules(settings):
    with pytest.raises(ValueError):
        ResearchRules(**settings)


def star_fixture(morning=False):
    f = frame(26)
    for i in range(20):
        put(f, i, 100 + 2 * i, 101 + 2 * i, 99 + 2 * i, 100 + 2 * i)
    put(f, 20, 140, 149, 139, 148)
    put(f, 21, 149, 150, 148, 149.5)
    put(f, 22, 149, 150, 142, 143)
    if morning:
        before = f[["open", "high", "low", "close"]].copy()
        f["open"], f["close"] = 300 - before.open, 300 - before.close
        f["high"], f["low"] = 300 - before.low, 300 - before.high
    return f


@pytest.mark.parametrize("morning,name", [(False, "Evening Star"), (True, "Morning Star")])
def test_star_context_and_third_close_availability(morning, name):
    f = star_fixture(morning)
    e = [e for e in contextual_candles(f) if e["name"] == name]
    assert len(e) == 1 and e[0]["index"] == 22
    assert e[0]["formed_at"] == str(f.index[20].date())
    assert not any(e["name"] == name for e in contextual_candles(f.iloc[:22]))
    flat = f.copy()
    flat.iloc[:20, flat.columns.get_indexer(["open", "high", "low", "close"])] = [140, 141, 139, 140]
    assert not any(e["name"] == name for e in contextual_candles(flat))


@pytest.mark.parametrize("down,upper,name", [(True, False, "Hammer"), (False, False, "Hanging man"), (True, True, "Inverted hammer"), (False, True, "Shooting star")])
def test_single_candle_shadow_and_preceding_trend(down, upper, name):
    f = frame(25)
    for i in range(20):
        p = 200 - 2 * i if down else 100 + 2 * i
        put(f, i, p, p + 1, p - 1, p)
    p = 160 if down else 140
    put(f, 20, p, p + 6 if upper else p + 1.5, p - .5 if upper else p - 5, p + 1)
    assert any(e["name"] == name and e["index"] == 20 for e in contextual_candles(f))


def formation_fixture(name):
    f = frame(80)
    highs = [110, 110, 110] if name in {"Rectangle consolidation", "Ascending triangle"} else [110, 106, 102]
    lows = [90, 90, 90] if name in {"Rectangle consolidation", "Descending triangle"} else [90, 92, 94]
    pivots = []
    for i, kind, price in zip([10, 20, 30, 40, 50, 60], ["high", "low"] * 3, [highs[0], lows[0], highs[1], lows[1], highs[2], lows[2]]):
        f.iloc[i, f.columns.get_loc(kind)] = price
        pivots.append(Pivot(kind, i, i + 3, price, str(f.index[i].date()), str(f.index[i + 3].date())))
    if name == "Ascending triangle":
        pivots = [Pivot(p.kind, p.index, p.confirmed_at, {20: 90, 40: 94, 60: 98}.get(p.index, p.price), p.timestamp, p.detected_at) for p in pivots]
        for p in pivots:
            f.iloc[p.index, f.columns.get_loc(p.kind)] = p.price
    put(f, 67, 105, 114, 104, 113)
    return f, pivots


@pytest.mark.parametrize("name", ["Rectangle consolidation", "Ascending triangle", "Descending triangle", "Symmetrical triangle"])
def test_chart_formation_fit_and_delayed_knowledge(name):
    f, pivots = formation_fixture(name)
    events = chart_formations(f, pivots)
    assert events and all(e["name"] == name for e in events)
    assert events[0]["index"] == 63
    assert all(len(e["coordinates"]) == 6 for e in events)
    assert not chart_formations(f.iloc[:63], [p for p in pivots if p.confirmed_at < 63])


def test_divergence_uses_indicator_at_formed_pivots_and_confirmation_delay():
    f = frame(40)
    f["rsi_14"], f["macd"] = 50., 0.
    f.iloc[15, f.columns.get_indexer(["rsi_14", "macd"])] = [80, 2]
    f.iloc[25, f.columns.get_indexer(["rsi_14", "macd"])] = [70, 1]
    pivots = [Pivot("high", i, i + 3, p, str(f.index[i].date()), str(f.index[i + 3].date())) for i, p in [(15, 100), (25, 105)]]
    summary, events = momentum_analysis(f, pivots)
    assert {e["name"] for e in events} == {"Bearish RSI divergence", "Bearish MACD divergence"}
    assert all(e["index"] == 28 for e in events)
    assert "80.0000 → 70.0000" in events[0]["evidence"]
    assert summary["facts"]


def test_chart_pattern_rejects_insufficient_anchors_and_bad_boundary_fit():
    f, pivots = formation_fixture("Rectangle consolidation")
    assert not chart_formations(f, pivots[:5])
    p = pivots[2]
    pivots[2] = Pivot(p.kind, p.index, p.confirmed_at, p.price + 10, p.timestamp, p.detected_at)
    assert not chart_formations(f, pivots)


def test_roc_stochastic_exact_arithmetic_and_flat_undefined_case():
    f = frame(25)
    assert f.roc_10.iloc[-1] == 0
    assert f.stoch_k_14.iloc[-1] == 50
    assert f.stoch_d_3.iloc[-1] == 50
    raw = f[["open", "high", "low", "close", "volume"]].copy()
    raw.high = raw.low = 100.
    assert indicators(raw).stoch_k_14.isna().all()


def test_all_new_event_prefixes_are_future_append_invariant():
    root = Path(__file__).resolve().parents[1]
    d = load_bars((root / "data/synthetic_daily.csv").read_bytes(), "demo.csv")
    whole = analyze(d, Settings())
    for count in (60, 120, 200, 350):
        partial = analyze(type(d)(d.bars.iloc[:count].copy(), [], d.source_hash), Settings())
        assert partial.events == [e for e in whole.events if e["index"] < count]
    evidence = run_evidence(whole, d, Settings(), "SYNTHETIC", "Synthetic")
    json.dumps(evidence, allow_nan=False)
    assert evidence["research_rules"]["lookback"] == 20
    assert "Momentum context" in report_markdown(whole, "SYNTHETIC", "Synthetic")


def test_new_research_panel_and_configurable_rules_ui():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=45).run()
    assert not app.exception
    assert any(t.label == "Patterns & momentum" for t in app.tabs)
    app.number_input(key="research_rvol").set_value(1.0).run()
    assert not app.exception
    assert any("research-events/1" in j.value for j in app.json)
