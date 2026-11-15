"""Original invented prices in the observed export schema; never bundle user data."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.data import load_bars

NAME = "Quote-Equity-DEMO-ALPHA-EQ-01-01-2024-31-01-2024.csv"


def quote_frame():
    return pd.DataFrame({
        "DATE": ["04-Jan-2024", "03-Jan-2024", "02-Jan-2024"], "SERIES": ["EQ"] * 3,
        "OPEN": ["1,234.50", "1,220.00", "1,210.00"],
        "HIGH": ["1,250.00", "1,245.00", "1,230.00"],
        "LOW": ["1,230.00", "1,215.00", "1,200.00"],
        "PREV. CLOSE": ["1,235.00", "1,220.00", "1,199.00"],
        "LTP": ["1,248.00", "1,234.00", "1,219.00"],
        "CLOSE": ["1,240.00", "1,235.00", "1,220.00"],
        "VWAP": ["1,239.30"] * 3, "52 WEEK HIGH": ["1,300.00"] * 3,
        "52 WEEK LOW": ["900.00"] * 3, "VOLUME": ["23,34,553", "1,234,567", "100000"],
        "VALUE": ["28,95,00,000"] * 3, "NO. OF  TRADES": ["20,000"] * 3})


def payload(frame=None):
    return (quote_frame() if frame is None else frame).to_csv(index=False).encode()


def test_original_download_shape_exact_mapping_sorting_and_hash():
    content = payload()
    data = load_bars(content, NAME)
    assert data.bars.index.strftime("%Y-%m-%d").tolist() == ["2024-01-02", "2024-01-03", "2024-01-04"]
    assert data.bars.iloc[-1].tolist() == pytest.approx([1234.5, 1250, 1230, 1240, 2334553])
    assert list(data.bars) == ["open", "high", "low", "close", "volume"]
    assert data.source_hash == sha256(content).hexdigest()
    assert data.metadata["file_symbol"] == "DEMO-ALPHA"
    assert data.metadata["file_series"] == "EQ"
    assert "filename" in data.metadata["symbol_basis"]
    assert any("sorted" in w for w in data.warnings)


def test_header_whitespace_bom_long_price_names_and_excel_match():
    frame = quote_frame().rename(columns={"OPEN": "Open Price", "HIGH": "High Price", "LOW": "Low Price", "CLOSE": "Close Price", "VOLUME": "Total Traded Quantity"})
    frame.columns = ["  " + c + "  " for c in frame.columns]
    csv = load_bars(b"\xef\xbb\xbf" + payload(frame), NAME)
    stream = BytesIO()
    frame.to_excel(stream, index=False)
    xlsx = load_bars(stream.getvalue(), NAME.replace(".csv", ".xlsx"))
    pd.testing.assert_frame_equal(csv.bars, xlsx.bars)
    assert csv.bars.iloc[-1].volume == 2334553


@pytest.mark.parametrize("value", ["12,34", "1,2345", "1,2,345", "1,,234", "-", "NaN", "inf", "", "₹1,234"])
def test_missing_or_malformed_numbers_not_silently_repaired(value):
    frame = quote_frame()
    frame.loc[0, "OPEN"] = value
    with pytest.raises(ValueError, match="missing or invalid"):
        load_bars(payload(frame), NAME)


@pytest.mark.parametrize("value", ["01/02/2024", "31-Feb-2024", "02-Foo-2024", "2024-01-02T09:15:00"])
def test_bad_or_ambiguous_dates_rejected(value):
    frame = quote_frame()
    frame.loc[0, "DATE"] = value
    with pytest.raises(ValueError, match="date|Date"):
        load_bars(payload(frame), NAME)


@pytest.mark.parametrize("mutate,match", [
    (lambda f: f.assign(SERIES=["EQ", "BE", "EQ"]), "EQ series"),
    (lambda f: f.assign(DATE=["02-Jan-2024"] * 3), "Duplicate"),
    (lambda f: f.assign(HIGH="100.00"), "Invalid OHLC"),
    (lambda f: f.assign(VOLUME="123.5"), "whole number"),
    (lambda f: f.drop(columns="VOLUME"), "VOLUME"),
    (lambda f: f.assign(**{"Open Price": "1234"}), "ambiguous duplicate"),
    (lambda f: f.assign(SYMBOL=["ALPHA", "BETA", "ALPHA"]), "one nonblank symbol"),
    (lambda f: f.assign(SYMBOL="BETA"), "conflicts"),
])
def test_price_identity_and_schema_guards(mutate, match):
    with pytest.raises(ValueError, match=match):
        load_bars(payload(mutate(quote_frame())), NAME)


def test_duplicate_raw_csv_headers_rejected_before_pandas_mangles_names():
    content = payload().replace(b"DATE,SERIES,OPEN,", b"DATE,SERIES,OPEN, open ,")
    with pytest.raises(ValueError, match="unique"):
        load_bars(content, NAME)


def test_renamed_download_keeps_identity_unknown_and_duplicate_suffix_supported():
    renamed = load_bars(payload(), "my-data.csv")
    assert "file_symbol" not in renamed.metadata
    duplicate = load_bars(payload(), NAME.replace(".csv", " (1).csv"))
    assert duplicate.metadata["file_symbol"] == "DEMO-ALPHA"
    with pytest.raises(ValueError, match="filename series"):
        load_bars(payload(), NAME.replace("-EQ-", "-BE-"))


def test_generic_csv_still_requires_iso_dates_and_unformatted_numbers():
    generic = quote_frame()[["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"]]
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        load_bars(payload(generic), "generic.csv")


def test_direct_nse_download_ui_auto_label_close_and_passport(monkeypatch):
    import streamlit as st
    uploaded = BytesIO(payload())
    uploaded.name = NAME
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: uploaded)
    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(root / "app.py"), default_timeout=30).run()
    next(r for r in app.radio if r.label == "Data source").set_value("Upload daily data").run()
    app.checkbox[0].check().run()
    assert not app.exception
    assert any("NSE stock-history format detected" in s.value for s in app.success)
    assert app.metric[0].value == "1,240.00"  # CLOSE differs from LTP
    assert any("DEMO-ALPHA" in c.value for c in app.caption)
    assert any("NSE security-history export" in m.value for m in app.markdown)
    assert any(e.label == "How this upload was interpreted" for e in app.expander)
    assert any("Fewer than 60" in m.value for m in app.markdown)
