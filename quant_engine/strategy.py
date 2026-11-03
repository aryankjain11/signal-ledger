"""One daily, long-only hypothesis. No calibrated probability is implied."""
import math

import pandas as pd

from .models import BacktestResult, Settings


def breakout_signals(frame: pd.DataFrame, settings: Settings) -> pd.Series:
    prior_high = frame.high.shift(1).rolling(settings.lookback).max()
    return ((frame.close > prior_high) & (frame.close > frame.ema_50) &
            (frame.relative_volume >= 1.2) & (frame.atr_14 > 0)).fillna(False)


def size_position(equity: float, entry: float, stop: float, prior_volume: float,
                  settings: Settings) -> dict:
    values = (equity, entry, stop, prior_volume)
    if not all(math.isfinite(v) for v in values) or equity <= 0 or not 0 < stop < entry or prior_volume < 0:
        raise ValueError("Position sizing requires positive equity and entry > stop > 0, with nonnegative volume.")
    fee = settings.fee_bps / 10_000
    slip = settings.slippage_bps / 10_000
    stop_fill = stop * (1 - slip)
    loss_per_unit = entry - stop_fill + fee * (entry + stop_fill)
    risk_budget = equity * settings.risk_fraction
    risk_quantity = math.floor(risk_budget / loss_per_unit)
    cash_quantity = math.floor(equity / (entry * (1 + fee)))
    liquidity_quantity = math.floor(prior_volume * settings.participation)
    quantity = max(0, min(risk_quantity, cash_quantity, liquidity_quantity))
    return {"quantity": quantity, "risk_budget": risk_budget,
            "loss_per_unit_with_costs": loss_per_unit,
            "planned_loss_with_costs": quantity * loss_per_unit,
            "cash_required": quantity * entry * (1 + fee),
            "risk_quantity": risk_quantity, "cash_quantity": cash_quantity,
            "liquidity_quantity": liquidity_quantity}


def current_setup(frame: pd.DataFrame, settings: Settings) -> dict:
    bar = frame.iloc[-1]
    if not bool(breakout_signals(frame, settings).iloc[-1]):
        return {"status": "NO TRADE — INSUFFICIENT EVIDENCE",
                "reason": f"Requires a close above the prior {settings.lookback} highs, above EMA50, relative volume >= 1.2, and a valid ATR14.",
                "probability": None}
    entry = float(bar.close * (1 + settings.slippage_bps / 10_000))
    stop = float(entry - settings.stop_atr * bar.atr_14)
    if stop <= 0:
        return {"status": "NO TRADE — INVALID STOP", "probability": None}
    target = entry + settings.reward_risk * (entry - stop)
    size = size_position(settings.capital, entry, stop, float(bar.volume), settings)
    fee = settings.fee_bps / 10_000
    target_fill = target * (1 - settings.slippage_bps / 10_000)
    reward = target_fill - entry - fee * (target_fill + entry)
    return {"status": "Conditional long research setup" if size["quantity"] else "NO TRADE — POSITION BELOW ONE SHARE",
            "entry_condition": "Next observed session open only. Recompute entry, stop, target and size from that open; expires if that entry cannot be taken.",
            "reference_entry": entry, "reference_stop": stop, "reference_target": target,
            "gross_reward_risk": settings.reward_risk,
            "net_reward_risk_at_reference": reward / size["loss_per_unit_with_costs"],
            "max_hold_sessions": settings.max_hold, "probability": None,
            "invalidation": "Exit at the volatility stop, target, or holding limit. Stop distance is fixed at entry; gaps can exceed intended risk.",
            "note": "Reference levels use the latest close with entry slippage. They are illustrative, not a known next-open fill.", **size}


def backtest(frame: pd.DataFrame, settings: Settings) -> BacktestResult:
    signals = breakout_signals(frame, settings)
    fee = settings.fee_bps / 10_000
    slip = settings.slippage_bps / 10_000
    cash = settings.capital
    position = None
    trades, curve = [], []
    for i in range(len(frame)):
        bar = frame.iloc[i]
        date = frame.index[i].date().isoformat()
        # Yesterday's completed-bar signal is the only entry input today.
        if position is None and i > 0 and bool(signals.iloc[i - 1]):
            entry = float(bar.open * (1 + slip))
            distance = float(settings.stop_atr * frame.atr_14.iloc[i - 1])
            stop = entry - distance
            if stop > 0:
                size = size_position(cash, entry, stop, float(frame.volume.iloc[i - 1]), settings)
                qty = size["quantity"]
                if qty > 0:
                    cash -= qty * entry * (1 + fee)
                    position = {"signal_date": frame.index[i - 1].date().isoformat(),
                                "entry_date": date, "entry_index": i, "entry": entry,
                                "stop": stop, "target": entry + settings.reward_risk * distance,
                                "quantity": qty, "planned_risk": size["planned_loss_with_costs"]}
        if position is not None:
            p = position
            price, reason = None, None
            # Adverse opening gaps override an assumed fill at the stop threshold.
            if bar.open <= p["stop"]:
                price, reason = float(bar.open), "Gap through stop"
            elif bar.open >= p["target"]:
                price, reason = float(bar.open), "Gap above target"
            elif bar.low <= p["stop"]:
                price = p["stop"]
                reason = "Stop (both touched; stop first)" if bar.high >= p["target"] else "Stop"
            elif bar.high >= p["target"]:
                price, reason = p["target"], "Target"
            elif i - p["entry_index"] + 1 >= settings.max_hold:
                price, reason = float(bar.close), "Holding limit"
            elif i == len(frame) - 1:
                price, reason = float(bar.close), "End of data"
            if price is not None:
                exit_fill = price * (1 - slip)
                proceeds = p["quantity"] * exit_fill * (1 - fee)
                cash += proceeds
                pnl = proceeds - p["quantity"] * p["entry"] * (1 + fee)
                trades.append({**p, "exit_date": date, "exit": exit_fill,
                               "pnl": pnl, "reason": reason,
                               "holding_sessions": i - p["entry_index"] + 1})
                position = None
        liquidation_value = (position["quantity"] * float(bar.close) * (1 - slip) * (1 - fee)
                             if position is not None else 0)
        curve.append({"date": frame.index[i], "equity": cash + liquidation_value})
    equity = pd.DataFrame(curve).set_index("date")
    equity["drawdown"] = equity.equity / equity.equity.cummax().clip(lower=settings.capital) - 1
    trade_frame = pd.DataFrame(trades)
    profits = trade_frame.pnl if not trade_frame.empty else pd.Series(dtype=float)
    loss = -float(profits[profits < 0].sum())
    metrics = {"trades": len(trades), "final_equity": float(equity.equity.iloc[-1]),
               "total_return": float(equity.equity.iloc[-1] / settings.capital - 1),
               "max_drawdown": float(equity.drawdown.min()),
               "historical_win_fraction": float((profits > 0).mean()) if len(profits) else None,
               "profit_factor": float(profits[profits > 0].sum() / loss) if loss > 0 else None,
               "expectancy": float(profits.mean()) if len(profits) else None,
               "gross_buy_hold_return": float(frame.close.iloc[-1] / frame.close.iloc[0] - 1),
               "validation": "Exploratory, same-dataset simulation. No held-out or prospective validation; not a forecast."}
    return BacktestResult(trade_frame, equity, metrics)
