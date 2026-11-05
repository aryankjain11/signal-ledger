"""Descriptive, single-stock pattern outcomes. No fills, statistical tests or forecasts."""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json

import numpy as np
import pandas as pd

from .analysis import json_safe
from .datasets import canonical_bars_bytes

STUDY_VERSION = "pattern-outcomes/1"
TREND_LABELS = ("Above EMA50", "At/below EMA50", "Unavailable EMA50")
VOLUME_LABELS = ("RVOL >= 1.2", "RVOL < 1.2", "Unavailable RVOL")
SUMMARY_COLUMNS = ["cohort", "horizon", "selected", "complete", "incomplete", "action_excluded",
                   "mean_return", "median_return", "q25_return", "q75_return", "positive_fraction",
                   "zero_count", "median_mfe", "median_mae", "matched_events", "matched_event_mean",
                   "matched_baseline_mean", "difference_from_baseline", "sample_note"]


@dataclass(frozen=True)
class StudyRules:
    horizons: tuple[int, ...] = (1, 5, 10, 20)
    reference: str = "Next observed open"
    perspective: str = "Pattern direction"
    overlap: str = "Thin within cohort"
    cohorts: tuple[str, ...] = ()
    trend: str = "All"
    volume: str = "All"
    start: str | None = None
    end: str | None = None
    min_controls: int = 5

    def __post_init__(self):
        if (not isinstance(self.horizons, tuple) or not 1 <= len(self.horizons) <= 8
                or any(type(h) is not int or not 1 <= h <= 252 for h in self.horizons)
                or tuple(sorted(set(self.horizons))) != self.horizons):
            raise ValueError("Use 1–8 distinct, increasing integer horizons from 1 to 252 observations.")
        if self.reference not in {"Next observed open", "Detection close"}:
            raise ValueError("Unknown price reference.")
        if self.perspective not in {"Pattern direction", "Upward price change"}:
            raise ValueError("Unknown outcome perspective.")
        if self.overlap not in {"Thin within cohort", "Keep all"}:
            raise ValueError("Unknown overlap policy.")
        if not isinstance(self.cohorts, tuple) or any(not isinstance(c, str) for c in self.cohorts):
            raise ValueError("Cohort selection must be a tuple of names.")
        if self.trend not in ("All", *TREND_LABELS) or self.volume not in ("All", *VOLUME_LABELS):
            raise ValueError("Unknown trend or volume filter.")
        if type(self.min_controls) is not int or not 1 <= self.min_controls <= 100:
            raise ValueError("Minimum matching controls must be 1–100.")
        for date in (self.start, self.end):
            if date is not None:
                value = pd.Timestamp(date)
                if value.tz is not None or value != value.normalize() or value.date().isoformat() != date:
                    raise ValueError("Event dates must use YYYY-MM-DD.")
        if self.start and self.end and self.start > self.end:
            raise ValueError("Event date range is reversed.")


@dataclass
class StudyResult:
    occurrences: pd.DataFrame
    outcomes: pd.DataFrame
    controls: pd.DataFrame
    summary: pd.DataFrame
    audit: dict
    rules: dict
    run_id: str


def _validate(frame):
    if (not isinstance(frame.index, pd.DatetimeIndex) or frame.index.tz is not None
            or not frame.index.is_monotonic_increasing or not frame.index.is_unique
            or frame.index.hasnans or not frame.index.equals(frame.index.normalize())):
        raise ValueError("Study bars need unique, increasing, timezone-free daily dates.")
    if frame.empty or not {"open", "high", "low", "close", "volume", "ema_50", "relative_volume"} <= set(frame):
        raise ValueError("Supply analyzed OHLC bars with EMA50 and relative volume.")
    prices = frame[["open", "high", "low", "close"]].to_numpy(dtype=float)
    if (not np.isfinite(prices).all() or (prices <= 0).any()
            or (frame.high < frame[["open", "low", "close"]].max(axis=1)).any()
            or (frame.low > frame[["open", "high", "close"]].min(axis=1)).any()):
        raise ValueError("Study OHLC prices must be finite, positive and internally consistent.")
    for column in ("ema_50", "relative_volume"):
        if np.isinf(frame[column].to_numpy(dtype=float)).any():
            raise ValueError("Context values must be finite or unavailable.")
    if not np.isfinite(frame.volume.to_numpy(dtype=float)).all() or (frame.volume < 0).any():
        raise ValueError("Study volume must be finite and nonnegative.")


def _contexts(frame):
    trend = np.where(frame.ema_50.isna(), TREND_LABELS[2],
                     np.where(frame.close > frame.ema_50, TREND_LABELS[0], TREND_LABELS[1]))
    volume = np.where(frame.relative_volume.isna(), VOLUME_LABELS[2],
                      np.where(frame.relative_volume >= 1.2, VOLUME_LABELS[0], VOLUME_LABELS[1]))
    return pd.DataFrame({"trend_context": trend, "volume_context": volume,
        "close_at_detection": frame.close, "ema50_at_detection": frame.ema_50,
        "rvol_at_detection": frame.relative_volume}, index=frame.index)


def occurrence_ledger(frame, events):
    """Retain transitions separately, including excluded diagnostics. Never select final state."""
    _validate(frame)
    context = _contexts(frame)
    rows, seen = [], {}
    for event in events:
        i = event.get("index")
        if type(i) is not int or not 0 <= i < len(frame):
            raise ValueError("An event knowledge index is outside the visible bars.")
        date = frame.index[i].date().isoformat()
        if event.get("detected_at") != date or not event.get("formed_at") or event["formed_at"] > date:
            raise ValueError("Event knowledge date/index or formation chronology is inconsistent.")
        formed = pd.Timestamp(event["formed_at"])
        if formed.tz is not None or formed != formed.normalize() or formed.date().isoformat() != event["formed_at"]:
            raise ValueError("Event formation dates must use YYYY-MM-DD.")
        for key in ("id", "name", "status"):
            if not isinstance(event.get(key), str) or not event[key]:
                raise ValueError("Events need non-empty identity, name and state.")
        family = event.get("family", "chart" if event["name"].startswith("Double") else "candle")
        if family not in {"breakout", "chart", "candle", "momentum"}:
            raise ValueError("Unsupported event family.")
        direction = event.get("direction", 0)
        if event["status"] == "Confirmed upward break":
            direction = 1
        elif event["status"] == "Confirmed downward break":
            direction = -1
        elif "direction" not in event:
            direction = 1 if event["name"].startswith("Bullish") else -1 if event["name"].startswith("Bearish") else 0
        if type(direction) is not int or direction not in {-1, 0, 1}:
            raise ValueError("Event direction must be -1, 0 or 1.")
        key = json.dumps([event["id"], event["status"], date], separators=(",", ":"))
        serialized = json.dumps(json_safe(event), sort_keys=True, allow_nan=False)
        duplicate = key in seen
        if duplicate and seen[key] != serialized:
            raise ValueError("Conflicting duplicate event transition.")
        seen[key] = serialized
        diagnostic = event["status"].startswith(("Failed", "Expired", "Invalidated"))
        reason = "Duplicate transition" if duplicate else "Diagnostic lifecycle state" if diagnostic else ""
        rows.append({"event_key": key, "formation_id": event["id"], "family": family,
                     "name": event["name"], "state": event["status"], "direction": direction,
                     "cohort": f"{family} | {event['name']} | {event['status']} | {direction:+d}",
                     "formed_at": event["formed_at"], "known_at": date, "index": i,
                     "rule_version": event.get("rule_version", "legacy-patterns/1"),
                     **context.iloc[i].to_dict(), "eligible": not reason, "exclusion": reason})
    columns = ["event_key", "formation_id", "family", "name", "state", "direction", "cohort",
               "formed_at", "known_at", "index", "rule_version", "trend_context", "volume_context",
               "close_at_detection", "ema50_at_detection", "rvol_at_detection", "eligible", "exclusion"]
    return pd.DataFrame(rows, columns=columns).sort_values(["index", "cohort", "event_key"], kind="stable").reset_index(drop=True)


def _thin(indices, span):
    """Greedy closed-window spacing, before checking whether any outcome is mature."""
    accepted, previous = [], -span - 1
    for index in indices:
        if index > previous + span:
            accepted.append(index)
            previous = index
    return accepted


def _measurements(frame, horizon, direction, reference, raw_actions):
    n = len(frame)
    end_indices = np.arange(n) + horizon
    complete = end_indices < n
    ref = frame.open.shift(-1) if reference == "Next observed open" else frame.close
    future_high = frame.high.shift(-1).iloc[::-1].rolling(horizon, min_periods=horizon).max().iloc[::-1]
    future_low = frame.low.shift(-1).iloc[::-1].rolling(horizon, min_periods=horizon).min().iloc[::-1]
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        change = direction * (frame.close.shift(-horizon) / ref - 1)
        favorable = (future_high / ref - 1) if direction == 1 else (1 - future_low / ref)
        adverse = (future_low / ref - 1) if direction == 1 else (1 - future_high / ref)
    values = np.column_stack([change, favorable, adverse])
    if not np.isfinite(values[complete]).all():
        raise ValueError("Outcome arithmetic overflowed; review the input price scale.")
    end_dates = [frame.index[i] if i < n else pd.NaT for i in end_indices]
    action_crossing = np.zeros(n, dtype=bool)
    for date in raw_actions:
        action_crossing |= (frame.index < date) & (pd.DatetimeIndex(end_dates) >= date)
    state = np.where(~complete, "Incomplete horizon", np.where(action_crossing, "Excluded raw corporate action", "Complete"))
    result = pd.DataFrame({"index": np.arange(n), "horizon": horizon, "measurement_direction": direction,
        "reference_date": frame.index.to_series().shift(-1).to_numpy() if reference == "Next observed open" else frame.index,
        "reference_price": ref.to_numpy(), "exit_date": end_dates, "outcome_state": state,
        "forward_return": change.to_numpy(), "mfe": favorable.clip(lower=0).to_numpy(),
        "mae": adverse.clip(upper=0).to_numpy()})
    result.loc[result.outcome_state.ne("Complete"), ["forward_return", "mfe", "mae"]] = np.nan
    result["calendar_days"] = (pd.to_datetime(result.exit_date) - pd.Series(frame.index)).dt.days
    for key in ("reference_date", "exit_date"):
        result[key] = pd.to_datetime(result[key]).dt.strftime("%Y-%m-%d").where(result[key].notna(), None)
    return result


def build_study(frame, events, rules=None, metadata=None):
    rules, metadata = rules or StudyRules(), metadata or {}
    ledger = occurrence_ledger(frame, events)
    max_h = max(rules.horizons)
    valid_cohorts = set(ledger.loc[ledger.eligible, "cohort"])
    if set(rules.cohorts) - valid_cohorts:
        raise ValueError("A selected cohort is not present in the visible event ledger.")
    chosen = set(rules.cohorts) if rules.cohorts else valid_cohorts
    dates = frame.index.strftime("%Y-%m-%d")
    context = _contexts(frame).reset_index(drop=True)
    period = np.ones(len(frame), dtype=bool)
    if rules.start:
        period &= dates >= rules.start
    if rules.end:
        period &= dates <= rules.end
    # Non-event means no selected eligible event at the decision close. Future events are allowed.
    event_dates = set(ledger.loc[ledger.eligible & ledger.cohort.isin(chosen)
        & (ledger.direction.ne(0) if rules.perspective == "Pattern direction" else True), "index"])
    controls_mask = period & ~np.isin(np.arange(len(frame)), list(event_dates))
    for col, value in (("trend_context", rules.trend), ("volume_context", rules.volume)):
        if value != "All":
            controls_mask &= context[col].eq(value).to_numpy()
    ledger["selection"] = ledger.exclusion
    ledger.loc[ledger.eligible & ~ledger.cohort.isin(chosen), "selection"] = "Cohort filter"
    for idx, row in ledger.iterrows():
        if ledger.at[idx, "selection"]:
            continue
        if rules.perspective == "Pattern direction" and row.direction == 0:
            ledger.at[idx, "selection"] = "Neutral direction"
        elif not period[row["index"]]:
            ledger.at[idx, "selection"] = "Event date filter"
        elif rules.trend != "All" and row.trend_context != rules.trend:
            ledger.at[idx, "selection"] = "Trend filter"
        elif rules.volume != "All" and row.volume_context != rules.volume:
            ledger.at[idx, "selection"] = "Volume filter"
    # Same-cohort same-date geometries provide one price path, regardless of anchor combinations.
    seen = set()
    for idx, row in ledger.loc[ledger.selection.eq("")].iterrows():
        key = (row.cohort, row["index"])
        if key in seen:
            ledger.at[idx, "selection"] = "Same cohort and knowledge date"
        seen.add(key)
    if rules.overlap == "Thin within cohort":
        for _, group in ledger.loc[ledger.selection.eq("")].groupby("cohort", sort=False):
            accepted = set(_thin(group["index"].tolist(), max_h))
            ledger.loc[group.index[~group["index"].isin(accepted)], "selection"] = "Overlapping within cohort"
    selected = ledger.loc[ledger.selection.eq("")].copy()
    ledger.loc[ledger.selection.eq(""), "selection"] = "Included"
    actions = metadata.get("corporate_actions", {})
    raw_actions = [] if actions.get("mode") == "Split/bonus adjusted research" else [
        pd.Timestamp(e["ex_date"]) for e in actions.get("known_events", [])]
    measurements = {}
    def measure(horizon, direction):
        key = (horizon, direction)
        if key not in measurements:
            measurements[key] = _measurements(frame, horizon, direction, rules.reference, raw_actions)
        return measurements[key]
    outcome_parts = []
    for direction, group in selected.groupby("direction", sort=True):
        d = int(direction) if rules.perspective == "Pattern direction" else 1
        for h in rules.horizons:
            outcome_parts.append(group.merge(measure(h, d), on="index", how="left", validate="many_to_one"))
    outcomes = pd.concat(outcome_parts, ignore_index=True) if outcome_parts else pd.DataFrame()
    control_parts = []
    # One auditable pool per pre-known context; reuse across cohorts is disclosed, not multiplied into n.
    for d in sorted(set(outcomes.measurement_direction)) if not outcomes.empty else []:
        for (trend, volume), group in context.loc[controls_mask].groupby(["trend_context", "volume_context"], sort=True):
            anchors = group.index.tolist()
            if rules.overlap == "Thin within cohort":
                anchors = _thin(anchors, max_h)
            for h in rules.horizons:
                measured = measure(h, int(d)).iloc[anchors].copy()
                measured["known_at"] = dates[anchors]
                measured["trend_context"], measured["volume_context"] = trend, volume
                for column in ("close_at_detection", "ema50_at_detection", "rvol_at_detection"):
                    measured[column] = context.loc[anchors, column].to_numpy()
                control_parts.append(measured)
    controls = pd.concat(control_parts, ignore_index=True) if control_parts else pd.DataFrame()
    if not outcomes.empty:
        outcomes["control_count"] = 0
        outcomes["control_mean"] = np.nan
        if not controls.empty:
            keys = ["horizon", "measurement_direction", "trend_context", "volume_context"]
            pools = controls.loc[controls.outcome_state.eq("Complete")].groupby(keys).forward_return.agg(["count", "mean"])
            for idx, row in outcomes.iterrows():
                key = tuple(row[k] for k in keys)
                if key in pools.index:
                    count, mean = pools.loc[key, ["count", "mean"]]
                    outcomes.at[idx, "control_count"] = int(count)
                    if count >= rules.min_controls and row.outcome_state == "Complete":
                        outcomes.at[idx, "control_mean"] = mean
        outcomes["difference_from_control_mean"] = outcomes.forward_return - outcomes.control_mean
    summaries = []
    if not outcomes.empty:
        for (cohort, horizon), group in outcomes.groupby(["cohort", "horizon"], sort=True):
            completed = group.loc[group.outcome_state.eq("Complete")]
            matched = completed.loc[completed.control_mean.notna()]
            values = completed.forward_return
            n = len(values)
            summaries.append({"cohort": cohort, "horizon": int(horizon), "selected": len(group), "complete": n,
                "incomplete": int(group.outcome_state.eq("Incomplete horizon").sum()),
                "action_excluded": int(group.outcome_state.eq("Excluded raw corporate action").sum()),
                "mean_return": values.mean(), "median_return": values.median(),
                "q25_return": values.quantile(.25) if n else np.nan, "q75_return": values.quantile(.75) if n else np.nan,
                "positive_fraction": (values > 1e-12).mean() if n else np.nan,
                "zero_count": int(values.abs().le(1e-12).sum()),
                "median_mfe": completed.mfe.median(), "median_mae": completed.mae.median(),
                "matched_events": len(matched), "matched_event_mean": matched.forward_return.mean(),
                "matched_baseline_mean": matched.control_mean.mean(),
                "difference_from_baseline": matched.difference_from_control_mean.mean(),
                "sample_note": "No complete outcomes" if not n else "Very small sample (<5)" if n < 5 else "Small sample (<30)" if n < 30 else "Descriptive; dependence remains"})
    summary = pd.DataFrame(summaries, columns=SUMMARY_COLUMNS)
    audit = {"version": STUDY_VERSION, "visible_start": dates[0], "visible_end": dates[-1], "bars": len(frame),
        "source_sha256": metadata.get("source_sha256"),
        "visible_ohlcv_sha256": sha256(canonical_bars_bytes(frame[["open", "high", "low", "close", "volume"]])).hexdigest(),
        "received_transitions": len(events), "included_occurrences": len(selected),
        "selection_counts": ledger.selection.value_counts().to_dict(), "max_horizon": max_h,
        "candidate_control_anchors_before_spacing": int(controls_mask.sum()),
        "retained_control_anchor_count": int(controls["index"].nunique()) if not controls.empty else 0,
        "raw_action_ex_dates": [d.date().isoformat() for d in raw_actions],
        "context": "At knowledge close: close > EMA50 versus at/below; RVOL >=1.2 versus below; unavailable separate.",
        "baseline": "Same stock/date window, no selected eligible event at anchor; same trend/RVOL bucket and measurement direction. Matching pools reuse controls; future events allowed. Event-weighted mean of available control means; matched event mean uses identical event coverage.",
        "overlap": "Greedy knowledge indices > previous + largest horizon within each cohort; controls thinned within context pool. Applied before outcome maturity. Different cohorts/pools and controls versus events can overlap; no independence claim.",
        "censoring": "Missing full horizon is incomplete, never a failure or a forced end-of-data exit. No partial MFE/MAE included.",
        "units": "Return, MFE and signed MAE are fractional gross price movements. Directional bearish outcomes negate price changes; they are not executable short returns. No costs, dividends, annualization or compounding across events.",
        "uncertainty": "Descriptive distribution only. Quartiles are outcome dispersion, not confidence intervals. No p-values, independent-sample standard errors or calibrated probabilities.",
        "scope": "Single uploaded stock; no point-in-time universe or held-out validation. Non-event baseline difference is not causal alpha or market-model abnormal return. Calendar horizons count observed bars, not guaranteed exchange sessions."}
    identity = {"version": STUDY_VERSION, "audit": audit, "rules": asdict(rules),
                "occurrences": ledger.to_dict("records"), "metadata": metadata}
    run_id = sha256(json.dumps(json_safe(identity), sort_keys=True, allow_nan=False).encode()).hexdigest()
    return StudyResult(ledger, outcomes, controls, summary, audit, asdict(rules), run_id)


def study_record(result, provenance=None):
    """Portable record; storing this file is distinct from a database/history service."""
    return json_safe({"schema": STUDY_VERSION, "run_id": result.run_id, "rules": result.rules,
        "audit": result.audit, "provenance": provenance or {},
        "occurrences": result.occurrences.to_dict("records"), "outcomes": result.outcomes.to_dict("records"),
        "controls": result.controls.to_dict("records"), "summary": result.summary.to_dict("records")})
