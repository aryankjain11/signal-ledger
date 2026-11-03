"""Explicit split/bonus normalization on a declared raw daily dataset.

No event inference or automatic exchange fetch. Research units are not an order
execution model; dividends/mergers/rights and share-accounting backtests are separate.
"""
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO, StringIO
import csv
import json
import re

import numpy as np
import pandas as pd

from .data import validate_daily
from .datasets import canonical_bars_bytes
from .models import ValidatedData

ACTION_VERSION = "split-bonus/1"
FIELDS = ["action_id", "symbol", "ex_date", "known_on", "action_type", "shares_before", "shares_after", "source"]


@dataclass(frozen=True)
class ActionLedger:
    events: pd.DataFrame
    source_sha256: str


def read_action_ledger(content: bytes) -> ActionLedger:
    if len(content) > 1024 * 1024:
        raise ValueError("Action ledger exceeds the 1 MB limit.")
    try:
        text = content.decode("utf-8-sig")
        header = next(csv.reader(StringIO(text)), [])
        header = [h.strip().casefold() for h in header]
        if len(header) != len(set(header)) or set(header) != set(FIELDS):
            raise ValueError("Action ledger needs unique columns: " + ", ".join(FIELDS))
        frame = pd.read_csv(StringIO(text), dtype=str, keep_default_na=False, nrows=1001)
    except (UnicodeError, csv.Error, pd.errors.ParserError) as exc:
        raise ValueError("Expected a UTF-8 corporate-action CSV ledger.") from exc
    if frame.empty or len(frame) > 1000:
        raise ValueError("Action ledger must contain between 1 and 1,000 events.")
    frame.columns = header
    frame = frame[FIELDS].apply(lambda c: c.str.strip())
    frame["symbol"] = frame.symbol.str.upper()
    frame["action_type"] = frame.action_type.str.lower()
    if not frame.symbol.str.fullmatch(r"[A-Z0-9&._/-]{1,80}").all():
        raise ValueError("Every action needs an explicit valid instrument symbol/research label.")
    if not frame.action_id.str.fullmatch(r"[A-Za-z0-9._-]{1,80}").all() or frame.action_id.duplicated().any():
        raise ValueError("Action IDs must be nonblank, unique and use letters, numbers, dot, underscore or hyphen.")
    if not frame.source.str.len().between(1, 500).all():
        raise ValueError("Every action needs a source reference (1–500 characters).")
    if not frame.action_type.isin(["split", "bonus"]).all():
        raise ValueError("Only split and bonus events are supported. Dividend, rights, merger and other events require separate review.")
    for name in ("ex_date", "known_on"):
        if not frame[name].str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
            raise ValueError("Action dates must use explicit YYYY-MM-DD session dates.")
        try:
            frame[name] = pd.to_datetime(frame[name], format="%Y-%m-%d", errors="raise")
        except ValueError as exc:
            raise ValueError("Action ledger contains an invalid date.") from exc
    for name in ("shares_before", "shares_after"):
        if not frame[name].str.fullmatch(r"\d+").all():
            raise ValueError("Share ratios must be positive whole-number counts before and after the event.")
        frame[name] = pd.to_numeric(frame[name], errors="coerce")
        if not frame[name].between(1, 1_000_000).all():
            raise ValueError("Share ratio counts must be between 1 and 1,000,000.")
    ratio = frame.shares_after / frame.shares_before
    if (ratio == 1).any() or not ratio.between(0.0001, 10000).all():
        raise ValueError("An action needs a nontrivial share ratio between 0.0001 and 10,000.")
    if ((frame.action_type == "bonus") & (ratio <= 1)).any():
        raise ValueError("Bonus shares_after means total resulting shares and must exceed shares_before.")
    # Simultaneous events need an explicit composite specification, not a guessed order.
    if frame.duplicated(["symbol", "ex_date"]).any():
        raise ValueError("Multiple events on the same symbol/ex-date require review; do not silently combine them.")
    return ActionLedger(frame.sort_values(["symbol", "ex_date", "action_id"]).reset_index(drop=True), sha256(content).hexdigest())


def apply_actions(data: ValidatedData, ledger: ActionLedger, *, as_of, adjusted=False):
    """Use only declared events known and effective by the visible daily cutoff.

    All OHLC are divided by resulting shares per old share before each ex-date;
    volume is multiplied by the same ratio. Ex-date bars remain in their new units.
    """
    if data.metadata.get("corporate_actions"):
        raise ValueError("This dataset already has an action audit; start again from its original raw input.")
    cutoff = pd.Timestamp(as_of)
    if cutoff.tz is not None or cutoff != cutoff.normalize():
        raise ValueError("Action cutoff must be a timezone-free daily session date.")
    if cutoff not in data.bars.index:
        raise ValueError("Action cutoff must be an observed session in the input dataset.")
    symbol = data.metadata.get("instrument", {}).get("symbol", "").strip().upper()
    if not symbol:
        raise ValueError("Attach an explicit instrument passport before applying an action ledger.")
    selected = ledger.events.loc[ledger.events.symbol.eq(symbol)]
    if selected.empty:
        raise ValueError("No actions match this dataset's symbol/research label; check instrument identity.")
    if adjusted and data.metadata.get("adjustment_basis") not in {"Unadjusted OHLC", "Synthetic example"}:
        raise ValueError("To prevent double adjustment, declare the original input Unadjusted OHLC before using adjusted research.")
    raw = data.bars.loc[:cutoff].copy()
    known = selected.loc[selected.known_on <= cutoff]
    eligible = known.loc[known.ex_date <= cutoff]
    effective = eligible.loc[(eligible.ex_date > raw.index[0]) & (eligible.ex_date <= raw.index[-1])]
    if not effective.ex_date.isin(raw.index).all():
        raise ValueError("An effective action ex-date has no observed bar. Review the session/source before adjusting.")
    factors = pd.Series(1.0, index=raw.index, name="price_factor")
    rows = []
    for event in known.itertuples(index=False):
        status = "Announced; not effective by cutoff" if event.ex_date > cutoff else "Before/at visible range start; no earlier bars to change"
        if event.action_id in set(effective.action_id):
            status = "Applied to pre-ex-date bars" if adjusted else "Effective event; original prices retained"
            if adjusted:
                factors.loc[factors.index < event.ex_date] /= event.shares_after / event.shares_before
        rows.append({"action_id": event.action_id, "symbol": event.symbol, "action_type": event.action_type,
            "ex_date": event.ex_date.date().isoformat(), "known_on": event.known_on.date().isoformat(),
            "shares_before": int(event.shares_before), "shares_after": int(event.shares_after),
            "source": event.source, "status": status})
    if not np.isfinite(factors.to_numpy()).all() or (factors <= 0).any():
        raise ValueError("Cumulative action factors overflow or underflow; review the action ledger.")
    transformed = raw.copy()
    transformed[["open", "high", "low", "close"]] = raw[["open", "high", "low", "close"]].mul(factors, axis=0)
    transformed["volume"] = raw.volume / factors
    if not np.isfinite(transformed.to_numpy()).all() or (transformed[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("Cumulative action factors overflow or underflow; review the action ledger.")
    validated = validate_daily(transformed.reset_index(), data.source_hash, min_rows=1)
    metadata = deepcopy(data.metadata)
    metadata.pop("data_quality", None)
    audit = {"version": ACTION_VERSION, "mode": "Split/bonus adjusted research" if adjusted else "Original prices with action audit",
        "cutoff": cutoff.date().isoformat(), "ledger_sha256": ledger.source_sha256,
        "basis": "Visible cutoff share units; pre-ex-date OHLC divided and share volume multiplied by resulting-share ratio",
        "known_on_semantics": "User-declared first knowable date; available at that day's close, not independently verified",
        "known_events": rows, "effective_events_in_range": len(effective),
        "applied_events": len(effective) if adjusted else 0,
        "original_visible_sha256": sha256(canonical_bars_bytes(raw)).hexdigest(),
        "result_visible_sha256": sha256(canonical_bars_bytes(transformed)).hexdigest(),
        "source_dataset_id": data.metadata.get("dataset_id"),
        "scope": "User-supplied split/bonus ledger only; completeness, origin and listing continuity unverified. No dividends/total returns or execution accounting."}
    metadata["corporate_actions"] = audit
    metadata["research_view_id"] = sha256(json.dumps({"source_dataset_id": audit["source_dataset_id"],
        "version": ACTION_VERSION, "mode": audit["mode"], "cutoff": audit["cutoff"],
        "ledger_sha256": audit["ledger_sha256"], "result_sha256": audit["result_visible_sha256"]}, sort_keys=True).encode()).hexdigest()
    # Preserve source dataset identity/basis; describe the transformed analysis separately.
    metadata["analysis_price_basis"] = audit["mode"]
    metadata["original_data_warnings"] = list(data.warnings)
    inherited = [w for w in data.warnings if not (adjusted and w.startswith("A close-to-close move exceeds 25%"))]
    warnings = validated.warnings + [w for w in inherited if w not in validated.warnings]
    warnings.append(audit["scope"])
    restricted = adjusted or len(effective) > 0
    if restricted:
        metadata["execution_restriction"] = "Sizing, executable trade plans and backtests are unavailable for this action-audited range until share-accounting execution is implemented."
        transformed.attrs["execution_restriction"] = metadata["execution_restriction"]
        warnings.append(metadata["execution_restriction"])
    result = ValidatedData(transformed, warnings, data.source_hash, metadata)
    factor_table = pd.DataFrame({"price_multiplier": factors, "volume_multiplier": 1 / factors})
    return result, factor_table


def synthetic_action_files():
    """Original six-session fixture with split and bonus; no real observations."""
    dates = ["2026-06-01", "2026-06-02", "2026-06-03", "2026-06-04", "2026-06-05", "2026-06-08"]
    close = pd.Series([200., 204., 102., 104., 52., 54.])
    bars = pd.DataFrame({"date": dates, "symbol": "DEMOCA", "open": close, "high": close + 2,
                         "low": close - 2, "close": close, "volume": [1000, 1000, 2000, 2000, 4000, 4000]})
    actions = pd.DataFrame([
        ["demo-split", "DEMOCA", "2026-06-03", "2026-05-29", "split", 1, 2, "Synthetic fixture"],
        ["demo-bonus", "DEMOCA", "2026-06-05", "2026-06-04", "bonus", 1, 2, "Synthetic fixture"],
    ], columns=FIELDS)
    return bars.to_csv(index=False).encode(), actions.to_csv(index=False).encode()
