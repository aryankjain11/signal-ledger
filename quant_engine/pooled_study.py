"""Pattern outcomes pooled across a watchlist.

Each stock is studied with the unchanged single-stock engine (`event_study.build_study`):
same detectors, same knowledge-date timing, same overlap thinning, and the same
non-event baseline taken from *that stock's own* ordinary days. Only then are the
per-event outcomes stacked. Pooling adds two dependence problems, which are measured
and reported, never hidden:

* date clustering: a market-wide move makes many stocks print the "same" pattern on the
  same day, so the effective sample is closer to the number of distinct dates;
* concentration: one stock can supply most of a cohort's events.

The interval offered for the baseline difference is a bootstrap that resamples whole
event *dates* (all stocks' events on a date move together), so market-wide days are not
counted as independent evidence. It is descriptive, not a significance test, and only
shown when there are enough matched events and distinct dates.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .event_study import StudyRules, build_study

MIN_MATCHED_FOR_INTERVAL = 30
MIN_DATES_FOR_INTERVAL = 20
BOOTSTRAP_DRAWS = 1000
POOLED_COLUMNS = ["cohort", "horizon", "events", "stocks", "distinct_dates", "top_stock", "top_stock_share",
                  "mean_return", "median_return", "q25_return", "q75_return", "positive_fraction",
                  "median_mfe", "median_mae", "matched_events", "matched_event_mean", "matched_baseline_mean",
                  "difference_from_baseline", "difference_low", "difference_high", "incomplete", "sample_note"]


@dataclass
class PooledResult:
    outcomes: pd.DataFrame
    summary: pd.DataFrame
    by_stock: pd.DataFrame
    audit: dict


def date_clustered_interval(values: pd.Series, dates: pd.Series, draws: int = BOOTSTRAP_DRAWS,
                            level: float = 0.90, seed: int = 7):
    """Percentile interval for the mean of `values`, resampling whole dates with replacement."""
    frame = pd.DataFrame({"v": values.to_numpy(), "d": dates.to_numpy()}).dropna()
    groups = frame.groupby("d").v.agg(["sum", "count"])
    if len(groups) < 2:
        return None, None
    sums, counts = groups["sum"].to_numpy(), groups["count"].to_numpy()
    rng = np.random.default_rng(seed)
    picks = rng.integers(0, len(groups), size=(draws, len(groups)))
    means = sums[picks].sum(axis=1) / counts[picks].sum(axis=1)
    tail = (1 - level) / 2
    return float(np.quantile(means, tail)), float(np.quantile(means, 1 - tail))


def _note(n, dates, share):
    if n == 0:
        return "No complete outcomes"
    if n < 30 or dates < 20:
        return "Small sample: read as anecdote"
    if share > 0.4:
        return "One stock supplies >40% of events"
    if dates < 0.5 * n:
        return "Heavily date-clustered"
    return "Descriptive; dependence remains"


def summarize_pooled(outcomes: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if outcomes.empty:
        return pd.DataFrame(columns=POOLED_COLUMNS)
    for (cohort, horizon), group in outcomes.groupby(["cohort", "horizon"], sort=True):
        done = group.loc[group.outcome_state.eq("Complete")]
        values = done.forward_return
        n = len(values)
        per_stock = done.symbol.value_counts()
        share = float(per_stock.iloc[0] / n) if n else 0.0
        matched = done.loc[done.control_mean.notna()]
        low = high = None
        dates = done.known_at.nunique()
        if len(matched) >= MIN_MATCHED_FOR_INTERVAL and matched.known_at.nunique() >= MIN_DATES_FOR_INTERVAL:
            low, high = date_clustered_interval(matched.difference_from_control_mean, matched.known_at)
        rows.append({
            "cohort": cohort, "horizon": int(horizon), "events": n, "stocks": int(per_stock.size),
            "distinct_dates": int(dates), "top_stock": per_stock.index[0] if n else "", "top_stock_share": share,
            "mean_return": values.mean(), "median_return": values.median(),
            "q25_return": values.quantile(.25) if n else np.nan, "q75_return": values.quantile(.75) if n else np.nan,
            "positive_fraction": (values > 1e-12).mean() if n else np.nan,
            "median_mfe": done.mfe.median(), "median_mae": done.mae.median(),
            "matched_events": len(matched), "matched_event_mean": matched.forward_return.mean(),
            "matched_baseline_mean": matched.control_mean.mean(),
            "difference_from_baseline": matched.difference_from_control_mean.mean(),
            "difference_low": low, "difference_high": high,
            "incomplete": int(group.outcome_state.eq("Incomplete horizon").sum()),
            "sample_note": _note(n, dates, share)})
    return pd.DataFrame(rows, columns=POOLED_COLUMNS)


def pooled_study(stocks: dict, rules: StudyRules | None = None) -> PooledResult:
    """`stocks` maps symbol -> (indicator frame, events, metadata). Cohort filters are applied after pooling."""
    rules = rules or StudyRules()
    per_stock_rules = StudyRules(**{**asdict(rules), "cohorts": ()})
    parts, coverage = [], []
    for symbol, (frame, events, metadata) in stocks.items():
        try:
            result = build_study(frame, events, per_stock_rules, metadata)
        except ValueError as exc:
            coverage.append({"symbol": symbol, "sessions": len(frame), "included_events": 0, "error": str(exc)})
            continue
        coverage.append({"symbol": symbol, "sessions": len(frame), "first": frame.index[0].date().isoformat(),
                         "last": frame.index[-1].date().isoformat(),
                         "included_events": int(result.audit["included_occurrences"]), "error": ""})
        if not result.outcomes.empty:
            parts.append(result.outcomes.assign(symbol=symbol))
    outcomes = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
    if rules.cohorts and not outcomes.empty:
        outcomes = outcomes.loc[outcomes.cohort.isin(rules.cohorts)].reset_index(drop=True)
    summary = summarize_pooled(outcomes)
    by_stock = pd.DataFrame()
    if not outcomes.empty:
        done = outcomes.loc[outcomes.outcome_state.eq("Complete")]
        by_stock = (done.groupby(["cohort", "horizon", "symbol"]).agg(
            events=("forward_return", "size"), mean_return=("forward_return", "mean"),
            difference_from_baseline=("difference_from_control_mean", "mean")).reset_index())
    audit = {
        "method": "Single-stock engine per symbol (own detectors, timing, thinning and own non-event baseline), then pooled.",
        "stocks_requested": len(stocks), "stocks_with_events": int(outcomes.symbol.nunique()) if not outcomes.empty else 0,
        "coverage": coverage, "rules": asdict(rules),
        "interval": (f"{int(BOOTSTRAP_DRAWS)} date-clustered bootstrap draws, 90% percentile interval of the mean "
                     f"event-minus-baseline difference; shown only with >= {MIN_MATCHED_FOR_INTERVAL} matched events "
                     f"on >= {MIN_DATES_FOR_INTERVAL} distinct dates. Descriptive, not a significance test."),
        "limits": ("Watchlist is today's index membership applied to the past (survivorship bias). Returns are gross "
                   "price moves without costs or dividends. Overlap thinning is within each stock; events on the same "
                   "date in different stocks are correlated, which the date-clustered interval accounts for only "
                   "partially. Many cohorts × horizons are shown, so some will look notable by chance."),
    }
    return PooledResult(outcomes, summary, by_stock, audit)
