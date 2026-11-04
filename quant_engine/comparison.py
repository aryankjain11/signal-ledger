"""Two-stock comparison on shared observations and genuinely matching return intervals."""
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class PairComparison:
    prices: pd.DataFrame
    indexed: pd.DataFrame
    drawdowns: pd.DataFrame
    returns: pd.DataFrame
    rolling: pd.Series
    summary: dict


def compare_stocks(a, b, *, window=20, minimum_pairs=10):
    if type(window) is not int or not 5 <= window <= 252:
        raise ValueError("Rolling correlation window must be 5–252 matched intervals.")
    if type(minimum_pairs) is not int or minimum_pairs < 3:
        raise ValueError("At least three paired intervals are required for a correlation threshold.")
    for frame in (a, b):
        if frame.empty or not isinstance(frame.index, pd.DatetimeIndex) or not frame.index.is_unique or not frame.index.is_monotonic_increasing or frame.index.tz is not None:
            raise ValueError("Comparison needs validated, sorted, unique timezone-free daily observations.")
        if not np.isfinite(frame.close).all() or (frame.close <= 0).any():
            raise ValueError("Comparison prices must be positive and finite.")
    prices = pd.concat([a.close.rename("Stock A"), b.close.rename("Stock B")], axis=1, join="inner")
    if len(prices) < 2:
        raise ValueError("The two files need at least two common observation dates in the selected period.")
    def returns(frame, name):
        return pd.DataFrame({name: frame.close.pct_change(fill_method=None), f"start_{name}": pd.Series(frame.index, index=frame.index).shift()})
    joined = returns(a, "A").join(returns(b, "B"), how="inner")
    mask = joined.start_A.notna() & joined.start_A.eq(joined.start_B) & np.isfinite(joined.A) & np.isfinite(joined.B)
    paired = joined.loc[mask, ["A", "B", "start_A"]].rename(columns={"start_A": "interval_start"})
    indexed = prices.div(prices.iloc[0]).mul(100)
    if not np.isfinite(indexed.to_numpy()).all():
        raise ValueError("Price normalization overflowed; review input scale and units.")
    drawdowns = indexed.div(indexed.cummax()).sub(1)
    sufficient = len(paired) >= minimum_pairs
    nonconstant = len(paired) >= 2 and paired.A.std(ddof=1) > 1e-12 and paired.B.std(ddof=1) > 1e-12
    corr = float(paired.A.corr(paired.B)) if sufficient and nonconstant else None
    rank_corr = float(paired.A.round(12).rank().corr(paired.B.round(12).rank())) if sufficient and nonconstant else None
    rolling = paired.A.rolling(window, min_periods=window).corr(paired.B).replace([np.inf, -np.inf], np.nan)
    # Explicitly mark effectively constant windows undefined rather than returning numerical noise.
    rolling = rolling.where((paired.A.rolling(window).std() > 1e-12) & (paired.B.rolling(window).std() > 1e-12))
    metrics = []
    for label, name in (("Stock A", "A"), ("Stock B", "B")):
        metrics.append({"stock": label, "period_price_return": float(indexed[label].iloc[-1] / 100 - 1),
            "observed_date_max_drawdown": float(drawdowns[label].min()),
            "matched_interval_volatility": float(paired[name].std(ddof=1)) if len(paired) >= 2 else None})
    summary = {"version": "stock-comparison/1", "common_dates": len(prices), "paired_intervals": len(paired),
        "excluded_unmatched_return_intervals": int((joined.start_A.notna() | joined.start_B.notna()).sum() - len(paired)),
        "only_A_dates": len(a.index.difference(b.index)), "only_B_dates": len(b.index.difference(a.index)),
        "start": str(prices.index[0].date()), "end": str(prices.index[-1].date()), "rolling_window": window,
        "minimum_pairs": minimum_pairs, "rank_return_precision_decimals": 12,
        "pearson_return_correlation": corr, "spearman_return_correlation": rank_corr,
        "correlation_status": "Available" if corr is not None else "Insufficient matched intervals" if not sufficient else "Undefined: effectively constant return series",
        "metrics": metrics, "relative_performance_A_over_B": float(indexed.iloc[-1, 0] / indexed.iloc[-1, 1]),
        "method": "Native observation-to-observation simple returns paired only when BOTH start and end dates match. No filling or bridging unmatched intervals.",
        "limitations": "Descriptive price-return comparison, not total returns, causation, cointegration or a pairs-trading signal. Drawdowns use common observed dates; gaps can conceal path extremes. Volatility is per matched interval, not annualized. Adjustment declarations remain unverified."}
    return PairComparison(prices, indexed, drawdowns, paired, rolling, summary)


def synthetic_pair():
    """Deterministic original fixture; no real stock observations."""
    dates = pd.bdate_range("2026-01-01", periods=150)
    x = np.arange(len(dates))
    ra = .001 + .008 * np.sin(x * .47) + .003 * np.cos(x * .11)
    rb = .0006 + .55 * ra + .005 * np.cos(x * .63)
    frames = []
    for label, initial, r in (("DEMO-A", 100, ra), ("DEMO-B", 180, rb)):
        close = initial * np.cumprod(1 + r)
        opening = np.r_[close[0], close[:-1]]
        frames.append(pd.DataFrame({"date": dates.strftime("%Y-%m-%d"), "symbol": label, "open": opening,
            "high": np.maximum(opening, close) * 1.01, "low": np.minimum(opening, close) * .99,
            "close": close, "volume": 100000 + (x % 17) * 1000}))
    return tuple(frame.to_csv(index=False).encode() for frame in frames)
