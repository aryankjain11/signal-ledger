"""Deterministic evidence summary: one vote per evidence family, plus non-voting context.

Highly correlated indicators (EMA alignment, Supertrend, SMA200; or RSI, MACD, ROC)
are first combined inside their family, so the overall balance counts each kind of
evidence once. The result is a heuristic description of current evidence. It is
not a probability and does not by itself recommend a trade.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

LIVE_STATES = ("Developing", "Confirmed", "Breakout", "Breakdown", "Retest held", "Continuation",
               "Contextual geometry", "Confirmed-pivot observation", "Confirmed upward break",
               "Confirmed downward break", "Confirmed neckline break")
WORDS = {1: "Bullish", -1: "Bearish", 0: "Neutral", None: "Unavailable"}


def _num(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _combine(subsignals):
    """Majority inside a family: need all-but-one agreement (and at least two inputs)."""
    values = [s for s in subsignals if s is not None]
    if len(values) < 2:
        return None
    need = max(2, len(values) - 1)
    total = sum(values)
    return 1 if total >= need else -1 if total <= -need else 0


def _family(name, signal, detail, votes=True, inputs=None):
    return {"family": name, "signal": signal, "label": WORDS[signal], "detail": detail,
            "votes": votes, "inputs": inputs or []}


def market_read(analysis, recent_bars: int = 15) -> dict:
    frame = analysis.frame
    last = frame.iloc[-1]
    close = float(last.close)
    atr = _num(last.get("atr_14"))
    families = []

    # 1. Confirmed swing structure
    structure = {"Bullish structure": 1, "Bearish structure": -1, "Mixed / range structure": 0}.get(analysis.trend)
    families.append(_family("Price structure", structure, analysis.structure))

    # 2. Trend (moving averages + Supertrend), combined
    ema20, ema50, sma200 = (_num(last.get(k)) for k in ("ema_20", "ema_50", "sma_200"))
    st_dir = _num(last.get("supertrend_dir"))
    inputs = []
    subs = []
    if ema50 is not None:
        subs.append(1 if close > ema50 else -1)
        inputs.append(f"close {'above' if close > ema50 else 'below'} EMA50 ({ema50:,.2f})")
    if ema20 is not None and ema50 is not None:
        subs.append(1 if ema20 > ema50 else -1)
        inputs.append(f"EMA20 {'above' if ema20 > ema50 else 'below'} EMA50")
    if st_dir is not None:
        subs.append(int(st_dir))
        inputs.append(f"Supertrend {'up' if st_dir > 0 else 'down'} (line {float(last.supertrend):,.2f})")
    if sma200 is not None:
        subs.append(1 if close > sma200 else -1)
        inputs.append(f"close {'above' if close > sma200 else 'below'} SMA200 ({sma200:,.2f})")
    trend = _combine(subs)
    families.append(_family("Trend", trend, "; ".join(inputs) or "Needs 50+ sessions for moving averages.", inputs=inputs))

    # 3. Momentum (RSI band, MACD histogram, ROC), combined
    rsi, hist, roc = (_num(last.get(k)) for k in ("rsi_14", "macd_histogram", "roc_10"))
    subs, inputs = [], []
    if rsi is not None:
        subs.append(1 if rsi > 55 else -1 if rsi < 45 else 0)
        inputs.append(f"RSI14 {rsi:.1f}")
    if hist is not None:
        subs.append(1 if hist > 0 else -1 if hist < 0 else 0)
        inputs.append(f"MACD histogram {'positive' if hist > 0 else 'negative'}")
    if roc is not None:
        subs.append(1 if roc > 0 else -1 if roc < 0 else 0)
        inputs.append(f"10-session change {roc:+.1f}%")
    families.append(_family("Momentum", _combine(subs), "; ".join(inputs) or "Warming up.", inputs=inputs))

    # 4. Volume flow (CMF and OBV direction), both must agree
    cmf = _num(last.get("cmf_20"))
    obv_change = _num(frame.obv.iloc[-1] - frame.obv.iloc[-21]) if len(frame) > 21 else None
    subs, inputs = [], []
    if cmf is not None:
        subs.append(1 if cmf > .05 else -1 if cmf < -.05 else 0)
        inputs.append(f"Chaikin money flow {cmf:+.2f}")
    if obv_change is not None:
        subs.append(1 if obv_change > 0 else -1 if obv_change < 0 else 0)
        inputs.append(f"OBV {'rising' if obv_change > 0 else 'falling'} over 20 sessions")
    flow = None if len(subs) < 2 else (subs[0] if subs[0] == subs[1] else 0)
    families.append(_family("Volume flow", flow, "; ".join(inputs) or "Needs 21+ sessions.", inputs=inputs))

    # 5. Completed weekly context
    weekly = analysis.weekly
    wk = None if weekly.get("status") != "Available" else (1 if weekly["context"].startswith("Above") else -1)
    families.append(_family("Weekly timeframe", wk, f"{weekly['context']} ({weekly['completed_weeks']} completed weeks)."))

    # 6. Recent, still-live pattern observations with a direction
    start = len(frame) - recent_bars
    latest = {}
    for event in sorted(analysis.events, key=lambda e: e["index"]):
        latest[event["id"]] = event
    live = [e for e in latest.values() if e["index"] >= start and e.get("direction") in (1, -1)
            and e["status"].startswith(LIVE_STATES)]
    if live:
        net = sum(e["direction"] for e in live)
        names = ", ".join(f"{e['name']} ({e['status'].lower()}, {e['detected_at']})" for e in sorted(live, key=lambda e: e["index"])[-4:])
        families.append(_family("Recent patterns", int(np.sign(net)), names))
    else:
        families.append(_family("Recent patterns", None, f"No directional pattern observation in the last {recent_bars} sessions."))

    # Context that informs but does not vote
    adx = _num(last.get("adx_14"))
    if adx is not None:
        strength = "strong trend" if adx >= 25 else "developing trend" if adx >= 20 else "weak trend / range-bound"
        di = "+DI leads" if last.plus_di_14 > last.minus_di_14 else "−DI leads"
        families.append(_family("Trend strength (ADX)", None, f"ADX {adx:.1f}: {strength}; {di}.", votes=False))
    stretch = []
    if rsi is not None and (rsi >= 70 or rsi <= 30):
        stretch.append(f"RSI {'overbought' if rsi >= 70 else 'oversold'} ({rsi:.1f})")
    wr, cci = _num(last.get("williams_r_14")), _num(last.get("cci_20"))
    if wr is not None and (wr >= -20 or wr <= -80):
        stretch.append(f"Williams %R {wr:.0f}")
    if cci is not None and abs(cci) >= 100:
        stretch.append(f"CCI {cci:.0f}")
    families.append(_family("Stretch", None, ("; ".join(stretch) + ". Stretched readings can persist in strong trends; they are not reversal signals.")
                            if stretch else "No oscillator at an extreme.", votes=False))
    vol_bits = []
    if _num(last.get("squeeze_on")) == 1:
        vol_bits.append("Bollinger bands inside Keltner channels (volatility squeeze)")
    if _num(last.get("atr_pct")) is not None:
        vol_bits.append(f"ATR {float(last.atr_pct):.2f}% of price")
    if _num(last.get("hv_20")) is not None:
        vol_bits.append(f"20-session annualized volatility {float(last.hv_20):.1f}%")
    families.append(_family("Volatility", None, "; ".join(vol_bits) or "Warming up.", votes=False))

    voting = [f for f in families if f["votes"]]
    bullish = sum(f["signal"] == 1 for f in voting)
    bearish = sum(f["signal"] == -1 for f in voting)
    neutral = sum(f["signal"] == 0 for f in voting)
    available = bullish + bearish + neutral
    net = bullish - bearish
    if available < 3:
        verdict = "Insufficient evidence"
    elif net >= 3 and bearish == 0:
        verdict = "Bullish"
    elif net <= -3 and bullish == 0:
        verdict = "Bearish"
    elif net >= 2 and bearish <= 1:
        verdict = "Leaning bullish"
    elif net <= -2 and bullish <= 1:
        verdict = "Leaning bearish"
    else:
        verdict = "Mixed / conflicting"

    levels = key_levels(analysis, close, atr)
    summary = (f"{bullish} of {available} evidence families point up, {bearish} down and {neutral} neutral."
               if available else "Not enough history to read the evidence.")
    return {"verdict": verdict, "bullish": bullish, "bearish": bearish, "neutral": neutral,
            "available": available, "families": families, "levels": levels, "summary": summary,
            "probability": None,
            "basis": "Count of agreeing evidence families (one vote each); a heuristic description, not a probability or a trade signal."}


def key_levels(analysis, close, atr):
    frame = analysis.frame
    rows = []
    def add(kind, label, low, high=None):
        high = low if high is None else high
        mid = (low + high) / 2
        rows.append({"kind": kind, "label": label, "low": float(low), "high": float(high),
                     "distance_pct": 100 * (mid / close - 1),
                     "distance_atr": (mid - close) / atr if atr else None})
    below = [z for z in analysis.zones if z["high"] < close]
    above = [z for z in analysis.zones if z["low"] > close]
    for z in sorted(below, key=lambda z: close - z["high"])[:2]:
        add("Support", f"Support · {z['pivot_count']} swings", z["low"], z["high"])
    for z in sorted(above, key=lambda z: z["low"] - close)[:2]:
        add("Resistance", f"Resistance · {z['pivot_count']} swings", z["low"], z["high"])
    inside = [z for z in analysis.zones if z["low"] <= close <= z["high"]]
    for z in inside[:1]:
        add("Inside zone", f"Inside zone · {z['pivot_count']} swings", z["low"], z["high"])
    if len(frame) > 21:
        add("Resistance", "20-day high", float(frame.high.iloc[-21:-1].max()))
        add("Support", "20-day low", float(frame.low.iloc[-21:-1].min()))
    hi, lo = _num(frame.high_52w.iloc[-1]) if "high_52w" in frame else None, _num(frame.low_52w.iloc[-1]) if "low_52w" in frame else None
    if hi is not None:
        add("Resistance", "52-week high", hi)
        add("Support", "52-week low", lo)
    return sorted(rows, key=lambda r: -r["distance_pct"])
