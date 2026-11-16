from io import BytesIO
from pathlib import Path
import json

import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from quant_engine.analysis import json_safe
from quant_engine.comparison import compare_stocks, synthetic_pair
from quant_engine.data import load_bars


def bars(returns, initial=100):
    close = initial * np.cumprod(np.r_[1, 1 + np.array(returns)])
    return pd.DataFrame({"close": close}, index=pd.bdate_range("2026-01-01", periods=len(close)))


@pytest.mark.parametrize("sign", [1, -1])
def test_exact_return_correlation_and_common_base_normalization(sign):
    returns = [.01, -.02, .03, -.01, .005, .04, -.02, .01, -.005, .02, .015]
    a, b = bars(returns), bars(np.array(returns) * sign, 300)
    pair = compare_stocks(a, b, window=5)
    assert pair.summary["pearson_return_correlation"] == pytest.approx(sign)
    assert pair.summary["spearman_return_correlation"] == pytest.approx(sign)
    assert pair.indexed.iloc[0].tolist() == [100, 100]
    assert pair.summary["paired_intervals"] == len(returns)
    assert pair.rolling.iloc[:4].isna().all()
    assert pair.rolling.iloc[4:].to_numpy() == pytest.approx(np.full(len(returns) - 4, sign))


def test_missing_date_excludes_mismatched_return_interval_without_forward_fill():
    a = bars([.01, .02, -.01, .03, -.02, .01, .01, -.03, .02, .01, .03])
    b = a.drop(a.index[2])
    before = b.copy()
    pair = compare_stocks(a, b)
    assert len(pair.prices) == len(b)
    assert a.index[3] not in pair.returns.index
    assert pair.summary["excluded_unmatched_return_intervals"] == 1
    assert pair.summary["only_A_dates"] == 1
    pd.testing.assert_frame_equal(b, before)
    assert all(pair.returns.interval_start < pair.returns.index)


def test_flat_returns_and_short_samples_show_unavailable_not_zero_correlation():
    flat = bars([0] * 12)
    result = compare_stocks(flat, flat)
    assert result.summary["pearson_return_correlation"] is None
    assert "Undefined" in result.summary["correlation_status"]
    assert result.rolling.isna().all()
    short = compare_stocks(bars([.01, .02]), bars([.02, .03]))
    assert short.summary["pearson_return_correlation"] is None
    assert "Insufficient" in short.summary["correlation_status"]
    json.dumps(json_safe(short.summary), allow_nan=False)


def test_drawdown_return_and_relative_performance_arithmetic():
    pair = compare_stocks(bars([.1, -.2, .25]), bars([0, 0, 0]))
    assert pair.summary["metrics"][0]["period_price_return"] == pytest.approx(.1)
    assert pair.summary["metrics"][0]["observed_date_max_drawdown"] == pytest.approx(-.2)
    assert pair.summary["relative_performance_A_over_B"] == pytest.approx(1.1)


def test_nonoverlap_duplicate_dates_and_bad_window_are_rejected():
    a = bars([.01] * 20)
    b = a.copy()
    b.index = b.index + pd.Timedelta(days=300)
    with pytest.raises(ValueError, match="common observation"):
        compare_stocks(a, b)
    with pytest.raises(ValueError, match="unique"):
        compare_stocks(pd.concat([a, a.iloc[:1]]), a)
    with pytest.raises(ValueError, match="window"):
        compare_stocks(a, a, window=2)


def test_synthetic_pair_deterministic_and_finite():
    assert synthetic_pair() == synthetic_pair()
    a, b = [load_bars(content, "demo.csv").bars for content in synthetic_pair()]
    pair = compare_stocks(a, b)
    assert pair.summary["paired_intervals"] == 149
    assert -1 < pair.summary["pearson_return_correlation"] < 1
    json.dumps(json_safe(pair.summary), allow_nan=False)


def test_comparison_page_synthetic_pair_and_period_replay():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=45).run()
    app.radio(key="workspace_page").set_value("Compare stocks").run()
    assert not app.exception and app.title[0].value == "Compare stocks"
    assert any(m.label == "Matched return intervals" and m.value == "149" for m in app.metric)
    app.number_input(key="correlation_window").set_value(10).run()
    assert not app.exception
    app.select_slider(key="comparison_period").set_value(("2026-01-01", "2026-01-07")).run()
    assert not app.exception
    assert any(m.label == "Return correlation (Pearson)" and m.value == "Unavailable" for m in app.metric)
    app.select_slider(key="comparison_period").set_value(("2026-01-01", "2026-01-02")).run()
    assert not app.exception
    assert any("At least three" in i.value for i in app.info)


def test_two_native_nse_uploads_work_without_manual_cleanup(monkeypatch):
    import streamlit as st
    def uploader(*args, **kwargs):
        ticker = "ALPHA" if kwargs.get("key") == "compare_upload_A" else "BETA"
        content = b'DATE,SERIES,OPEN,HIGH,LOW,CLOSE,VOLUME,LTP\n04-Jan-2026,EQ,"1,000","1,020",990,"1,010","1,00,000","1,015"\n05-Jan-2026,EQ,"1,010","1,030","1,000","1,020","1,10,000","1,025"\n06-Jan-2026,EQ,"1,020","1,040","1,010","1,030","1,20,000","1,035"\n'
        uploaded = BytesIO(content)
        uploaded.name = f"Quote-Equity-{ticker}-EQ-01-01-2026-31-01-2026.csv"
        return uploaded
    monkeypatch.setattr(st, "file_uploader", uploader)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=45).run()
    app.radio(key="workspace_page").set_value("Compare stocks").run()
    app.radio(key="comparison_mode").set_value("Upload two stocks").run()
    app.checkbox(key="compare_complete").check().run()
    assert not app.exception
    assert any("ALPHA versus BETA" in c.value for c in app.caption)
    assert any("same bytes" in w.value for w in app.warning)
