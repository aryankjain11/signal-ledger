"""Top-down multi-timeframe read: monthly, weekly and daily from the same daily bars.

Higher timeframes are built only from *completed* periods. The calendar week or
month containing the last daily bar is always dropped, even if it might be
complete, so a higher-timeframe reading never uses a period that is still forming.
Nothing is made up when history is short: the timeframe is reported unavailable.
"""
from __future__ import annotations

import math

import pandas as pd

from .data import completed_weeks
from .indicators import indicators
from .patterns import market_structure, swings

MIN_BARS = {"Monthly": 24, "Weekly": 30, "Daily": 60}
STRUCTURE_SIGNAL = {"Bullish structure": 1, "Bearish structure": -1, "Mixed / range structure": 0}


def completed_months(bars: pd.DataFrame) -> pd.DataFrame:
    periods = bars.index.to_period("M")
    prior = bars.loc[periods < periods[-1]]
    if prior.empty:
        return bars.iloc[:0].copy()
    grouped = prior.groupby(prior.index.to_period("M"))
    result = grouped.agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    result.index = pd.DatetimeIndex(grouped.apply(lambda x: x.index[-1]).to_numpy())
    return result


def _finite(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def read_timeframe(name: str, bars: pd.DataFrame, pivot_window: int) -> dict:
    """Trend vote for one timeframe from close vs EMA20, EMA10 vs EMA20 and Supertrend."""
    if len(bars) < MIN_BARS[name]:
        return {"timeframe": name, "status": "Unavailable", "bars": len(bars), "signal": None,
                "label": "Unavailable", "detail": f"Needs {MIN_BARS[name]} completed {name.lower()} bars; {len(bars)} available."}
    frame = indicators(bars)
    frame["ema_10"] = frame.close.ewm(span=10, adjust=False, min_periods=10).mean()
    last = frame.iloc[-1]
    close, ema10, ema20 = float(last.close), _finite(last.ema_10), _finite(last.ema_20)
    st_dir, rsi, hist = _finite(last.get("supertrend_dir")), _finite(last.rsi_14), _finite(last.macd_histogram)
    subs = []
    if ema20 is not None:
        subs.append(1 if close > ema20 else -1)
    if ema10 is not None and ema20 is not None:
        subs.append(1 if ema10 > ema20 else -1)
    if st_dir is not None:
        subs.append(int(st_dir))
    if len(subs) < 2:
        signal = None
    else:
        need = max(2, len(subs) - 1)
        signal = 1 if sum(subs) >= need else -1 if sum(subs) <= -need else 0
    structure, structure_text = market_structure(swings(frame, pivot_window))
    bits = []
    if ema20 is not None:
        bits.append(f"close {'above' if close > ema20 else 'below'} EMA20 ({ema20:,.2f})")
    if st_dir is not None:
        bits.append(f"Supertrend {'up' if st_dir > 0 else 'down'}")
    if rsi is not None:
        bits.append(f"RSI {rsi:.0f}")
    if hist is not None:
        bits.append(f"MACD {'rising' if hist > 0 else 'falling'}")
    label = {1: "Uptrend", -1: "Downtrend", 0: "Sideways / mixed", None: "Unavailable"}[signal]
    return {"timeframe": name, "status": "Available", "bars": len(bars), "signal": signal, "label": label,
            "structure": structure, "structure_signal": STRUCTURE_SIGNAL.get(structure),
            "last_period": frame.index[-1].date().isoformat(), "close": close, "rsi": rsi,
            "detail": "; ".join(bits) + f". Swings: {structure.lower()}."}


def multi_timeframe(bars: pd.DataFrame, pivot_window: int = 3) -> dict:
    """Monthly → weekly → daily trend reads plus a plain-language alignment verdict."""
    reads = [read_timeframe("Monthly", completed_months(bars), 2),
             read_timeframe("Weekly", completed_weeks(bars), 2),
             read_timeframe("Daily", bars, pivot_window)]
    by = {r["timeframe"]: r for r in reads}
    htf, alignment = alignment_verdict(by["Monthly"]["signal"], by["Weekly"]["signal"], by["Daily"]["signal"])
    return {"reads": reads, "higher_signal": htf, "alignment": alignment,
            "note": "Weekly/monthly bars use only completed calendar periods; the current week and month are excluded."}


def alignment_verdict(monthly, weekly, daily):
    """Combine monthly+weekly into one higher-timeframe signal and describe daily against it.

    Both directional and equal -> that direction; one unavailable -> the other;
    anything else (sideways or opposite) -> 0, described precisely.
    """
    words = {1: "up", -1: "down", 0: "sideways"}
    available = [x for x in (monthly, weekly) if x is not None]
    if not available:
        return None, "Higher timeframes unavailable: not enough completed weeks/months."
    if len(available) == 1:
        htf = available[0]
    else:
        htf = monthly if monthly == weekly else 0
    if htf == 0 and len(available) == 2 and monthly != weekly:
        if 0 in (monthly, weekly):
            moving = monthly if monthly else weekly
            larger = (f"Monthly {words[monthly]}, weekly {words[weekly]}: the larger trend is {words[moving]} "
                      f"but {'pausing' if weekly == 0 else 'not yet established'} on the {'weekly' if weekly == 0 else 'monthly'} chart.")
        else:
            larger = f"Monthly {words[monthly]} but weekly {words[weekly]}: the higher timeframes conflict."
    elif htf == 0:
        larger = "Higher timeframes are sideways."
    else:
        larger = f"Higher timeframes point {words[htf]}."
    if daily is None:
        return htf, larger + " Daily trend not yet readable."
    if htf in (1, -1) and daily == htf:
        return htf, f"Aligned: daily {words[daily]}, same direction as the higher timeframes."
    if htf in (1, -1) and daily == -htf:
        return htf, (f"Counter-trend: daily {words[daily]} against a higher-timeframe {words[htf]}trend. "
                     "Moves against the larger trend tend to be less reliable.")
    if htf in (1, -1):
        return htf, f"Daily is sideways inside a higher-timeframe {words[htf]}trend."
    return htf, larger + f" Daily is {words[daily]}."
