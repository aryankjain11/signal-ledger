"""Versioned long breakout/retest hypothesis. See docs/BREAKOUT_RETEST_STRATEGY.md."""
from dataclasses import dataclass
import math

import numpy as np
import pandas as pd

from .models import Settings
from .strategy import size_position

STRATEGY_VERSION = "long-breakout-retest/1"
EVENT_COLUMNS = ["setup_id", "index", "date", "state", "reason", "level", "reference_atr", "stop", "target", "entry"]
CANDIDATE_COLUMNS = ["setup_id", "breakout_index", "breakout_date", "range_start", "range_end", "level",
    "reference_atr", "breakout_close", "breakout_relative_volume", "invalidation_close_below",
    "retest_last_eligible_index", "status", "reason", "decision_date", "retest_index", "retest_date",
    "retest_low", "retest_close", "retest_volume", "stop", "entry_index", "entry_date", "entry",
    "raw_entry_open", "target", "quantity", "planned_risk", "risk_budget", "cash_required", "risk_quantity",
    "cash_quantity", "liquidity_quantity", "net_reward_risk", "exit_date", "entry_attempt_date", "entry_attempt_open", "max_entry_open"]
TRADE_COLUMNS = [*CANDIDATE_COLUMNS, "exit_index", "exit", "raw_exit_reference", "pnl", "entry_fee", "exit_fee",
    "gross_pnl_after_slippage", "realized_r", "holding_sessions", "forced_cutoff_exit"]


@dataclass(frozen=True)
class RetestRules:
    lookback: int = 20
    breakout_buffer_atr: float = .1
    min_relative_volume: float = 1.2
    retest_tolerance_atr: float = .25
    invalidation_atr: float = .5
    retest_window: int = 10
    stop_buffer_atr: float = .25
    max_entry_gap_atr: float = 1.
    reward_multiple: float = 2.
    max_hold: int = 10

    def __post_init__(self):
        for name, low, high in (("lookback", 5, 252), ("retest_window", 2, 60), ("max_hold", 1, 252)):
            value = getattr(self, name)
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{name} must be an integer in [{low}, {high}].")
        for name in ("breakout_buffer_atr", "min_relative_volume", "retest_tolerance_atr",
                     "invalidation_atr", "stop_buffer_atr", "max_entry_gap_atr", "reward_multiple"):
            value = getattr(self, name)
            if type(value) not in (float, int) or not math.isfinite(value) or not 0 <= value <= 10:
                raise ValueError(f"{name} must be finite and between 0 and 10.")
        if self.stop_buffer_atr <= 0 or self.reward_multiple <= 0:
            raise ValueError("Stop buffer and reward multiple must be positive.")


@dataclass
class RetestResult:
    candidates: pd.DataFrame
    events: pd.DataFrame
    trades: pd.DataFrame
    equity: pd.DataFrame
    metrics: dict
    current: dict


def _check_frame(frame):
    if frame.attrs.get("execution_restriction"):
        raise ValueError(frame.attrs["execution_restriction"])
    required = ["open", "high", "low", "close", "volume", "ema_50", "atr_14", "relative_volume"]
    if frame.empty or any(c not in frame for c in required):
        raise ValueError("The strategy needs nonempty validated daily OHLCV and EMA50/ATR14/relative volume.")
    if not isinstance(frame.index, pd.DatetimeIndex) or not frame.index.is_unique or not frame.index.is_monotonic_increasing:
        raise ValueError("Strategy observations must have unique, increasing session dates.")
    prices = frame[["open", "high", "low", "close", "volume"]]
    if (not np.isfinite(prices.to_numpy()).all() or (prices.iloc[:, :4] <= 0).any().any()
        or (frame.volume < 0).any() or (frame.high < frame[["open", "close", "low"]].max(axis=1)).any()
        or (frame.low > frame[["open", "close", "high"]].min(axis=1)).any()):
        raise ValueError("Strategy input must contain finite, positive, internally consistent OHLC and nonnegative volume.")


def simulate_retest(frame: pd.DataFrame, settings: Settings, rules=None) -> RetestResult:
    rules = rules or RetestRules()
    _check_frame(frame)
    level_series = frame.high.shift(1).rolling(rules.lookback).max()
    fee, slip = settings.fee_bps / 10000, settings.slippage_bps / 10000
    cash, position, active = float(settings.capital), None, None
    candidates, events, trades, curve = [], [], [], []
    current = {"status": "No active setup", "reason": "No accepted setup remains at this cutoff."}
    ready_bars = 0

    def emit(candidate, i, state, reason):
        # Copy scalar evidence now: later candidate updates must not rewrite this tape.
        events.append({"setup_id": candidate["setup_id"], "index": i, "date": frame.index[i].date().isoformat(),
            "state": state, "reason": reason, "level": candidate["level"],
            "reference_atr": candidate["reference_atr"], "stop": candidate.get("stop"),
            "target": candidate.get("target"), "entry": candidate.get("entry")})

    def cancel(candidate, i, reason, state="Cancelled"):
        candidate.update(status=state, reason=reason, decision_date=frame.index[i].date().isoformat())
        emit(candidate, i, state, reason)

    for i, (_, bar) in enumerate(frame.iterrows()):
        date = frame.index[i].date().isoformat()
        busy_at_start = active is not None or position is not None
        terminal = False
        # Entry decision uses only the observed open and yesterday's frozen evidence.
        if active is not None and active.get("retest_index") is not None and position is None:
            p = active
            raw_open = float(bar.open)
            p.update(entry_attempt_date=date, entry_attempt_open=raw_open)
            reason = None
            if raw_open <= p["stop"]:
                reason = "Next open at/below frozen stop"
            elif raw_open < p["level"]:
                reason = "Next open lost the frozen breakout level"
            elif raw_open > p["retest_close"] + rules.max_entry_gap_atr * p["reference_atr"]:
                reason = "Next open exceeded the permitted upward gap"
            if reason is None:
                entry = raw_open * (1 + slip)
                distance = entry - p["stop"]
                target = entry + rules.reward_multiple * distance
                target_fill = target * (1 - slip)
                net_reward = target_fill - entry - fee * (entry + target_fill)
                if net_reward <= 0:
                    reason = "Target reward is nonpositive after estimated costs"
                else:
                    size = size_position(cash, entry, p["stop"], p["retest_volume"], settings)
                    p.update(risk_quantity=size["risk_quantity"], cash_quantity=size["cash_quantity"],
                        liquidity_quantity=size["liquidity_quantity"], risk_budget=size["risk_budget"])
                    if size["quantity"] == 0:
                        reason = "Cash, risk or prior-volume cap permits fewer than one share"
                    else:
                        p.update(status="Open", reason="Filled at next observed open with adverse slippage",
                            entry_index=i, entry_date=date, entry=entry, raw_entry_open=raw_open,
                            target=target, quantity=size["quantity"], planned_risk=size["planned_loss_with_costs"],
                            risk_budget=size["risk_budget"], cash_required=size["cash_required"],
                            risk_quantity=size["risk_quantity"], cash_quantity=size["cash_quantity"],
                            liquidity_quantity=size["liquidity_quantity"],
                            net_reward_risk=net_reward / size["loss_per_unit_with_costs"])
                        cash -= size["cash_required"]
                        position = p
                        emit(p, i, "Entry filled", p["reason"])
            if reason:
                cancel(p, i, reason)
                active, terminal = None, True

        if position is not None:
            p = position
            price, reason = None, None
            if bar.open <= p["stop"]:
                price, reason = float(bar.open), "Gap through stop"
            elif bar.open >= p["target"]:
                price, reason = float(bar.open), "Gap above target"
            elif bar.low <= p["stop"]:
                price = p["stop"]
                reason = "Stop (both touched; stop first)" if bar.high >= p["target"] else "Stop"
            elif bar.high >= p["target"]:
                price, reason = p["target"], "Target"
            elif i - p["entry_index"] + 1 >= rules.max_hold:
                price, reason = float(bar.close), "Holding limit"
            # Capture the genuine cutoff position before the artificial liquidation.
            if i == len(frame) - 1 and price is None:
                current = {**p, "status": "Open at cutoff", "reason": "Simulation liquidates at cutoff; no natural exit observed."}
                price, reason = float(bar.close), "End of data"
            if price is not None:
                exit_fill = price * (1 - slip)
                qty = p["quantity"]
                proceeds = qty * exit_fill * (1 - fee)
                cash += proceeds
                entry_cost = qty * p["entry"] * (1 + fee)
                pnl = proceeds - entry_cost
                trade = {**p, "status": "Closed", "exit_index": i, "exit_date": date, "exit": exit_fill,
                    "raw_exit_reference": price, "reason": reason, "pnl": pnl,
                    "entry_fee": qty * p["entry"] * fee, "exit_fee": qty * exit_fill * fee,
                    "gross_pnl_after_slippage": qty * (exit_fill - p["entry"]),
                    "realized_r": pnl / p["planned_risk"], "holding_sessions": i - p["entry_index"] + 1,
                    "forced_cutoff_exit": reason == "End of data"}
                trades.append(trade)
                p.update(status="Closed", reason=reason, exit_date=date, decision_date=date)
                # End-of-file liquidation is a boundary convention, not a natural event.
                if reason != "End of data":
                    emit(p, i, "Exit", reason)
                position, active, terminal = None, None, True

        elif active is not None and active.get("retest_index") is None:
            p = active
            age, level, atr = i - p["breakout_index"], p["level"], p["reference_atr"]
            if float(bar.close) < level - rules.invalidation_atr * atr:
                cancel(p, i, "Close crossed below the frozen invalidation threshold")
                active, terminal = None, True
            elif age >= rules.retest_window:
                cancel(p, i, "Retest deadline reached before a valid retest", "Expired")
                active, terminal = None, True
            elif bar.low <= level + rules.retest_tolerance_atr * atr and bar.high >= level - rules.retest_tolerance_atr * atr and bar.close >= level:
                if not np.isfinite(bar.ema_50) or bar.close <= bar.ema_50:
                    cancel(p, i, "Retest close did not remain above available EMA50")
                    active, terminal = None, True
                else:
                    stop = min(float(bar.low), level) - rules.stop_buffer_atr * atr
                    if stop <= 0:
                        cancel(p, i, "Retest produced a nonpositive structural stop")
                        active, terminal = None, True
                    else:
                        p.update(status="Awaiting next open", reason="Retest held; one next-open entry attempt pending",
                            retest_index=i, retest_date=date, retest_low=float(bar.low), retest_close=float(bar.close),
                            retest_volume=float(bar.volume), stop=stop,
                            max_entry_open=float(bar.close) + rules.max_entry_gap_atr * p['reference_atr'])
                        emit(p, i, "Retest confirmed", p["reason"])

        # Fresh break at today's completed close. Never use today's ATR as prior ATR.
        if i >= rules.lookback:
            atr, level, rvol = float(frame.atr_14.iloc[i-1]), float(level_series.iloc[i]), float(bar.relative_volume)
            ready = all(np.isfinite(v) for v in (atr, level, rvol, bar.ema_50)) and atr > 0
            ready_bars += int(ready)
            threshold = level + rules.breakout_buffer_atr * atr
            geometric = (np.isfinite(atr) and atr > 0 and np.isfinite(rvol) and rvol >= rules.min_relative_volume
                and bar.close > threshold and frame.close.iloc[i-1] <= threshold)
            if geometric:
                p = {"setup_id": f"retest-{date}", "breakout_index": i, "breakout_date": date,
                    "range_start": frame.index[i-rules.lookback].date().isoformat(),
                    "range_end": frame.index[i-1].date().isoformat(), "level": level, "reference_atr": atr,
                    "breakout_close": float(bar.close), "breakout_relative_volume": rvol,
                    "invalidation_close_below": level - rules.invalidation_atr * atr,
                    "retest_last_eligible_index": i + rules.retest_window - 1,
                    "status": "Awaiting retest", "reason": "Fresh break accepted; wait for a later completed retest"}
                candidates.append(p)
                if busy_at_start or active is not None or position is not None or terminal:
                    cancel(p, i, "Another setup/position or terminal transition occupies this bar", "Skipped capacity")
                elif not np.isfinite(bar.ema_50) or bar.close <= bar.ema_50:
                    cancel(p, i, "Breakout close was not above available EMA50", "Rejected")
                else:
                    active = p
                    emit(p, i, "Breakout accepted", p["reason"])

        liquidation = position["quantity"] * float(bar.close) * (1-slip) * (1-fee) if position else 0.
        curve.append({"date": frame.index[i], "cash": cash, "position_value": liquidation, "equity": cash + liquidation})

    if active is not None:
        current = {**active, "reason": active["reason"] + " at cutoff; not a failed or expired trade"}
    equity = pd.DataFrame(curve).set_index("date")
    equity["drawdown"] = equity.equity / equity.equity.cummax().clip(lower=settings.capital) - 1
    trade_frame = pd.DataFrame(trades, columns=TRADE_COLUMNS)
    profits = trade_frame.pnl if len(trades) else pd.Series(dtype=float)
    losses = -float(profits[profits < 0].sum())
    metrics = {"candidates": len(candidates), "trades": len(trades), "ready_observations": ready_bars,
        "cancelled": sum(p["status"] in {"Cancelled", "Rejected", "Expired"} for p in candidates),
        "skipped_capacity": sum(p["status"] == "Skipped capacity" for p in candidates),
        "pending": int(active is not None), "forced_cutoff_exits": sum(t["forced_cutoff_exit"] for t in trades),
        "final_equity": float(equity.equity.iloc[-1]), "total_return": float(equity.equity.iloc[-1]/settings.capital-1),
        "max_drawdown": float(equity.drawdown.min()),
        "historical_win_fraction": float((profits > 0).mean()) if len(profits) else None,
        "profit_factor": float(profits[profits > 0].sum()/losses) if losses > 0 else None,
        "expectancy": float(profits.mean()) if len(profits) else None,
        "validation": "Exploratory same-dataset hypothesis. No held-out, prospective or calibrated-probability validation."}
    event_frame = pd.DataFrame(events, columns=EVENT_COLUMNS).astype({"stop": float, "target": float, "entry": float})
    return RetestResult(pd.DataFrame(candidates, columns=CANDIDATE_COLUMNS),
        event_frame, trade_frame, equity, metrics, current)
