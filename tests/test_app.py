from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_demo_replay_and_backtest_flow():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "Price structure, with evidence."
    app.button(key="run_baseline").click().run()
    assert not app.exception
    assert any(m.label == "Completed trades" for m in app.metric)
    app.select_slider[0].set_value("2023-01-10").run()
    assert not app.exception
    assert any("Warming up" in str(m.value) for m in app.metric)


def test_upload_requires_data_and_completed_bar_confirmation():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Upload daily data").run()
    assert not app.exception
    assert any("Upload one symbol" in i.value for i in app.info)


def test_valid_upload_requires_confirmation_then_analyzes(monkeypatch):
    from io import BytesIO
    import streamlit as st

    uploaded = BytesIO((ROOT / "data" / "synthetic_daily.csv").read_bytes())
    uploaded.name = "uploaded.csv"
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: uploaded)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Upload daily data").run()
    assert any("Confirm that all" in w.value for w in app.warning)
    app.checkbox[0].check().run()
    assert not app.exception
    assert len(app.metric) == 4


def test_invalid_upload_shows_error_without_crashing(monkeypatch):
    from io import BytesIO
    import streamlit as st

    uploaded = BytesIO(b"date,open,high,low,close,volume\n2024-01-01,100,50,99,101,100\n2024-01-02,100,50,99,101,100\n2024-01-03,100,50,99,101,100\n")
    uploaded.name = "bad.csv"
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: uploaded)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Upload daily data").run()
    app.checkbox[0].check().run()
    assert not app.exception
    assert any("Invalid OHLC" in e.value for e in app.error)
