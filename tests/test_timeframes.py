import numpy as np
import pandas as pd

from quant_engine.timeframes import completed_months, multi_timeframe, read_timeframe


def bars(n, start="2020-01-01", slope=0.2, seed=1):
    index = pd.bdate_range(start, periods=n)
    rng = np.random.default_rng(seed)
    close = 100 + slope * np.arange(n) + rng.normal(0, .3, n)
    open_ = np.r_[close[0], close[:-1]]
    return pd.DataFrame({"open": open_, "high": np.maximum(open_, close) + .5, "low": np.minimum(open_, close) - .5,
                         "close": close, "volume": 1e5}, index=index)


def test_completed_months_drop_the_forming_month_and_aggregate_correctly():
    b = bars(70, "2026-01-01")  # Jan..early April
    months = completed_months(b)
    assert months.index[-1].month < b.index[-1].month
    jan = b[b.index.month == 1]
    first = months.iloc[0]
    assert first.open == jan.open.iloc[0] and first.close == jan.close.iloc[-1]
    assert first.high == jan.high.max() and first.low == jan.low.min() and first.volume == jan.volume.sum()


def test_no_forming_period_leaks_into_higher_timeframes():
    b = bars(1200)
    full = multi_timeframe(b)
    # Changing the bars of the current (forming) week/month must not change higher-timeframe reads.
    tweaked = b.copy()
    tweaked.iloc[-2:, :4] = tweaked.iloc[-2:, :4] * 0.5
    tweaked["high"] = tweaked[["open", "high", "close"]].max(axis=1)
    tweaked["low"] = tweaked[["open", "low", "close"]].min(axis=1)
    again = multi_timeframe(tweaked)
    for name in ("Monthly", "Weekly"):
        a = next(r for r in full["reads"] if r["timeframe"] == name)
        c = next(r for r in again["reads"] if r["timeframe"] == name)
        if a["last_period"] < str(b.index[-6].date()):
            assert a == c


def test_short_history_is_reported_unavailable_not_guessed():
    out = multi_timeframe(bars(120))
    monthly = next(r for r in out["reads"] if r["timeframe"] == "Monthly")
    assert monthly["status"] == "Unavailable" and monthly["signal"] is None
    assert read_timeframe("Daily", bars(30), 3)["signal"] is None


def test_alignment_language():
    from quant_engine.timeframes import alignment_verdict as av
    up = multi_timeframe(bars(1500, slope=0.3))
    assert up["higher_signal"] == 1 and up["alignment"].startswith("Aligned")
    assert av(1, 1, -1)[0] == 1 and av(1, 1, -1)[1].startswith("Counter-trend")
    assert av(-1, -1, 0)[1].startswith("Daily is sideways inside a higher-timeframe downtrend")
    assert av(1, 0, -1) == (0, av(1, 0, -1)[1]) and "pausing on the weekly" in av(1, 0, -1)[1]
    assert "conflict" in av(1, -1, 1)[1] and av(1, -1, 1)[0] == 0
    assert av(None, -1, -1)[0] == -1 and av(None, None, 1)[0] is None
    assert av(0, 0, 1)[1].startswith("Higher timeframes are sideways")
