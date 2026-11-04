from dataclasses import asdict
import json

import numpy as np
import pandas as pd

from . import __version__
from .data import completed_weeks
from .indicators import indicators
from .models import Analysis, Settings, ValidatedData, ResearchRules
from .research import breakout_events, contextual_candles, chart_formations, momentum_analysis, RULE_VERSION
from .patterns import candle_events, double_patterns, market_structure, support_resistance, swings
from .strategy import current_setup
from .datasets import passport_for_analysis


def analyze(data: ValidatedData, settings: Settings, rules: ResearchRules | None = None) -> Analysis:
    if len(data.bars) < 3:
        raise ValueError("Analysis needs at least three completed daily observations; a smaller import is preview-only.")
    rules = rules or ResearchRules()
    frame = indicators(data.bars)
    if data.metadata.get("execution_restriction"):
        frame.attrs["execution_restriction"] = data.metadata["execution_restriction"]
    pivots = swings(frame, settings.pivot_window)
    trend, structure = market_structure(pivots)
    bar = frame.iloc[-1]
    evidence = [structure]
    if pd.notna(bar.ema_50):
        evidence.append(f"Close {bar.close:.4f} is {'above' if bar.close > bar.ema_50 else 'at/below'} EMA50 {bar.ema_50:.4f}.")
    if pd.notna(bar.rsi_14):
        evidence.append(f"RSI14 is {bar.rsi_14:.2f}; describes recent momentum, not a reversal guarantee.")
    if pd.notna(bar.relative_volume):
        evidence.append(f"Volume is {bar.relative_volume:.2f} times the previous 20 sessions' mean.")
    weeks = completed_weeks(data.bars)
    if len(weeks) >= 20:
        weekly_mean = float(weeks.close.iloc[-20:].mean())
        weekly_close = float(weeks.close.iloc[-1])
        weekly = {"status": "Available", "completed_weeks": len(weeks),
                  "last_session": weeks.index[-1].date().isoformat(),
                  "close": weekly_close, "sma_20": weekly_mean,
                  "context": "Above weekly SMA20" if weekly_close > weekly_mean else "At/below weekly SMA20"}
    else:
        weekly = {"status": "Insufficient data", "completed_weeks": len(weeks),
                  "required_weeks": 20, "context": "Weekly SMA20 unavailable"}
    warnings = data.warnings + [
        "The latest calendar week is excluded conservatively from weekly context.",
        "Pattern rules are heuristic geometric definitions; predictive performance has not been validated.",
        "Corporate actions, spreads, news, event risk and actual order-book liquidity are not verified."]
    momentum, divergences = momentum_analysis(frame, pivots)
    events = (candle_events(frame) + contextual_candles(frame, rules) + double_patterns(frame, pivots)
              + breakout_events(frame, rules) + chart_formations(frame, pivots) + divergences)
    return Analysis(frame, pivots, events,
                    support_resistance(frame, pivots), trend, structure, evidence, weekly,
                    current_setup(frame, settings), warnings, momentum,
                    {"version": RULE_VERSION, **asdict(rules)})


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return json_safe(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def run_evidence(analysis: Analysis, data: ValidatedData, settings: Settings,
                 symbol: str, adjustment: str) -> dict:
    return json_safe({"engine_version": __version__, "symbol": symbol,
                      "source_sha256": data.source_hash, "adjustment_status": adjustment,
                      "data_passport": passport_for_analysis(data) if data.metadata.get("dataset_id") else None,
                      "bar_semantics": "User-declared completed daily session bars; timezone-free dates",
                      "settings": asdict(settings), "rows": len(analysis.frame),
                      "start": analysis.frame.index[0], "as_of": analysis.frame.index[-1],
                      "trend": analysis.trend, "evidence": analysis.evidence,
                      "latest_values": analysis.frame.iloc[-1].to_dict(),
                      "pivots": [asdict(p) for p in analysis.pivots],
                      "events": analysis.events, "zones": analysis.zones,
                      "research_rules": analysis.rules, "momentum": analysis.momentum,
                      "weekly": analysis.weekly, "setup": analysis.setup,
                      "warnings": analysis.warnings, "probability": None})


def report_markdown(analysis: Analysis, symbol: str, adjustment: str) -> str:
    last = analysis.frame.index[-1].date().isoformat()
    parts = [f"# {symbol} · daily research report", f"As of {last} · {len(analysis.frame)} sessions",
             f"Adjustment declaration: {adjustment}", f"## {analysis.trend}"]
    parts.extend(f"- {e}" for e in analysis.evidence)
    weekly = analysis.weekly
    weekly_text = f"{weekly['context']}. {weekly['completed_weeks']} prior calendar weeks available."
    if "sma_20" in weekly:
        weekly_text += f" Last completed-week close {weekly['close']:.4f}; weekly SMA20 {weekly['sma_20']:.4f}."
    parts += ["\n## Weekly context", weekly_text, "\n## Baseline setup", analysis.setup["status"]]
    setup = analysis.setup
    if "reference_entry" in setup:
        parts += [setup["entry_condition"], setup["note"],
                  "| Parameter | Reference value |\n| --- | --- |\n"
                  f"| Entry including slippage | {setup['reference_entry']:.4f} |\n"
                  f"| Stop threshold | {setup['reference_stop']:.4f} |\n"
                  f"| Target threshold | {setup['reference_target']:.4f} |\n"
                  f"| Gross reward / risk | {setup['gross_reward_risk']:.2f} |\n"
                  f"| Net reward / risk estimate | {setup['net_reward_risk_at_reference']:.2f} |\n"
                  f"| Whole-share quantity | {setup['quantity']} |\n"
                  f"| Planned loss including costs | {setup['planned_loss_with_costs']:.2f} |\n"
                  f"| Maximum holding sessions | {setup['max_hold_sessions']} |", setup["invalidation"]]
    else:
        parts.append(setup.get("reason", "No executable baseline setup."))
    parts += ["\n## Support and resistance"]
    if analysis.zones:
        parts.extend(f"- {z['role']}: {z['low']:.4f}–{z['high']:.4f}; {z['pivot_count']} clustered pivots."
                     for z in analysis.zones)
    else:
        parts.append("No zones met the clustered-pivot criteria.")
    parts += ["\n## Recent candlestick observations"]
    candles = [e for e in analysis.events if e.get("family") == "candle" or ("family" not in e and not e["name"].startswith("Double"))][-10:]
    parts.extend(f"- {e['name']} on {e['detected_at']}; geometry only." for e in candles)
    if not candles:
        parts.append("No supported candle geometry detected.")
    parts += ["\n## Chart pattern event history"]
    pattern_events = [e for e in analysis.events if e["name"].startswith("Double")]
    parts.extend(f"- {e['name']} · {e['status']} · formed {e['formed_at']} · known {e['detected_at']} · neckline {e['neckline']:.4f}"
                 for e in pattern_events[-20:])
    if not pattern_events:
        parts.append("No double-top/bottom geometries met the configured criteria.")
    parts += ["\n## Breakout, chart and divergence observations"]
    expanded = sorted([e for e in analysis.events if e.get("family") in {"breakout", "chart", "momentum"}], key=lambda e: (e["detected_at"], e["id"]))[-20:]
    parts.extend(f"- {e['name']} · {e['status']} · known {e['detected_at']}. {e['evidence']}" for e in expanded)
    if not expanded:
        parts.append("No additional supported observations in this slice.")
    parts += ["\n## Momentum context"] + analysis.momentum.get("interpretation", [])
    parts.append(f"Research definition: {analysis.rules}. Descriptive events do not change the existing baseline strategy or supply calibrated probabilities.")
    parts += ["\n## Limitations"] + [f"- {w}" for w in analysis.warnings]
    parts += ["\nNo calibrated success probability is available. Research and decision support only; no guaranteed outcomes."]
    return "\n\n".join(parts)
