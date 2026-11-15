"""Immutable portable strategy records; never mix saved output with new inputs."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json

from .analysis import json_safe, run_evidence
from .datasets import canonical_bars_bytes
from .retest_strategy import STRATEGY_VERSION, simulate_retest

EXECUTION_FIELDS = ("capital", "risk_fraction", "fee_bps", "slippage_bps", "participation")


def retest_identity(analysis, data, settings, rules, symbol, adjustment):
    columns = ["open", "high", "low", "close", "volume", "ema_50", "atr_14", "relative_volume"]
    evidence = {"strategy": STRATEGY_VERSION, "rules": asdict(rules),
        "execution": {key: getattr(settings, key) for key in EXECUTION_FIELDS},
        "source_sha256": data.source_hash, "symbol": symbol, "price_basis": adjustment,
        "visible_features_sha256": sha256(canonical_bars_bytes(analysis.frame[columns])).hexdigest(),
        "dataset_id": data.metadata.get("dataset_id"), "research_view_id": data.metadata.get("research_view_id"),
        "execution_restriction": data.metadata.get("execution_restriction", ""),
        "frame_restriction": analysis.frame.attrs.get("execution_restriction", "")}
    return sha256(json.dumps(json_safe(evidence), sort_keys=True, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class SavedRetest:
    request_id: str
    record_json: str


def save_retest(analysis, data, settings, rules, symbol, adjustment):
    if data.metadata.get("execution_restriction"):
        raise ValueError(data.metadata["execution_restriction"])
    result = simulate_retest(analysis.frame, settings, rules)
    identity = retest_identity(analysis, data, settings, rules, symbol, adjustment)
    bars = analysis.frame[["open", "high", "low", "close", "volume"]].reset_index()
    bars = bars.rename(columns={bars.columns[0]: "date"})
    record = json_safe({"schema": "breakout-retest-run/1", "strategy_version": STRATEGY_VERSION,
        "request_id": identity, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "rules": asdict(rules), "execution": {key: getattr(settings, key) for key in EXECUTION_FIELDS},
        "analysis": run_evidence(analysis, data, settings, symbol, adjustment),
        "metrics": result.metrics, "current": result.current,
        "candidates": result.candidates.to_dict("records"), "candidate_columns": result.candidates.columns.tolist(),
        "events": result.events.to_dict("records"), "event_columns": result.events.columns.tolist(),
        "trades": result.trades.to_dict("records"), "trade_columns": result.trades.columns.tolist(),
        "equity": result.equity.reset_index().to_dict("records"), "bars": bars.to_dict("records"),
        "execution_conventions": {"entry": "One next-open attempt after later close-confirmed retest",
            "stop": "Frozen min(retest low, breakout level) minus frozen ATR buffer",
            "ambiguity": "Stop first if both barriers touched, including entry bar",
            "cutoff": "Open positions liquidated; pending setups remain pending",
            "scope": "Long only; blended per-side fees/adverse slippage; no orders, settlement, dividends or partial fills"}})
    return SavedRetest(identity, json.dumps(record, indent=2, allow_nan=False))
