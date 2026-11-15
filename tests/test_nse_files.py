"""Independent acceptance cases using invented reports; no real exchange data."""
from dataclasses import replace
from hashlib import sha256
from io import BytesIO
import json
import zipfile

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.analysis import analyze, run_evidence
from quant_engine.datasets import canonical_bars_bytes, passport_for_analysis
from quant_engine.models import Settings
from quant_engine.nse_files import read_reports, synthetic_reports

HEADER = "TradDt,Sgmt,Src,TckrSymb,SctySrs,ISIN,OpnPric,HghPric,LwPric,ClsPric,TtlTradgVol"


def report(date="2024-01-02", **changes):
    values = dict(zip(HEADER.split(","), [date, "CM", "NSE", "ALPHA", "EQ", "ZZ0000000001", "100", "105", "98", "103", "1000"]))
    values.update(changes)
    return (",".join(values) + "\n" + ",".join(values.values()) + "\n").encode()


def archive(name, content):
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(name, content)
    return stream.getvalue()


def test_synthetic_report_exact_prices_identity_and_determinism():
    payload = synthetic_reports()
    assert payload == synthetic_reports()
    bundle = read_reports([("demo.zip", payload)])
    assert len(bundle.reports) == 80
    assert [i["symbol"] for i in bundle.instruments()] == ["DEMOALPHA", "DEMOBETA"]
    data = bundle.select("DEMOALPHA", is_synthetic=True)
    assert len(data.bars) == 80
    assert data.bars.iloc[0].tolist() == pytest.approx([98.8, 100.8, 96.8, 99.3, 100000])
    assert data.metadata["instrument"]["isin"] == "ZZ0000000001"
    assert data.metadata["dataset_id"] != bundle.select("DEMOBETA", is_synthetic=True).metadata["dataset_id"]
    assert data.metadata["is_synthetic"]


def test_input_order_stable_and_zip_plain_csv_equivalent():
    files = [("a.csv", report()), ("b.csv", report("2024-01-03")), ("c.csv", report("2024-01-04"))]
    a = read_reports(files).select("ALPHA")
    b = read_reports(list(reversed(files))).select("ALPHA")
    assert a.metadata["dataset_id"] == b.metadata["dataset_id"]
    zipped = BytesIO()
    with zipfile.ZipFile(zipped, "w") as z:
        for name, content in files:
            z.writestr(name, content)
    c = read_reports([("all.zip", zipped.getvalue())]).select("ALPHA")
    pd.testing.assert_frame_equal(a.bars, c.bars)
    assert a.metadata["normalized_sha256"] == c.metadata["normalized_sha256"]
    assert a.source_hash != c.source_hash  # raw containers differ


def test_trade_date_used_instead_of_business_date_and_non_eq_excluded():
    content = report(BizDt="2024-01-05")
    content += report(TckrSymb="ALPHA", SctySrs="BE").splitlines()[1] + b",2024-01-05\n"
    data = read_reports([("a.csv", content)]).select("ALPHA")
    assert str(data.bars.index[0].date()) == "2024-01-02"
    assert len(data.bars) == 1


def test_absent_security_recorded_without_filling_or_calendar_claim():
    bundle = read_reports([("a.csv", report()), ("b.csv", report("2024-01-03", TckrSymb="BETA", ISIN="ZZ0000000002"))])
    data = bundle.select("ALPHA")
    assert len(data.bars) == 1
    assert data.metadata["coverage"]["report_dates_without_security"] == ["2024-01-03"]
    assert "Not configured" in data.metadata["calendar_status"]


@pytest.mark.parametrize("changed", [{}, {"ClsPric": "104"}])
def test_duplicate_sessions_never_silently_merged(changed):
    with pytest.raises(ValueError, match="duplicate"):
        read_reports([("a.csv", report()), ("b.csv", report(**changed))])


def test_identity_change_requires_review():
    bundle = read_reports([("a.csv", report()), ("b.csv", report("2024-01-03", ISIN="ZZ0000000002"))])
    with pytest.raises(ValueError, match="multiple ISINs"):
        bundle.select("ALPHA")
    with pytest.raises(ValueError, match="not present"):
        bundle.select("MISSING")


@pytest.mark.parametrize("change,match", [
    ({"ISIN": ""}, "ISIN"), ({"ISIN": "invalid"}, "ISIN"),
    ({"TckrSymb": ""}, "ticker"), ({"Sgmt": "FO"}, "capital-market"),
    ({"Src": "BSE"}, "capital-market"), ({"TradDt": "02/01/2024"}, "YYYY-MM-DD"),
    ({"TradDt": "2024-02-30"}, "invalid calendar"), ({"SsnId": "I1"}, "Interim"),
])
def test_bad_identity_session_and_source(change, match):
    with pytest.raises(ValueError, match=match):
        read_reports([("a.csv", report(**change))])


@pytest.mark.parametrize("name,match", [
    ("BhavCopy_NSE_CM_0_0_0_20240103_F_0000.csv", "disagrees"),
    ("BhavCopy_NSE_CM_0_0_0_20240102_P_0000.csv", "Provisional"),
])
def test_filename_consistency_inside_zip(name, match):
    with pytest.raises(ValueError, match=match):
        read_reports([("reports.zip", archive(name, report()))])


@pytest.mark.parametrize("content,match", [
    (b"date,close\n2024-01-02,100\n", "missing UDiFF"),
    ((HEADER + ",TRADDT\n").encode(), "duplicate column"),
    (report() + report("2024-01-03").splitlines()[1] + b"\n", "exactly one"),
    (report(SctySrs="BE"), "No EQ"),
])
def test_invalid_report_shapes(content, match):
    with pytest.raises(ValueError, match=match):
        read_reports([("a.csv", content)])


@pytest.mark.parametrize("change,match", [({"HghPric": "90"}, "Invalid OHLC"), ({"TtlTradgVol": "-1"}, "negative"), ({"ClsPric": "nan"}, "missing|finite")])
def test_selected_prices_validated(change, match):
    with pytest.raises(ValueError, match=match):
        read_reports([("a.csv", report(**change))]).select("ALPHA")


@pytest.mark.parametrize("name", ["../a.csv", "/a.csv", "C:/a.csv", "nested.zip"])
def test_unsafe_archive_members_rejected(name):
    with pytest.raises(ValueError, match="plain CSV"):
        read_reports([("a.zip", archive(name, report()))])


def test_symlink_archive_rejected():
    stream = BytesIO()
    with zipfile.ZipFile(stream, "w") as z:
        info = zipfile.ZipInfo("link.csv")
        info.create_system = 3
        info.external_attr = 0o120777 << 16
        z.writestr(info, report())
    with pytest.raises(ValueError, match="plain CSV"):
        read_reports([("a.zip", stream.getvalue())])


@pytest.mark.parametrize("name,content,match", [("a.zip", b"broken", "corrupt"), ("a.xlsx", b"x", "CSV or ZIP")])
def test_unsupported_containers(name, content, match):
    with pytest.raises(ValueError, match=match):
        read_reports([(name, content)])


@pytest.mark.parametrize("limit", ["MAX_FILE_BYTES", "MAX_INPUT_BYTES", "MAX_EXPANDED_BYTES", "MAX_TOTAL_ROWS"])
def test_import_resource_limits(monkeypatch, limit):
    import quant_engine.nse_files as module
    monkeypatch.setattr(module, limit, 1)
    content = report() + report(TckrSymb="BETA", ISIN="ZZ0000000002").splitlines()[1] + b"\n"
    with pytest.raises(ValueError):
        read_reports([("a.csv", content)])


def test_preview_and_replay_passport_hashes_match_exports_and_evidence():
    preview = read_reports([("a.csv", report())]).select("ALPHA")
    with pytest.raises(ValueError, match="preview-only"):
        analyze(preview, Settings())
    full = read_reports([("a.zip", synthetic_reports())]).select("DEMOALPHA", is_synthetic=True)
    sliced = replace(full, bars=full.bars.iloc[:40].copy())
    passport = passport_for_analysis(sliced)
    assert passport["source_rows"] == 80 and passport["analyzed_rows"] == 40
    assert passport["dataset_id"] == full.metadata["dataset_id"]
    assert passport["analyzed_normalized_sha256"] == sha256(canonical_bars_bytes(sliced.bars)).hexdigest()
    assert passport["analyzed_normalized_sha256"] != passport["normalized_sha256"]
    evidence = run_evidence(analyze(sliced, Settings()), sliced, Settings(), "DEMOALPHA", "Synthetic example")
    assert evidence["data_passport"] == passport
    json.dumps(evidence, allow_nan=False)


def test_report_walkthrough_ui_and_security_switch():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(root / "app.py"), default_timeout=30).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Synthetic NSE report walkthrough").run()
    assert not app.exception
    assert len(app.metric) == 4
    assert app.selectbox(key="report_instrument").value == "DEMOALPHA|EQ"
    app.selectbox(key="report_instrument").set_value("DEMOBETA|EQ").run()
    assert not app.exception
    assert any("DEMOBETA" in m.value for m in app.markdown)
    next(r for r in app.radio if r.label == "Data source").set_value("Import NSE daily reports").run()
    assert not app.exception
    assert any("Upload NSE CM" in i.value for i in app.info)


def test_real_report_upload_confirmation_and_preview(monkeypatch):
    from pathlib import Path
    import streamlit as st
    uploaded = BytesIO(report())
    uploaded.name = "a.csv"
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: [uploaded])
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Import NSE daily reports").run()
    assert any("Confirm that all" in w.value for w in app.warning)
    app.checkbox[0].check().run()
    assert not app.exception
    assert any("at least three" in w.value for w in app.warning)
    assert not app.metric


@pytest.mark.parametrize("content,expected", [(synthetic_reports(), "metrics"), (b"corrupt", "error")])
def test_uploaded_zip_analysis_or_friendly_failure(monkeypatch, content, expected):
    from pathlib import Path
    import streamlit as st
    uploaded = BytesIO(content)
    uploaded.name = "reports.zip"
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: [uploaded])
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Import NSE daily reports").run()
    app.checkbox[0].check().run()
    assert not app.exception
    if expected == "metrics":
        assert len(app.metric) == 4
    else:
        assert any("Report import could not continue" in e.value for e in app.error)


def test_lesson_two_available_in_education():
    from pathlib import Path
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    app.selectbox(key="workspace_page").set_value("Education and Concepts").run()
    assert not app.exception
    assert any("Lesson 2" in e.label for e in app.expander)
    assert any("analyzed_normalized_sha256" in m.value for m in app.markdown)
