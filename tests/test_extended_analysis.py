import numpy as np
import pandas as pd
import pytest

from quant_engine.analysis import analyze
from quant_engine.data import load_bars
from quant_engine.indicators import indicators
from quant_engine.market_read import market_read
from quant_engine.models import Settings, ValidatedData
from quant_engine.patterns import swings
from quant_engine.research import head_shoulders

EXTENDED = ["adx_14", "plus_di_14", "minus_di_14", "supertrend", "supertrend_dir", "donchian_high_20",
            "keltner_upper", "squeeze_on", "cmf_20", "mfi_14", "vwap_20", "williams_r_14", "cci_20",
            "stoch_rsi_14", "hv_20", "atr_pct", "high_52w", "low_52w"]


def synthetic():
    from pathlib import Path
    return load_bars((Path(__file__).parents[1] / "data" / "synthetic_daily.csv").read_bytes(), "s.csv")


def path_bars(points, seed=3):
    """Linear interpolation between (bar, price) anchors with a small, deterministic wiggle."""
    xs, ys = zip(*points)
    close = np.interp(np.arange(xs[-1] + 1), xs, ys)
    rng = np.random.default_rng(seed)
    close = close + rng.normal(0, .05, len(close))
    open_ = (np.r_[close[0], close[:-1]] + close) / 2
    high = np.maximum(open_, close) + .3
    low = np.minimum(open_, close) - .3
    index = pd.bdate_range("2024-01-01", periods=len(close))
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close,
                         "volume": 1e5}, index=index)


def test_extended_indicators_are_causal():
    bars = synthetic().bars
    full = indicators(bars)
    cut = indicators(bars.iloc[:400])
    for column in EXTENDED:
        a, b = full[column].iloc[:400], cut[column]
        assert ((a - b).abs().fillna(0) < 1e-9).all() and (a.isna() == b.isna()).all(), column


def test_extended_indicator_ranges():
    f = indicators(synthetic().bars).iloc[300:]
    assert f.adx_14.between(0, 100).all() and f.mfi_14.between(0, 100).all()
    assert f.williams_r_14.between(-100, 0).all() and f.cmf_20.between(-1, 1).all()
    assert set(f.supertrend_dir.unique()) <= {1.0, -1.0}
    above = f.supertrend_dir == 1
    assert (f.supertrend[above] <= f.high[above] + 1e-9).all()
    assert (f.donchian_high_20 >= f.high).all() and (f.keltner_upper > f.keltner_lower).all()


def test_head_and_shoulders_lifecycle_and_frozen_neckline():
    # left shoulder 110, head 120, right shoulder 110, neckline ~100, then breakdown to 85
    bars = indicators(path_bars([(0, 95), (30, 100), (40, 110), (50, 100), (60, 120), (70, 100.5),
                                 (80, 110), (90, 101), (105, 85), (120, 86)]))
    events = head_shoulders(bars, swings(bars, 3))
    hs = [e for e in events if e["name"] == "Head and shoulders"]
    assert hs, "expected a head-and-shoulders detection"
    developing = next(e for e in hs if e["status"] == "Developing")
    confirmed = next(e for e in hs if e["status"] == "Confirmed neckline break")
    assert developing["direction"] == -1 and developing["formed_at"] <= developing["detected_at"]
    assert confirmed["index"] > developing["index"]
    assert bars.close.iloc[confirmed["index"]] < confirmed["level"]
    assert confirmed["measured_target"] < confirmed["level"]
    # Knowable only after right-shoulder confirmation: the right shoulder is the last anchor.
    assert pd.Timestamp(developing["coordinates"][-1][0]) < pd.Timestamp(developing["detected_at"])
    # No repainting: running on data truncated at detection yields the same developing event.
    cut = bars.iloc[:developing["index"] + 1]
    again = [e for e in head_shoulders(cut, swings(cut, 3)) if e["id"] == developing["id"]]
    assert again and again[0]["status"] == "Developing" and again[0]["neckline"] == pytest.approx(developing["neckline"])


def test_inverse_head_and_shoulders_and_rejection_of_lopsided_shapes():
    inverse = indicators(path_bars([(0, 110), (30, 105), (40, 95), (50, 105), (60, 85), (70, 104.5),
                                    (80, 95), (90, 104), (105, 120), (120, 119)]))
    events = head_shoulders(inverse, swings(inverse, 3))
    assert any(e["name"] == "Inverse head and shoulders" and e["status"] == "Confirmed neckline break" for e in events)
    # Shoulders 15 apart (far more than 1 ATR) are not a head-and-shoulders.
    lopsided = indicators(path_bars([(0, 95), (30, 100), (40, 125), (50, 100), (60, 130), (70, 100.5),
                                     (80, 108), (90, 101), (105, 85), (120, 86)]))
    assert not [e for e in head_shoulders(lopsided, swings(lopsided, 3)) if e["name"] == "Head and shoulders"]


def test_market_read_one_vote_per_family_and_no_probability():
    analysis = analyze(synthetic(), Settings())
    read = market_read(analysis)
    families = [f["family"] for f in read["families"]]
    assert len(families) == len(set(families))
    voting = [f for f in read["families"] if f["votes"]]
    assert read["bullish"] + read["bearish"] + read["neutral"] == sum(f["signal"] is not None for f in voting)
    assert read["probability"] is None and "not a probability" in read["basis"]
    assert read["verdict"] in {"Bullish", "Bearish", "Mixed / conflicting", "Insufficient evidence", "Leaning bullish", "Leaning bearish"}
    for level in read["levels"]:
        assert level["distance_pct"] is not None


def test_market_read_insufficient_on_short_history():
    bars = synthetic().bars.iloc[:25]
    read = market_read(analyze(ValidatedData(bars, [], "x"), Settings()))
    assert read["verdict"] == "Insufficient evidence"


def test_market_read_trending_series():
    up = indicators(path_bars([(0, 100), (300, 180)]))
    data = ValidatedData(up[["open", "high", "low", "close", "volume"]], [], "up")
    read = market_read(analyze(data, Settings()))
    trend = next(f for f in read["families"] if f["family"] == "Trend")
    assert trend["signal"] == 1
