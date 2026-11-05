"""Independent price fixtures test timing, censoring, sample selection and control arithmetic."""
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.analysis import analyze
from quant_engine.data import load_bars
from quant_engine.event_study import StudyRules, build_study, occurrence_ledger, study_record
from quant_engine.event_study_ui import event_detail_chart, summary_display
from quant_engine.models import Settings, ValidatedData

ROOT = Path(__file__).resolve().parents[1]


def frame(n=30):
    return pd.DataFrame({"open": 100., "high": 110., "low": 90., "close": 100.,
        "volume": 1000., "ema_50": 95., "relative_volume": 1.}, index=pd.bdate_range("2026-01-01", periods=n))


def event(f, i=1, direction=1, name="Example", state="Breakout", identity=None):
    return {"id": identity or f"event-{i}-{name}", "family": "breakout", "name": name,
        "status": state, "direction": direction, "formed_at": f.index[max(0, i-1)].date().isoformat(),
        "detected_at": f.index[i].date().isoformat(), "index": i}


def rules(**values):
    return StudyRules(horizons=(1, 3), overlap="Keep all", min_controls=1, **values)


def test_reference_is_after_knowledge_and_detection_candle_extremes_are_excluded():
    f = frame(8)
    f.loc[f.index[1], ["high", "low", "close"]] = [999., 1., 105.]
    f.loc[f.index[2], ["open", "high", "low", "close"]] = [120., 132., 108., 126.]
    result = build_study(f, [event(f)], rules())
    row = result.outcomes.query("horizon == 1").iloc[0]
    assert row.reference_date == f.index[2].date().isoformat()
    assert row.reference_price == 120
    assert row.forward_return == pytest.approx(.05)
    assert row.mfe == pytest.approx(.1)
    assert row.mae == pytest.approx(-.1)
    close_row = build_study(f, [event(f)], rules(reference="Detection close")).outcomes.query("horizon == 1").iloc[0]
    assert close_row.reference_price == 105
    assert close_row.forward_return == pytest.approx(.2)
    assert close_row.mae == 0


def test_bearish_alignment_and_raw_price_perspective_have_explicit_opposite_signs():
    f = frame(8)
    f.loc[f.index[2], ["high", "low", "close"]] = [105., 80., 90.]
    aligned = build_study(f, [event(f, direction=-1)], rules()).outcomes.query("horizon == 1").iloc[0]
    assert aligned.forward_return == pytest.approx(.1)
    assert aligned.mfe == pytest.approx(.2)
    assert aligned.mae == pytest.approx(-.05)
    raw = build_study(f, [event(f, direction=-1)], rules(perspective="Upward price change")).outcomes.query("horizon == 1").iloc[0]
    assert raw.forward_return == pytest.approx(-.1)
    assert raw.mfe == pytest.approx(.05)
    assert raw.mae == pytest.approx(-.2)


@pytest.mark.parametrize("reference", ["Next observed open", "Detection close"])
@pytest.mark.parametrize("direction", [1, -1])
def test_three_observation_excursions_match_independent_hand_specified_extremes(reference, direction):
    f = frame(8)
    f.loc[f.index[1], "close"] = 102.
    f.loc[f.index[2], ["open", "high", "low", "close"]] = [104., 109., 97., 101.]
    f.loc[f.index[3], ["open", "high", "low", "close"]] = [100., 111., 96., 105.]
    f.loc[f.index[4], ["open", "high", "low", "close"]] = [103., 108., 94., 98.]
    row = build_study(f, [event(f, direction=direction)], rules(reference=reference)).outcomes.query("horizon == 3").iloc[0]
    p = 104. if reference == "Next observed open" else 102.
    assert row.forward_return == pytest.approx(direction * (98/p - 1))
    assert row.mfe == pytest.approx(111/p - 1 if direction == 1 else 1 - 94/p)
    assert row.mae == pytest.approx(94/p - 1 if direction == 1 else 1 - 111/p)


def test_confirmation_delay_uses_detection_index_and_never_formation_price():
    f = frame(12)
    e = event(f, i=6)
    e["formed_at"] = f.index[2].date().isoformat()
    f.loc[f.index[2], ["open", "low", "close"]] = [50., 45., 50.]
    f.loc[f.index[7], ["open", "low", "close"]] = [95., 85., 95.]
    row = build_study(f, [e], rules()).outcomes.query("horizon == 1").iloc[0]
    assert row.reference_price == 95
    assert row.forward_return == 0


def test_incomplete_horizons_keep_occurrences_and_null_all_outcomes_without_forced_exit():
    f = frame(6)
    result = build_study(f, [event(f, i=4), event(f, i=5)], rules())
    assert len(result.outcomes) == 4
    assert len(result.outcomes.query("outcome_state == 'Complete'")) == 1
    incomplete = result.outcomes.query("outcome_state == 'Incomplete horizon'")
    assert incomplete[["forward_return", "mfe", "mae"]].isna().all().all()
    s = result.summary.query("horizon == 3").iloc[0]
    assert s.complete == 0 and s.incomplete == 2 and pd.isna(s.positive_fraction)
    json.dumps(study_record(result), allow_nan=False)


def test_later_failure_does_not_remove_or_relabel_initial_breakout():
    f = frame(15)
    original = event(f, i=3, identity="same")
    failure = event(f, i=7, identity="same", state="Failed")
    result = build_study(f, [original, failure], rules())
    assert result.audit["included_occurrences"] == 1
    assert set(result.outcomes.known_at) == {original["detected_at"]}
    assert result.occurrences.iloc[1].selection == "Diagnostic lifecycle state"
    retest = event(f, i=6, identity="same", state="Retest held")
    separate = build_study(f, [original, retest], rules())
    assert separate.summary.cohort.nunique() == 2


def test_geometry_transitions_and_neutral_candles_are_not_given_invented_directions():
    f = frame(12)
    developing = {**event(f), "family": "chart", "status": "Developing", "direction": 0}
    downward = {**developing, "index": 4, "detected_at": f.index[4].date().isoformat(), "status": "Confirmed downward break"}
    assert occurrence_ledger(f, [developing, downward]).direction.tolist() == [0, -1]
    neutral = {**event(f), "family": "candle", "name": "Doji", "direction": 0, "status": "Observed geometry"}
    assert build_study(f, [neutral], rules()).outcomes.empty
    assert not build_study(f, [neutral], rules(perspective="Upward price change")).outcomes.empty
    legacy = {k: v for k, v in neutral.items() if k not in {"family", "direction"}}
    legacy["name"] = "Bearish engulfing"
    assert occurrence_ledger(f, [legacy]).iloc[0].direction == -1


def test_exact_duplicates_and_same_date_cohort_paths_do_not_inflate_sample_size():
    f = frame()
    a = event(f)
    b = {**a, "id": "another-geometry"}
    result = build_study(f, [a, a, b], rules())
    assert result.audit["included_occurrences"] == 1
    assert result.audit["selection_counts"]["Duplicate transition"] == 1
    assert result.audit["selection_counts"]["Same cohort and knowledge date"] == 1
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        occurrence_ledger(f, [a, {**a, "evidence": "conflicts"}])


def test_overlap_thinning_uses_largest_horizon_before_maturity_with_closed_endpoints():
    f = frame(12)
    events = [event(f, i=i) for i in (1, 2, 4, 5, 9, 10)]
    result = build_study(f, events, StudyRules(horizons=(1, 3)))
    included = result.occurrences.query("selection == 'Included'")
    assert included["index"].tolist() == [1, 5, 9]
    assert result.summary.query("horizon == 3").iloc[0].incomplete == 1
    full = build_study(f, events, rules())
    assert full.audit["included_occurrences"] == 6
    other = build_study(f, events + [event(f, i=2, name="Other")], StudyRules(horizons=(1, 3)))
    assert other.audit["included_occurrences"] == 4  # Different cohorts may overlap.


def test_context_filters_are_sampled_at_knowledge_not_at_formation_or_future_exit():
    f = frame()
    f.loc[f.index[5], ["ema_50", "relative_volume"]] = [105., 1.5]
    result = build_study(f, [event(f, i=1), event(f, i=5)], rules(trend="At/below EMA50", volume="RVOL >= 1.2"))
    assert result.occurrences.query("selection == 'Included'")["index"].tolist() == [5]
    assert result.audit["included_occurrences"] == 1
    # No matching non-event context exists, so no fabricated baseline.
    assert result.outcomes.control_count.eq(0).all()
    assert result.summary.matched_events.eq(0).all()


def test_baseline_matching_uses_correct_context_and_event_weighted_comparable_coverage():
    f = frame(12)
    f.loc[f.index[[3, 5]], "relative_volume"] = 2.
    f.loc[f.index[4], "close"] = 104.  # high-volume control anchor3: +4%
    f.loc[f.index[6], "close"] = 108.  # high-volume event anchor5: +8%
    f.loc[f.index[2], "close"] = 102.  # ordinary-volume control anchor1: +2%
    result = build_study(f, [event(f, i=5)], StudyRules(horizons=(1,), overlap="Keep all", min_controls=1))
    row = result.outcomes.iloc[0]
    assert row.control_count == 1
    assert row.control_mean == pytest.approx(.04)
    assert row.difference_from_control_mean == pytest.approx(.04)
    assert result.summary.iloc[0].matched_event_mean == pytest.approx(.08)
    assert result.summary.iloc[0].matched_baseline_mean == pytest.approx(.04)
    assert 5 not in result.controls["index"].tolist()
    insufficient = build_study(f, [event(f, i=5)], StudyRules(horizons=(1,), overlap="Keep all", min_controls=2))
    assert insufficient.outcomes.iloc[0].control_count == 1
    assert pd.isna(insufficient.outcomes.iloc[0].control_mean)


def test_baseline_has_no_future_event_exclusion_or_future_context_filter():
    f = frame(15)
    events = [event(f, i=4), event(f, i=8)]
    result = build_study(f, events, rules())
    # Anchor7 is eligible even though a selected event occurs during its future horizon.
    assert 7 in result.controls["index"].tolist()
    assert not {4, 8} & set(result.controls["index"])
    assert "future events allowed" in result.audit["baseline"]


def test_baseline_chart_compares_identical_event_coverage_instead_of_full_sample_mean():
    f = frame(12)
    f.loc[f.index[1], "ema_50"] = np.nan  # No other unavailable-EMA anchor exists.
    f.loc[f.index[[3, 5]], "relative_volume"] = 2.
    f.loc[f.index[2], "close"] = 98.
    f.loc[f.index[4], "close"] = 104.
    f.loc[f.index[6], "close"] = 108.
    result = build_study(f, [event(f, i=1), event(f, i=5)], StudyRules(horizons=(1,), overlap="Keep all", min_controls=1))
    row = result.summary.iloc[0]
    assert row.complete == 2 and row.matched_events == 1
    assert row.mean_return == pytest.approx(.03)
    assert row.matched_event_mean == pytest.approx(.08)
    assert row.matched_baseline_mean == pytest.approx(.04)
    assert row.difference_from_baseline == pytest.approx(.04)


def test_missing_dates_are_not_filled_and_horizons_count_observations_not_days():
    f = frame(3)
    f.index = pd.DatetimeIndex(["2026-01-02", "2026-01-05", "2026-01-09"])
    f.loc[f.index[2], "close"] = 104.
    result = build_study(f, [event(f, i=0)], StudyRules(horizons=(2,), min_controls=1))
    row = result.outcomes.iloc[0]
    assert row.forward_return == pytest.approx(.04)
    assert row.calendar_days == 7
    assert row.exit_date == "2026-01-09"
    assert len(result.occurrences) == 1


def test_action_crossing_exclusion_and_adjusted_research_are_distinct():
    f = frame(10)
    audit = {"mode": "Original prices with action audit", "known_events": [{"ex_date": f.index[3].date().isoformat()}]}
    raw = build_study(f, [event(f)], rules(), {"corporate_actions": audit})
    assert raw.outcomes.query("horizon == 1").iloc[0].outcome_state == "Complete"
    assert raw.outcomes.query("horizon == 3").iloc[0].outcome_state == "Excluded raw corporate action"
    assert pd.isna(raw.outcomes.query("horizon == 3").iloc[0].mfe)
    adjusted = build_study(f, [event(f)], rules(), {"corporate_actions": {**audit, "mode": "Split/bonus adjusted research"}})
    assert adjusted.outcomes.outcome_state.eq("Complete").all()
    on_date = build_study(f, [event(f, i=3)], rules(), {"corporate_actions": audit})
    assert on_date.outcomes.outcome_state.eq("Complete").all()


def test_date_filter_limits_anchors_but_outcomes_can_extend_after_anchor_end():
    f = frame(15)
    result = build_study(f, [event(f, i=2), event(f, i=5), event(f, i=8)],
        rules(start=f.index[3].date().isoformat(), end=f.index[5].date().isoformat()))
    assert result.occurrences.query("selection == 'Included'")["index"].tolist() == [5]
    assert result.outcomes.outcome_state.eq("Complete").all()
    assert set(result.controls["index"]) <= {3, 4}
    assert result.outcomes.query("horizon == 3").iloc[0].exit_date == f.index[8].date().isoformat()


def test_means_quartiles_positive_fraction_flat_count_and_percent_display():
    f = frame(12)
    f.loc[f.index[2], "close"] = 104.
    f.loc[f.index[4], "close"] = 98.
    result = build_study(f, [event(f, i=i) for i in (1, 3, 5)], StudyRules(horizons=(1,), overlap="Keep all", min_controls=1))
    s = result.summary.iloc[0]
    assert s.mean_return == pytest.approx(.02/3)
    assert s.median_return == 0
    assert s.q25_return == pytest.approx(-.01)
    assert s.q75_return == pytest.approx(.02)
    assert s.positive_fraction == pytest.approx(1/3)
    assert s.zero_count == 1 and s.complete == 3
    assert summary_display(result.summary).iloc[0]["Mean movement (%)"] == pytest.approx(2/3)


def test_outcomes_and_selection_are_future_append_invariant_and_replay_censors_newest():
    f = frame(30)
    events = [event(f, i=i) for i in (2, 5, 9, 13, 17, 21, 27)]
    full = build_study(f, events, StudyRules(horizons=(1, 3)))
    partial = build_study(f.iloc[:19], events[:5], StudyRules(horizons=(1, 3)))
    assert partial.occurrences.event_key.tolist() == full.occurrences.iloc[:5].event_key.tolist()
    assert partial.occurrences.selection.tolist() == full.occurrences.iloc[:5].selection.tolist()
    for _, row in partial.outcomes.query("outcome_state == 'Complete'").iterrows():
        other = full.outcomes.loc[full.outcomes.event_key.eq(row.event_key) & full.outcomes.horizon.eq(row.horizon)].iloc[0]
        assert row.forward_return == other.forward_return
        assert row.mfe == other.mfe and row.mae == other.mae
    assert partial.outcomes.query("index == 17 and horizon == 3").iloc[0].outcome_state == "Incomplete horizon"


@pytest.mark.parametrize("changes", [
    {"horizons": ()}, {"horizons": (0,)}, {"horizons": (5, 1)}, {"horizons": (True,)},
    {"horizons": (1, 1)}, {"horizons": (253,)}, {"reference": "Same bar high"},
    {"perspective": "Forecast"}, {"overlap": "Magic"}, {"min_controls": 0},
    {"trend": "Future bullish"}, {"volume": "Infinite"}, {"start": "2026-02-01", "end": "2026-01-01"},
    {"start": "2026-01-01T12:00:00"},
])
def test_invalid_study_definitions_are_rejected(changes):
    with pytest.raises(ValueError):
        replace(StudyRules(), **changes)


def test_invalid_bars_events_empty_ledgers_and_unknown_cohorts_are_handled():
    f = frame()
    assert build_study(f, [], rules()).summary.empty
    for bad in (f.iloc[::-1], pd.concat([f, f.iloc[:1]]), f.assign(close=-1), f.assign(high=1)):
        with pytest.raises(ValueError):
            build_study(bad, [], rules())
    for bad in ({**event(f), "index": 99}, {**event(f), "detected_at": "2026-10-01"}, {**event(f), "direction": 2}):
        with pytest.raises(ValueError):
            occurrence_ledger(f, [bad])
    with pytest.raises(ValueError, match="selected cohort"):
        build_study(f, [event(f)], rules(cohorts=("absent",)))


def test_gross_measurements_ignore_strategy_costs_and_record_reproducible_identity():
    f = frame()
    a = build_study(f, [event(f)], rules(), {"source_sha256": "abc"})
    b = build_study(f, [event(f)], rules(), {"source_sha256": "abc"})
    assert a.run_id == b.run_id
    assert a.run_id != build_study(f, [event(f)], rules(reference="Detection close"), {"source_sha256": "abc"}).run_id
    assert a.run_id != build_study(f, [event(f)], rules(), {"source_sha256": "different"}).run_id
    record = study_record(a)
    assert len(record["audit"]["visible_ohlcv_sha256"]) == 64
    assert "No costs" in record["audit"]["units"]
    json.dumps(record, allow_nan=False)


def test_real_engine_catalogue_runs_and_records_are_finite_and_chartable():
    data = load_bars((ROOT / "data/synthetic_daily.csv").read_bytes(), "synthetic.csv")
    analysis = analyze(data, Settings())
    result = build_study(analysis.frame, analysis.events)
    assert result.audit["included_occurrences"] > 10
    assert set(result.outcomes.family) == {"breakout", "chart", "candle", "momentum"}
    assert not result.controls.empty
    json.dumps(study_record(result), allow_nan=False)
    occurrence = result.occurrences.query("selection == 'Included'").iloc[0].to_dict()
    outcome = result.outcomes.loc[result.outcomes.event_key.eq(occurrence["event_key"])].iloc[0].to_dict()
    assert len(event_detail_chart(analysis.frame, occurrence, outcome, int(outcome["horizon"])).data) >= 2


def test_event_study_workspace_filters_replay_and_export_ui():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    app.selectbox(key="workspace_page").set_value("After the pattern").run()
    assert not app.exception
    assert app.title[0].value == "After the pattern"
    assert any(t.label == "Inspect an occurrence" for t in app.tabs)
    assert any(m.label == "Included occurrences" and int(m.value) > 0 for m in app.metric)
    assert any("pattern-outcomes/1" in j.value for j in app.json)
    app.selectbox(key="study_reference").set_value("Detection close")
    app.selectbox(key="study_overlap").set_value("Keep all")
    app.button(key="FormSubmitter:event_study_form-Run event study").click().run()
    assert not app.exception
    app.multiselect(key="study_horizons").set_value([])
    app.button(key="FormSubmitter:event_study_form-Run event study").click().run()
    assert any("Choose at least one" in w.value for w in app.warning)
    app.multiselect(key="study_horizons").set_value([1, 5])
    app.button(key="FormSubmitter:event_study_form-Run event study").click().run()
    app.select_slider[0].set_value("2023-01-10").run()
    assert not app.exception
    assert not app.error
    assert app.multiselect(key="study_cohorts").value
    assert app.select_slider(key="study_period").value[-1] <= "2023-01-10"
    assert any(m.label == "Included occurrences" for m in app.metric)
