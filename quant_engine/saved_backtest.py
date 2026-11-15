"""Immutable in-session backtest records; display changes do not alter past calculations."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json

from .analysis import json_safe, run_evidence
from .datasets import canonical_bars_bytes
from .strategy import backtest

BASELINE_VERSION = "long-breakout/1"


def backtest_identity(analysis, data, settings, symbol, adjustment):
    columns = ["open", "high", "low", "close", "volume", "ema_50", "atr_14", "relative_volume"]
    inputs = {"strategy": BASELINE_VERSION, "settings": asdict(settings),
        "source_sha256": data.source_hash, "symbol": symbol, "price_basis": adjustment,
        "visible_features_sha256": sha256(canonical_bars_bytes(analysis.frame[columns])).hexdigest(),
        "research_view_id": data.metadata.get("research_view_id"),
        "execution_restriction": data.metadata.get("execution_restriction", ""),
        "dataset_id": data.metadata.get("dataset_id")}
    return sha256(json.dumps(json_safe(inputs), sort_keys=True, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class SavedBacktest:
    request_id: str
    record_json: str
    trades_csv: str


def save_backtest(analysis, data, settings, symbol, adjustment):
    if data.metadata.get("execution_restriction"):
        raise ValueError(data.metadata["execution_restriction"])
    result = backtest(analysis.frame, settings)
    identity = backtest_identity(analysis, data, settings, symbol, adjustment)
    record = json_safe({"schema": "saved-backtest/1", "request_id": identity,
        "strategy_version": BASELINE_VERSION, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "analysis": run_evidence(analysis, data, settings, symbol, adjustment),
        "metrics": result.metrics, "trades": result.trades.to_dict("records"),
        "equity": result.equity.reset_index().to_dict("records")})
    return SavedBacktest(identity, json.dumps(record, indent=2, allow_nan=False), result.trades.to_csv(index=False))
