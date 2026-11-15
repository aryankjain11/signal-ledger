from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.analysis import analyze, run_evidence
from quant_engine.corporate_actions import apply_actions, read_action_ledger, synthetic_action_files
from quant_engine.data import load_bars
from quant_engine.datasets import Instrument, attach_passport, canonical_bars_bytes, passport_for_analysis
from quant_engine.models import Settings
from quant_engine.strategy import backtest


def source(adjustment="Unadjusted OHLC"):
    bars, actions = synthetic_action_files()
    data = load_bars(bars, "invented-prices.csv")
    attach_passport(data, instrument=Instrument("NSE", "DEMOCA"), provider="Synthetic fixture",
                    input_format="Standard CSV", adjustment=adjustment, sources=[])
    return data, actions


def changed_actions(**changes):
    _, content = source()
    frame = pd.read_csv(BytesIO(content), dtype=str)
    for key, value in changes.items():
        frame.loc[0, key] = value
    return frame.to_csv(index=False).encode()


def test_multiple_actions_exact_prices_volume_boundary_and_immutable_source():
    data, actions = source()
    raw = canonical_bars_bytes(data.bars)
    metadata = deepcopy(data.metadata)
    result, factors = apply_actions(data, read_action_ledger(actions), as_of="2026-06-08", adjusted=True)
    assert result.bars.close.tolist() == [50, 51, 51, 52, 52, 54]
    assert result.bars.volume.tolist() == [4000] * 6
    np.testing.assert_allclose(result.bars[["open", "high", "low", "close"]], data.bars[["open", "high", "low", "close"]].mul([.25, .25, .5, .5, 1, 1], axis=0))
    assert factors.price_multiplier.tolist() == [.25, .25, .5, .5, 1, 1]
    np.testing.assert_allclose(result.bars.close * result.bars.volume, data.bars.close * data.bars.volume)
    assert canonical_bars_bytes(data.bars) == raw and data.metadata == metadata
    assert result.source_hash == data.source_hash
    assert result.metadata["normalized_sha256"] == data.metadata["normalized_sha256"]
    assert result.metadata["dataset_id"] == data.metadata["dataset_id"]
    assert not any(w.startswith("A close-to-close move exceeds") for w in result.warnings)
    assert result.metadata["original_data_warnings"] == data.warnings
    assert result.metadata["corporate_actions"]["applied_events"] == 2
    assert "execution_restriction" in result.metadata


def test_replay_excludes_events_not_known_or_effective_then_rebases_at_cutoff():
    data, actions = source()
    ledger = read_action_ledger(actions)
    early, _ = apply_actions(data, ledger, as_of="2026-06-02", adjusted=True)
    assert early.bars.close.tolist() == [200, 204]
    assert len(early.metadata["corporate_actions"]["known_events"]) == 1
    assert early.metadata["corporate_actions"]["applied_events"] == 0
    middle, _ = apply_actions(data, ledger, as_of="2026-06-03", adjusted=True)
    assert middle.bars.close.tolist() == [100, 102, 102]
    assert "demo-bonus" not in json.dumps(middle.metadata["corporate_actions"])
    full, _ = apply_actions(data, ledger, as_of="2026-06-08", adjusted=True)
    assert full.metadata["research_view_id"] != early.metadata["research_view_id"]


def test_late_correction_only_available_on_declared_known_date():
    data, content = source()
    frame = pd.read_csv(BytesIO(content), dtype=str).iloc[:1].copy()
    frame["known_on"] = "2026-06-04"
    ledger = read_action_ledger(frame.to_csv(index=False).encode())
    before, _ = apply_actions(data, ledger, as_of="2026-06-03", adjusted=True)
    assert before.metadata["corporate_actions"]["known_events"] == []
    assert before.bars.close.tolist() == [200, 204, 102]
    after, _ = apply_actions(data, ledger, as_of="2026-06-04", adjusted=True)
    assert after.bars.close.tolist() == [100, 102, 102, 104]


def test_original_mode_records_events_without_adjusting_and_restricts_execution():
    data, content = source()
    result, factors = apply_actions(data, read_action_ledger(content), as_of="2026-06-08", adjusted=False)
    pd.testing.assert_frame_equal(result.bars, data.bars)
    assert factors.price_multiplier.eq(1).all()
    assert result.metadata["corporate_actions"]["applied_events"] == 0
    assert result.metadata["corporate_actions"]["effective_events_in_range"] == 2
    assert "execution_restriction" in result.metadata


def test_reverse_split_is_inverse_transform_and_event_at_first_bar_changes_nothing():
    data, _ = source()
    ledger = read_action_ledger(changed_actions(shares_before="2", shares_after="1"))
    result, _ = apply_actions(data, ledger, as_of="2026-06-03", adjusted=True)
    assert result.bars.close.tolist() == [400, 408, 102]
    assert result.bars.volume.tolist() == [500, 500, 2000]
    only = deepcopy(data)
    only.bars = only.bars.loc["2026-06-03":]
    same, _ = apply_actions(only, ledger, as_of="2026-06-03", adjusted=True)
    assert same.bars.close.iloc[0] == 102


@pytest.mark.parametrize("changes,match", [
    ({"action_type": "dividend"}, "Only split and bonus"),
    ({"action_type": "merger"}, "Only split and bonus"),
    ({"action_type": "rights"}, "Only split and bonus"),
    ({"shares_before": "0"}, "between"), ({"shares_after": "-1"}, "positive whole"),
    ({"shares_after": "1.5"}, "positive whole"), ({"shares_after": "nan"}, "positive whole"),
    ({"shares_after": "1000001"}, "between"), ({"shares_after": "1"}, "nontrivial"),
    ({"action_type": "bonus", "shares_before": "2", "shares_after": "1"}, "must exceed"),
    ({"source": ""}, "source reference"), ({"symbol": ""}, "instrument symbol"),
    ({"action_id": ""}, "Action IDs"), ({"ex_date": "03-Jun-2026"}, "YYYY-MM-DD"),
    ({"known_on": "2026-02-30"}, "invalid date"),
])
def test_unsafe_or_ambiguous_action_inputs_rejected(changes, match):
    with pytest.raises(ValueError, match=match):
        read_action_ledger(changed_actions(**changes))


def test_duplicates_ambiguous_headers_and_resource_limits():
    _, content = source()
    frame = pd.read_csv(BytesIO(content), dtype=str)
    duplicate = pd.concat([frame, frame.iloc[:1]])
    with pytest.raises(ValueError, match="Action IDs"):
        read_action_ledger(duplicate.to_csv(index=False).encode())
    frame.loc[1, "ex_date"] = frame.loc[0, "ex_date"]
    with pytest.raises(ValueError, match="same symbol/ex-date"):
        read_action_ledger(frame.to_csv(index=False).encode())
    with pytest.raises(ValueError, match="unique columns"):
        read_action_ledger(content.replace(b"symbol,", b"symbol,SYMBOL,"))
    with pytest.raises(ValueError, match="1 MB"):
        read_action_ledger(b"x" * (1024 * 1024 + 1))
    with pytest.raises(ValueError, match="1,000"):
        read_action_ledger(pd.concat([frame] * 501).to_csv(index=False).encode())


@pytest.mark.parametrize("basis", ["Unknown / unverified", "Consistently adjusted OHLC"])
def test_unknown_or_already_adjusted_source_cannot_be_adjusted(basis):
    data, content = source(basis)
    with pytest.raises(ValueError, match="double adjustment"):
        apply_actions(data, read_action_ledger(content), as_of="2026-06-08", adjusted=True)


def test_identity_date_gaps_double_adjustment_and_serializable_evidence():
    data, content = source()
    other = pd.read_csv(BytesIO(content), dtype=str)
    other["symbol"] = "OTHER"
    with pytest.raises(ValueError, match="No actions match"):
        apply_actions(data, read_action_ledger(other.to_csv(index=False).encode()), as_of="2026-06-03", adjusted=True)
    gap = deepcopy(data)
    gap.bars = gap.bars.drop(pd.Timestamp("2026-06-03"))
    with pytest.raises(ValueError, match="no observed bar"):
        apply_actions(gap, read_action_ledger(content), as_of="2026-06-08", adjusted=True)
    result, _ = apply_actions(data, read_action_ledger(content), as_of="2026-06-08", adjusted=True)
    with pytest.raises(ValueError, match="already has an action audit"):
        apply_actions(result, read_action_ledger(content), as_of="2026-06-08", adjusted=True)
    analysis = analyze(result, Settings())
    assert "execution unavailable" in analysis.setup["status"]
    with pytest.raises(ValueError, match="share-accounting"):
        backtest(analysis.frame, Settings())
    evidence = run_evidence(analysis, result, Settings(), "DEMOCA", result.metadata["analysis_price_basis"])
    assert evidence["data_passport"]["analyzed_normalized_sha256"] == sha256(canonical_bars_bytes(result.bars)).hexdigest()
    assert passport_for_analysis(result)["corporate_actions"]["ledger_sha256"] == sha256(content).hexdigest()
    json.dumps(evidence, allow_nan=False)


def test_ledger_order_does_not_change_adjusted_values_and_factor_hashes_are_stable():
    data, content = source()
    reversed_content = pd.read_csv(BytesIO(content)).iloc[::-1].to_csv(index=False).encode()
    a, af = apply_actions(data, read_action_ledger(content), as_of="2026-06-08", adjusted=True)
    b, bf = apply_actions(data, read_action_ledger(reversed_content), as_of="2026-06-08", adjusted=True)
    pd.testing.assert_frame_equal(a.bars, b.bars)
    pd.testing.assert_frame_equal(af, bf)
    assert a.metadata["corporate_actions"]["result_visible_sha256"] == b.metadata["corporate_actions"]["result_visible_sha256"]


def test_action_upload_ui_adjusted_view_and_execution_block(monkeypatch):
    import streamlit as st
    prices, events = synthetic_action_files()
    def uploader(*args, **kwargs):
        content, name = (events, "actions.csv") if kwargs.get("key") == "action_ledger_file" else (prices, "synthetic-prices.csv")
        uploaded = BytesIO(content)
        uploaded.name = name
        return uploaded
    monkeypatch.setattr(st, "file_uploader", uploader)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    app.radio[0].set_value("Upload daily data").run()
    app.checkbox[0].check().run()
    app.checkbox(key="use_action_ledger").check().run()
    app.radio(key="action_price_view").set_value("Split/bonus adjusted research").run()
    assert any("Select Unadjusted OHLC" in w.value for w in app.warning)
    app.selectbox[1].set_value("Unadjusted OHLC").run()
    assert not app.exception
    assert any("adjusted research view" in i.value for i in app.info)
    assert app.button(key="run_baseline").disabled
    assert any("execution unavailable" in h.value for h in app.subheader)
    assert any("Corporate-action audit" in e.label for e in app.expander)
    app.select_slider[0].set_value("2026-06-03").run()
    assert not app.exception
    assert app.metric[0].value == "102.00"


def test_view_switch_cache_isolates_execution_policy_when_prices_match(monkeypatch):
    import streamlit as st
    prices, events = synthetic_action_files()
    frame = pd.read_csv(BytesIO(events)).iloc[:1].copy()
    frame["ex_date"] = "2026-06-05"
    events = frame.to_csv(index=False).encode()
    def uploader(*args, **kwargs):
        uploaded = BytesIO(events if kwargs.get("key") == "action_ledger_file" else prices)
        uploaded.name = "actions.csv" if kwargs.get("key") == "action_ledger_file" else "prices.csv"
        return uploaded
    monkeypatch.setattr(st, "file_uploader", uploader)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    app.radio[0].set_value("Upload daily data").run()
    app.checkbox[0].check().run()
    app.selectbox[1].set_value("Unadjusted OHLC").run()
    app.checkbox(key="use_action_ledger").check().run()
    app.select_slider[0].set_value("2026-06-03").run()
    assert not app.button(key="run_baseline").disabled
    app.radio(key="action_price_view").set_value("Split/bonus adjusted research").run()
    assert app.button(key="run_baseline").disabled
    app.radio(key="action_price_view").set_value("Original prices").run()
    assert not app.exception and not app.button(key="run_baseline").disabled
    assert not any("execution unavailable" in h.value for h in app.subheader)
