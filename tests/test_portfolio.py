import math

import numpy as np
import pandas as pd
import pytest

from quant_engine.portfolio import PortfolioRules, run_portfolio, split_date, equal_weight_benchmark

DAYS = pd.bdate_range("2025-01-01", periods=12)
NOCOST = dict(fee_bps=0.0, slippage_bps=0.0)


def frame(rows):
    """rows: list of (open, high, low, close). ATR fixed at 2, relative volume 1."""
    f = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=DAYS[:len(rows)])
    f["volume"] = 1e5
    f["atr_14"] = 2.0
    f["relative_volume"] = 1.0
    return f


def sig(symbol, i, rvol=1.0):
    return {"symbol": symbol, "signal_date": DAYS[i], "entry_date": DAYS[i + 1], "signal_index": i,
            "atr": 2.0, "rvol": rvol, "cohort": "c"}


def run(stocks, signals, **kw):
    rules = PortfolioRules(**{**dict(capital=100_000, risk_pct=1.0, max_positions=5, max_position_pct=100,
                                     stop_atr=1.0, reward_risk=2.0, max_hold=10), **kw})
    return run_portfolio({s: (f, []) for s, f in stocks.items()}, ["c"], rules, pd.DataFrame(signals))


def flat(n=12, price=100.0):
    return [(price, price + 0.5, price - 0.5, price)] * n


def test_single_target_trade_matches_hand_calculation():
    rows = flat()
    rows[2] = (100, 100.5, 99.5, 100)     # entry day: open 100, stop 98, target 104
    rows[3] = (101, 104.5, 100.5, 104)    # target touched
    r = run({"A": frame(rows)}, [sig("A", 1)], **NOCOST)
    t = r.trades.iloc[0]
    # risk 1% of 100,000 = 1,000; per-share risk 2 -> 500 shares; profit 500 x 4 = 2,000
    assert t.quantity == 500 and t.entry == 100 and t.exit == 104 and t.reason == "Target"
    assert t.pnl == pytest.approx(2000) and t.r_multiple == pytest.approx(2.0) and t.sessions == 2
    assert r.metrics["final_equity"] == pytest.approx(102_000)


def test_costs_gap_stop_and_both_touched():
    rows = flat()
    rows[3] = (95, 96, 94, 95)            # opens below stop 98 -> exit at 95, not 98
    r = run({"A": frame(rows)}, [sig("A", 1)], fee_bps=10, slippage_bps=5)
    t = r.trades.iloc[0]
    assert t.reason == "Gap through stop" and t.exit == pytest.approx(95 * (1 - 0.0005))
    entry = 100 * 1.0005
    assert t.entry == pytest.approx(entry)
    assert t.pnl == pytest.approx(t.quantity * t.exit * 0.999 - t.quantity * entry * 1.001)
    rows = flat()
    rows[3] = (100, 106, 97, 100)         # both stop and target inside one bar -> stop assumed first
    t = run({"A": frame(rows)}, [sig("A", 1)], **NOCOST).trades.iloc[0]
    assert t.reason.startswith("Stop (both touched") and t.exit == 98


def test_capacity_priority_and_skips_are_recorded():
    stocks = {s: frame(flat()) for s in "ABC"}
    r = run(stocks, [sig("A", 1, rvol=1.0), sig("B", 1, rvol=3.0), sig("C", 1, rvol=2.0)], max_positions=2, **NOCOST)
    held = set(r.trades.symbol)
    assert held == {"B", "C"}  # highest relative volume first
    assert list(r.skipped.symbol) == ["A"] and r.skipped.reason.iloc[0] == "All position slots full"
    assert r.metrics["signals"] == 3 and r.metrics["skipped"] == 1


def test_cash_accounting_balances_and_holding_limit():
    stocks = {s: frame(flat()) for s in "AB"}
    r = run(stocks, [sig("A", 1), sig("B", 3)], max_hold=3, fee_bps=10, slippage_bps=5)
    assert set(r.trades.reason) == {"Holding limit"} and set(r.trades.sessions) == {3}
    assert r.metrics["final_equity"] == pytest.approx(100_000 + r.trades.pnl.sum())
    assert (r.equity.positions <= 5).all()


def test_position_caps_respected():
    r = run({"A": frame(flat())}, [sig("A", 1)], risk_pct=5, max_position_pct=10, **NOCOST)
    t = r.trades.iloc[0]
    assert t.quantity * t.entry <= 10_000 + 1e-9  # 10% of equity, even though risk budget allows more


def test_no_look_ahead_future_bars_do_not_change_earlier_trades():
    rows = flat()
    rows[3] = (101, 104.5, 100.5, 104)
    full = run({"A": frame(rows)}, [sig("A", 1), sig("A", 6)], **NOCOST).trades
    later = rows[:]
    for k in range(5, 12):
        later[k] = (50, 51, 49, 50)          # crash after the first trade closed
    changed = run({"A": frame(later)}, [sig("A", 1), sig("A", 6)], **NOCOST).trades
    assert full.iloc[0].to_dict() == changed.iloc[0].to_dict()


def test_split_and_benchmark():
    stocks = {"A": (frame([(100 + i, 101 + i, 99 + i, 100 + i) for i in range(10)]), [])}
    assert split_date(stocks, 0.3) == DAYS[7].date().isoformat()
    bench = equal_weight_benchmark(stocks, DAYS[0], DAYS[9])
    assert bench.iloc[0] == 1 and bench.iloc[-1] == pytest.approx(109 / 100)


def test_rules_validation():
    with pytest.raises(ValueError):
        PortfolioRules(risk_pct=10)


def test_strategy_backtest_page_end_to_end(monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    import quant_engine.providers as providers
    root = Path(__file__).resolve().parents[1]

    def fake(ticker, period):
        bars = pd.read_csv(root / "data" / "synthetic_daily.csv", parse_dates=["date"]).set_index("date")
        if ticker.startswith("REV"):
            bars = bars.iloc[::-1].set_axis(bars.index)
        if ticker.startswith("BAD"):
            raise RuntimeError("HTTP 404")
        bars.index = bars.index.tz_localize("Asia/Kolkata")
        return bars.rename(columns=str.title)

    monkeypatch.setattr(providers, "_yahoo_history", fake)
    app = AppTest.from_file(str(root / "app.py"), default_timeout=240).run()
    app.radio(key="workspace_page").set_value("Strategy backtest").run()
    assert not app.exception and app.title[0].value == "Strategy backtest"
    app.segmented_control(key="bt_preset").set_value("Custom list").run()
    app.text_area(key="bt_text_Custom list").set_value("AAA, REVX, BAD")
    next(b for b in app.button if b.label == "Load watchlist").click().run()
    assert not app.exception
    assert any("2 stocks loaded" in s.value and "1 could not be fetched" in s.value for s in app.success)
    next(b for b in app.button if b.label.startswith("Run backtest")).click().run()
    assert not app.exception
    table = next(d.value for d in app.dataframe if "Test years (unseen)" in d.value.columns)
    assert {"Trades", "Max drawdown", "Avg result per trade (R)"} <= set(table.index)
    banners = [m.value for m in list(app.success) + list(app.warning) + list(app.error)]
    assert any(b.startswith("**") for b in banners)


def test_random_entry_control_is_deterministic_and_respects_period():
    from quant_engine.portfolio import random_entry_control, percentile_vs_random
    rows = [(100 + 0.1 * i, 101 + 0.1 * i, 99 + 0.1 * i, 100 + 0.1 * i) for i in range(12)]
    stocks = {s: (frame(rows), []) for s in "AB"}
    rules = PortfolioRules(capital=100_000, risk_pct=1, stop_atr=1, reward_risk=2, max_hold=3, start=DAYS[2].date().isoformat(),
                           end=DAYS[8].date().isoformat(), **NOCOST)
    a = random_entry_control(stocks, rules, 4, draws=5, seed=3)
    b = random_entry_control(stocks, rules, 4, draws=5, seed=3)
    assert a == b and a["draws"] == 5 and a["low_r"] <= a["median_r"] <= a["high_r"]
    assert random_entry_control(stocks, rules, 999, draws=5)["draws"] == 0  # not enough candidate days
    assert percentile_vs_random(10.0, a) == 100.0 and percentile_vs_random(-10.0, a) == 0.0
    assert percentile_vs_random(None, a) is None


def test_verdict_judges_against_random_not_zero():
    from types import SimpleNamespace as NS
    from quant_engine.portfolio_ui import verdict
    control = {"draws": 10, "median_r": 0.1, "low_r": -0.1, "high_r": 0.3, "r_values": [i / 20 - 0.1 for i in range(10)]}
    mk = lambda r, n=50: NS(metrics={"trades": n, "expectancy_r": r, "control": control})
    assert verdict(mk(0.08), mk(0.5))[0].startswith("No clear edge")      # positive, but random entries do as well
    assert verdict(mk(0.5), mk(0.5))[0] == "Held up out of sample"
    assert verdict(mk(0.5), mk(0.15))[0] == "Weakened out of sample"
    assert verdict(mk(0.5), mk(0.0))[0] == "Failed out of sample"
    assert "read this loosely" in verdict(mk(0.5), mk(0.5, n=8))[1]
