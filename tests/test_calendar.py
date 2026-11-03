from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.calendar import (CALENDAR_HASH, CALENDAR_VERSION, IST, assess_data_quality,
                                   attach_quality, latest_ready_session, session_dates)
from quant_engine.data import validate_daily
from quant_engine.datasets import Instrument, attach_passport, canonical_bars_bytes, passport_for_analysis


def dataset(dates, exchange="NSE", synthetic=False):
    frame = pd.DataFrame({"date": dates, "open": 100, "high": 102, "low": 98, "close": 101, "volume": 1000})
    data = validate_daily(frame, "fixture", min_rows=1)
    return attach_passport(data, instrument=Instrument(exchange, "DEMO"), provider="Invented test data",
                           input_format="Standard CSV", adjustment="Unknown / unverified", sources=[], is_synthetic=synthetic)


def clock(value="2026-11-03T19:00:00+05:30"):
    return datetime.fromisoformat(value)


def test_trading_holidays_not_settlement_holidays_and_exceptional_sunday():
    # Jan 15 closure amendment; Feb 1 live Budget session; Nov 8 Muhurat.
    jan = session_dates("2026-01-14", "2026-01-16")
    assert jan.strftime("%Y-%m-%d").tolist() == ["2026-01-14", "2026-01-16"]
    assert "2026-02-01" in session_dates("2026-01-30", "2026-02-02").strftime("%Y-%m-%d")
    assert "2026-11-08" in session_dates("2026-11-06", "2026-11-11").strftime("%Y-%m-%d")
    assert len(session_dates("2026-04-01", "2026-04-01")) == 1  # bank closing is not CM trading holiday
    assert len(session_dates("2026-10-20", "2026-10-20")) == 0


@pytest.mark.parametrize("start,end", [("2025-12-31", "2026-01-02"), ("2026-12-31", "2027-01-01"), ("2026-01-02", "2026-01-01")])
def test_unsupported_range_not_extrapolated(start, end):
    with pytest.raises(ValueError, match="2026 only"):
        session_dates(start, end)


def test_calendar_times_rejected_and_aware_assessment_required():
    with pytest.raises(ValueError, match="session dates"):
        session_dates("2026-01-02T09:15", "2026-01-03")
    with pytest.raises(ValueError, match="timezone-aware"):
        latest_ready_session(datetime(2026, 11, 3))


@pytest.mark.parametrize("instant,expected", [
    ("2026-11-03T17:59:59+05:30", "2026-11-02"),
    ("2026-11-03T18:00:00+05:30", "2026-11-03"),
    ("2026-11-08T19:00:00+05:30", "2026-11-08"),
    ("2026-11-10T19:00:00+05:30", "2026-11-09"),
    ("2026-11-03T12:30:00+00:00", "2026-11-03"),
])
def test_conservative_freshness_cutoff_timezone_holiday_and_sunday(instant, expected):
    assert str(latest_ready_session(clock(instant)).date()) == expected


@pytest.mark.parametrize("instant", ["2025-12-31T19:00:00+05:30", "2027-01-02T19:00:00+05:30", "2026-01-01T10:00:00+05:30"])
def test_freshness_unknown_outside_coverage(instant):
    assert latest_ready_session(clock(instant)) is None


def test_absence_holiday_unexpected_dates_and_immutability():
    data = dataset(["2026-10-19", "2026-10-21", "2026-10-23", "2026-10-24"])
    before = canonical_bars_bytes(data.bars)
    quality = attach_quality(data, now=clock())
    assert quality["missing_expected_dates"] == ["2026-10-22"]
    assert quality["unexpected_dates"] == ["2026-10-24"]
    assert "2026-10-20" not in quality["missing_expected_dates"]
    assert before == canonical_bars_bytes(data.bars)
    assert not any(w.startswith("No exchange calendar") for w in data.warnings)
    assert any("Calendar review" in w for w in data.warnings)
    assert len(CALENDAR_HASH) == 64
    assert quality["calendar_version"] == CALENDAR_VERSION
    assert passport_for_analysis(data)["data_quality"] == quality
    json.dumps(quality, allow_nan=False)


def test_absent_muhurat_sunday_counts_as_expected_observation():
    q = assess_data_quality(dataset(["2026-11-06", "2026-11-09"]), now=clock("2026-11-11T19:00:00+05:30"))
    assert q["missing_expected_dates"] == ["2026-11-08"]
    assert q["lag_sessions"] == 1  # Nov 10 is a CM holiday


def test_freshness_and_internal_coverage_are_independent():
    data = dataset(["2026-10-30", "2026-11-03"])
    q = assess_data_quality(data, now=clock())
    assert q["lag_sessions"] == 0
    assert q["missing_expected_dates"] == ["2026-11-02"]


def test_replay_does_not_reveal_hidden_source_rows_or_compare_to_today():
    full = dataset(["2026-10-29", "2026-10-30", "2026-11-02", "2026-11-03"])
    sliced = replace(full, bars=full.bars.iloc[:2].copy(), metadata=dict(full.metadata))
    q = attach_quality(sliced, now=clock(), replay=True)
    assert "Historical replay" in q["freshness"]
    assert q["missing_expected_dates"] == []
    assert q["observed_rows"] == 2
    assert sliced.metadata["source_rows"] == 4
    assert q["latest_ready_session"] is None


@pytest.mark.parametrize("exchange,synthetic", [("Unknown", False), ("BSE", False), ("NSE", True)])
def test_other_or_synthetic_data_not_misclassified(exchange, synthetic):
    q = assess_data_quality(dataset(["2026-10-20", "2026-10-24"], exchange, synthetic), now=clock())
    assert q["calendar_version"] is None
    assert q["unexpected_dates"] == []


def test_partial_coverage_and_future_observations_are_explicit():
    q = assess_data_quality(dataset(["2025-12-31", "2026-01-02", "2026-11-04"]), now=clock())
    assert q["unsupported_dates"] == ["2025-12-31"]
    assert q["future_dates"] == ["2026-11-04"]
    assert "Partial" in q["calendar_status"]
    assert q["lag_sessions"] is None


def test_same_day_pre_cutoff_does_not_claim_feed_finality():
    q = assess_data_quality(dataset(["2026-11-02", "2026-11-03"]), now=clock("2026-11-03T16:00:00+05:30"))
    assert "beyond" in q["freshness"]
    assert any("finality is unverified" in n for n in q["notes"])


def test_quality_upload_ui_surfaces_absent_and_non_session_dates(monkeypatch):
    import streamlit as st
    dates = ["19-Oct-2026", "21-Oct-2026", "23-Oct-2026", "24-Oct-2026"]
    raw = pd.DataFrame({"DATE": dates, "SERIES": "EQ", "OPEN": 100, "HIGH": 102, "LOW": 98,
                        "CLOSE": 101, "VOLUME": 1000, "LTP": 101})
    uploaded = BytesIO(raw.to_csv(index=False).encode())
    uploaded.name = "Quote-Equity-DEMO-EQ-19-10-2026-24-10-2026.csv"
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: uploaded)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    app.radio[0].set_value("Upload daily data").run()
    app.checkbox[0].check().run()
    assert not app.exception
    assert any("Calendar checks found" in w.value for w in app.warning)
    tables = [d.value for d in app.dataframe if "Check" in d.value.columns]
    assert len(tables) == 1
    assert "2026-10-22" in tables[0]["Dates (first 20)"].tolist()
    assert any("Data quality checks" in m.value for m in app.markdown)
