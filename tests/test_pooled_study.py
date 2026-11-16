from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from quant_engine.analysis import analyze
from quant_engine.data import load_bars
from quant_engine.event_study import StudyRules, build_study
from quant_engine.models import Settings
from quant_engine.pooled_study import date_clustered_interval, pooled_study, summarize_pooled

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def demo():
    a = analyze(load_bars((ROOT / "data" / "synthetic_daily.csv").read_bytes(), "s.csv"), Settings())
    return a.frame, a.events


def test_one_stock_pool_reproduces_the_single_stock_study(demo):
    frame, events = demo
    single = build_study(frame, events, StudyRules()).summary.set_index(["cohort", "horizon"])
    pooled = pooled_study({"A": (frame, events, {})}).summary.set_index(["cohort", "horizon"])
    assert set(pooled.index) <= set(single.index) and len(pooled)
    for key, row in pooled.iterrows():
        ref = single.loc[key]
        assert row.events == ref.complete
        for ours, theirs in (("mean_return", "mean_return"), ("median_return", "median_return"),
                             ("positive_fraction", "positive_fraction"), ("difference_from_baseline", "difference_from_baseline")):
            assert (pd.isna(row[ours]) and pd.isna(ref[theirs])) or row[ours] == pytest.approx(ref[theirs])
        assert row.stocks == 1 and row.top_stock_share == 1.0


def test_duplicated_stock_doubles_events_but_not_evidence(demo):
    frame, events = demo
    one = pooled_study({"A": (frame, events, {})}).summary.set_index(["cohort", "horizon"])
    two = pooled_study({"A": (frame, events, {}), "B": (frame.copy(), events, {})}).summary.set_index(["cohort", "horizon"])
    for key, row in two.iterrows():
        assert row.events == 2 * one.loc[key, "events"]
        assert row.distinct_dates == one.loc[key, "distinct_dates"]  # same dates -> no new independent moments
        assert row.mean_return == pytest.approx(one.loc[key, "mean_return"])
        assert row.top_stock_share == pytest.approx(0.5) or row.events == 0
    # Interval: resampling whole dates means identical copies cannot make it narrower.
    values = pd.Series(np.random.default_rng(1).normal(0, 0.02, 60))
    dates = pd.Series([f"d{i}" for i in range(60)])
    lo1, hi1 = date_clustered_interval(values, dates)
    lo2, hi2 = date_clustered_interval(pd.concat([values, values]), pd.concat([dates, dates]))
    assert lo2 == pytest.approx(lo1) and hi2 == pytest.approx(hi1)
    # ...whereas treating the copies as independent dates would (wrongly) narrow it.
    lo3, hi3 = date_clustered_interval(pd.concat([values, values]), pd.Series([f"x{i}" for i in range(120)]))
    assert hi3 - lo3 < hi1 - lo1


def test_interval_basics_and_thresholds():
    assert date_clustered_interval(pd.Series([0.01] * 40), pd.Series(range(40))) == (pytest.approx(0.01), pytest.approx(0.01))
    assert date_clustered_interval(pd.Series([0.1]), pd.Series(["d"])) == (None, None)
    small = pd.DataFrame({"cohort": "c", "horizon": 5, "outcome_state": "Complete", "forward_return": [0.01] * 10,
                          "mfe": 0.02, "mae": -0.01, "control_mean": 0.0, "difference_from_control_mean": 0.01,
                          "known_at": [f"2026-01-{i + 1:02d}" for i in range(10)], "symbol": "A"})
    row = summarize_pooled(small).iloc[0]
    assert row.difference_low is None and "Small sample" in row.sample_note


def test_concentration_and_cohort_filter(demo):
    frame, events = demo
    full = pooled_study({"A": (frame, events, {})})
    cohort = full.summary.cohort.iloc[0]
    only = pooled_study({"A": (frame, events, {})}, StudyRules(cohorts=(cohort,)))
    assert set(only.summary.cohort) == {cohort}
    assert set(only.by_stock.symbol) == {"A"}
    assert only.audit["stocks_with_events"] == 1 and "survivorship" in only.audit["limits"]


def test_bad_stock_is_reported_not_fatal(demo):
    frame, events = demo
    out = pooled_study({"A": (frame, events, {}), "TINY": (frame.iloc[:5], [], {})})
    assert {c["symbol"] for c in out.audit["coverage"]} == {"A", "TINY"}
    assert not out.summary.empty


def test_pooled_page_end_to_end(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import quant_engine.providers as providers

    def fake(ticker, period):
        if ticker.startswith("BAD"):
            raise RuntimeError("HTTP 404")
        bars = pd.read_csv(ROOT / "data" / "synthetic_daily.csv", parse_dates=["date"]).set_index("date")
        if ticker.startswith("REV"):
            bars = bars.iloc[::-1].set_axis(bars.index)
        bars.index = bars.index.tz_localize("Asia/Kolkata")
        return bars.rename(columns=str.title)

    monkeypatch.setattr(providers, "_yahoo_history", fake)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=180).run()
    app.radio(key="workspace_page").set_value("Pattern research").run()
    assert not app.exception and app.segmented_control(key="research_scope").value == "This stock"
    assert any("Historical outcome research" in s.value for s in app.subheader)  # single-stock flow unchanged
    app.segmented_control(key="research_scope").set_value("Watchlist (pooled)").run()
    app.segmented_control(key="pool_preset").set_value("Custom list").run()
    app.text_area(key="pool_text_Custom list").set_value("AAA, REVX, BAD")  # form: value commits with the submit
    next(b for b in app.button if b.label == "Run watchlist study").click().run()
    assert not app.exception
    assert next(m for m in app.metric if m.label == "Stocks studied").value == "2 of 3"
    table = next(d.value for d in app.dataframe if "Pattern" in d.value.columns and "Distinct dates" in d.value.columns)
    assert len(table) > 0 and table["Stocks"].max() <= 2
    assert any("could not be fetched" in e.label for e in app.expander)
