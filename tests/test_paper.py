from datetime import date

import pandas as pd
import pytest

from quant_engine.paper import PaperPlan, check_recordable, evaluate, ledger_stats

DAYS = pd.bdate_range("2026-11-02", periods=10)  # Mon 2 Nov ...


def plan(**kw):
    base = dict(symbol="TCS", provider_symbol="TCS.NS", exchange="NSE", signal_date="2026-11-02", signal_close=100.0,
                atr=2.0, stop_atr=1.0, reward_risk=2.0, max_hold=5, fee_bps=0.0, slippage_bps=0.0)
    return PaperPlan(**{**base, **kw})


def bars(rows):
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=DAYS[:len(rows)])


FLAT = (100, 100.5, 99.5, 100)


def test_waiting_until_a_session_after_the_signal_exists():
    out = evaluate(plan(), bars([FLAT]))
    assert out["status"] == "Waiting for entry" and out["entry_price"] is None and out["checked_through"] == "2026-11-02"


def test_target_hit_by_hand():
    # entry 100 at the 3 Nov open; stop 98, target 104; 4 Nov high 104.5 -> target
    out = evaluate(plan(), bars([FLAT, FLAT, (101, 104.5, 100.5, 104)]))
    assert out["status"] == "Target hit" and out["entry_date"] == "2026-11-03" and out["exit_date"] == "2026-11-04"
    assert out["entry_price"] == 100 and out["stop"] == 98 and out["target"] == 104
    assert out["r_multiple"] == pytest.approx(2.0) and out["sessions"] == 2 and out["mfe_r"] == pytest.approx(2.0)


def test_open_trade_reports_unrealized_r_and_excursions():
    out = evaluate(plan(), bars([FLAT, FLAT, (100, 102, 99, 101)]))
    assert out["status"] == "Open" and out["unrealized_r"] == pytest.approx(0.5)
    assert out["mfe_r"] == pytest.approx(1.0) and out["mae_r"] == pytest.approx(-0.5)


def test_gap_stop_both_touched_and_expiry():
    gap = evaluate(plan(), bars([FLAT, FLAT, (95, 96, 94, 95)]))
    assert gap["status"] == "Stopped out" and gap["reason"] == "Gap through stop" and gap["r_multiple"] == pytest.approx(-2.5)
    both = evaluate(plan(), bars([FLAT, FLAT, (100, 105, 97, 100)]))
    assert both["reason"].startswith("Stop (both") and both["r_multiple"] == pytest.approx(-1.0)
    expired = evaluate(plan(max_hold=3), bars([FLAT] * 6))
    assert expired["status"] == "Expired" and expired["sessions"] == 3 and expired["exit_date"] == "2026-11-05"


def test_costs_reduce_r_like_the_backtest():
    out = evaluate(plan(fee_bps=10, slippage_bps=5), bars([FLAT, FLAT, (101, 104.5, 100.5, 104)]))
    entry = 100 * 1.0005
    planned = entry * 1.001 - (entry - 2) * 0.9995 * 0.999
    expected = ((entry + 4) * 0.9995 * 0.999 - entry * 1.001) / planned
    assert out["r_multiple"] == pytest.approx(expected) and out["r_multiple"] < 2


def test_bars_on_or_before_the_signal_are_never_used():
    crash_before = bars([(50, 51, 1, 2), FLAT, FLAT, (101, 104.5, 100.5, 104)])  # wild bar on 2 Nov, before the signal
    later = evaluate(plan(signal_date="2026-11-03"), crash_before)
    assert later["entry_date"] == "2026-11-04" and later["status"] == "Target hit" and later["mae_r"] == pytest.approx(-0.25)
    # Appending future bars never changes an already-closed outcome.
    more = pd.concat([crash_before, bars([FLAT] * 10).iloc[4:].assign(open=1, high=1, low=1, close=1)])
    assert evaluate(plan(signal_date="2026-11-03"), more)["r_multiple"] == later["r_multiple"]


def test_recording_rules_block_hindsight():
    assert check_recordable("2026-11-13", "2026-11-13", today=date(2026, 11, 15)) is None  # Friday signal, Sunday record
    assert "latest completed session" in check_recordable("2026-11-12", "2026-11-13", today=date(2026, 11, 13))
    assert "hindsight" in check_recordable("2026-11-02", "2026-11-02", today=date(2026, 11, 17))
    assert "Replay" in check_recordable("2026-11-13", "2026-11-13", today=date(2026, 11, 13), replay=True)


def test_plan_validation_and_stats():
    with pytest.raises(ValueError):
        plan(atr=0)
    with pytest.raises(ValueError):
        plan(stop_atr=60)  # stop distance above price
    rows = pd.DataFrame([{"status": "Target hit", "r_multiple": 2.0, "sessions": 3, "voided": False},
                         {"status": "Stopped out", "r_multiple": -1.0, "sessions": 2, "voided": False},
                         {"status": "Open", "r_multiple": None, "sessions": 1, "voided": False},
                         {"status": "Target hit", "r_multiple": 2.0, "sessions": 1, "voided": True}])
    s = ledger_stats(rows)
    assert s["recorded"] == 3 and s["voided"] == 1 and s["closed"] == 2 and s["open"] == 1
    assert s["win_rate"] == 0.5 and s["avg_r"] == pytest.approx(0.5) and s["total_r"] == pytest.approx(1.0)


def test_store_roundtrip_dedup_immutable_plan_and_void(tmp_path):
    from quant_engine.paper_store import PaperStore, paper_trades
    store = PaperStore(f"sqlite:///{tmp_path / 'p.sqlite'}")
    p = plan(snapshot={"verdict": "Bullish"}, note="test")
    assert store.add(p) is True
    assert store.add(plan(id="other", snapshot={})) is False  # same ledger/symbol/date/source/pattern
    df = store.load("default")
    assert len(df) == 1 and df.iloc[0].snapshot == {"verdict": "Bullish"}
    again = store.plan(df.iloc[0])
    assert again == p  # plan survives the round trip exactly
    store.save_evaluation(p.id, evaluate(p, bars([FLAT, FLAT, (101, 104.5, 100.5, 104)])))
    row = store.load("default").iloc[0]
    assert row.status == "Target hit" and row.r_multiple == pytest.approx(2.0) and row.signal_close == 100.0
    with pytest.raises(ValueError):
        store.void(p.id, "  ")
    store.void(p.id, "entered by mistake")
    row = store.load("default").iloc[0]
    assert bool(row.voided) and row.void_reason == "entered by mistake"
    assert store.load("someone-else").empty
    # The store exposes no way to change plan columns after insert.
    assert not hasattr(store, "update_plan")


def test_database_url_defaults_to_local_and_normalizes_postgres(monkeypatch, tmp_path):
    from quant_engine.paper_store import database_url
    monkeypatch.delenv("DATABASE_URL", raising=False)
    url, label = database_url(tmp_path)
    assert url.startswith("sqlite:///") and "Local file" in label
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@h:5432/db")
    url, label = database_url(tmp_path)
    assert url == "postgresql+psycopg://u:p@h:5432/db" and "Hosted" in label


def _recent_bars(extra=None):
    """60 synthetic sessions ending on the latest weekday before today, plus optional later sessions."""
    import numpy as np
    from datetime import datetime
    from quant_engine.paper import IST
    end = pd.Timestamp(datetime.now(IST).date()) - pd.offsets.BDay(1)
    idx = pd.bdate_range(end=end, periods=80)
    close = 100 + np.sin(np.arange(80) / 5) * 3 + np.arange(80) * 0.05
    frame = pd.DataFrame({"Open": close, "High": close + 1, "Low": close - 1, "Close": close, "Volume": 1e5}, index=idx)
    if extra is not None:
        frame = pd.concat([frame, extra])
    frame.index = frame.index.tz_localize("Asia/Kolkata")
    return frame


def test_paper_trade_lifecycle_through_the_app(monkeypatch, tmp_path):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    import quant_engine.providers as providers
    root = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'paper.sqlite'}")
    monkeypatch.setattr(providers, "_yahoo_history", lambda t, p: _recent_bars())
    app = AppTest.from_file(str(root / "app.py"), default_timeout=120).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Fetch by ticker").run()
    app.text_input(key="ticker_symbol").set_value("TCS").run()
    assert not app.exception
    next(b for b in app.button if b.label == "Record paper trade").click().run()
    assert not app.exception and any(s.value.startswith("Recorded TCS") for s in app.success)
    # Recording the same setup twice is refused.
    next(b for b in app.button if b.label == "Record paper trade").click().run()
    assert any("already in the 'default' ledger" in w.value for w in app.warning)

    app.radio(key="workspace_page").set_value("Paper trades").run()
    assert not app.exception and app.title[0].value == "Paper trades"
    next(b for b in app.button if b.label == "Update outcomes").click().run()
    table = next(d.value for d in app.dataframe if "Status" in d.value.columns)
    assert list(table["Status"]) == ["Waiting for entry"]  # no session after the signal yet

    # Time passes: three new sessions. Entry at the next open; the third session reaches the target.
    last = _recent_bars().iloc[-1]
    signal = _recent_bars().index[-1].tz_localize(None)
    new_idx = pd.bdate_range(signal + pd.offsets.BDay(1), periods=3)
    c = float(last.Close)
    extra = pd.DataFrame({"Open": [c, c + 1, c + 2], "High": [c + 0.5, c + 1.5, c + 40], "Low": [c - 0.5, c + 0.5, c + 1.5],
                          "Close": [c, c + 1, c + 35], "Volume": 1e5}, index=new_idx)
    monkeypatch.setattr(providers, "_yahoo_history", lambda t, p: _recent_bars(extra))
    from datetime import datetime as real_datetime

    class Later(real_datetime):  # the clock has moved on: the new sessions are now complete
        @classmethod
        def now(cls, tz=None):
            return real_datetime(2031, 1, 1, tzinfo=tz)
    monkeypatch.setattr(providers, "datetime", Later)
    import streamlit as st
    st.cache_data.clear()
    next(b for b in app.button if b.label == "Update outcomes").click().run()
    assert not app.exception
    table = next(d.value for d in app.dataframe if "Status" in d.value.columns)
    assert list(table["Status"]) == ["Target hit"] and table["Entry"].iloc[0] == new_idx[0].date().isoformat()
    assert table["Result (R)"].iloc[0] > 1.5
    assert next(m for m in app.metric if m.label == "Closed").value == "1"
