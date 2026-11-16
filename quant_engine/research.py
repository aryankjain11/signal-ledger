"""Causal descriptive events. Rules are hypotheses, not validated trading signals."""
from dataclasses import asdict

import numpy as np
import pandas as pd

from .models import ResearchRules

RULE_VERSION = "research-events/1"


def _date(frame, i):
    return frame.index[i].date().isoformat()


def breakout_events(frame, rules=None):
    rules = rules or ResearchRules()
    events, active = [], {}
    levels = {1: frame.high.shift(1).rolling(rules.lookback).max(),
              -1: frame.low.shift(1).rolling(rules.lookback).min()}
    def emit(state, i, status):
        direction = state["direction"]
        level = state["level"]
        events.append({"id": state["id"], "family": "breakout", "name": "Bullish breakout/retest" if direction == 1 else "Bearish breakdown/retest",
            "status": status, "index": i, "formed_at": _date(frame, state["start"]), "detected_at": _date(frame, i),
            "price": float(frame.high.iloc[i] if direction == 1 else frame.low.iloc[i]),
            "level": level, "direction": direction, "reference_atr": state["atr"],
            "reference_start": _date(frame, state["start"] - rules.lookback),
            "reference_end": _date(frame, state["start"] - 1),
            "coordinates": [[_date(frame, state["start"] - rules.lookback), level], [_date(frame, i), level]],
            "evidence": f"Frozen prior-{rules.lookback} {'high' if direction == 1 else 'low'} {level:.4f}; prior ATR {state['atr']:.4f}; break RVOL {state['rvol']:.2f}. Close-based state: {status}. No intrabar fill/order sequence inferred.",
            "rule_version": RULE_VERSION})
    for i in range(rules.lookback, len(frame)):
        bar = frame.iloc[i]
        for direction in (1, -1):
            state = active.get(direction)
            if state:
                age, level, atr = i - state["start"], state["level"], state["atr"]
                if direction * (bar.close - level) < -rules.invalidation_atr * atr:
                    emit(state, i, "Failed")
                    del active[direction]
                elif state["retest"] is not None and i > state["retest"] and direction * (bar.close - state["break_extreme"]) > rules.continuation_atr * atr:
                    emit(state, i, "Continuation")
                    del active[direction]
                elif age >= rules.retest_window:
                    emit(state, i, "Expired after retest" if state["retest"] is not None else "Expired without retest")
                    del active[direction]
                elif state["retest"] is None and bar.low <= level + rules.retest_tolerance_atr * atr and bar.high >= level - rules.retest_tolerance_atr * atr and direction * (bar.close - level) >= 0:
                    state["retest"] = i
                    emit(state, i, "Retest held")
                # A terminal bar cannot also create another event of the same direction.
                continue
            atr = float(frame.atr_14.iloc[i - 1])
            rvol = float(bar.relative_volume)
            if not np.isfinite(atr) or atr <= 0 or not np.isfinite(rvol) or rvol < rules.min_relative_volume:
                continue
            level = float(levels[direction].iloc[i])
            threshold = level + direction * rules.breakout_buffer_atr * atr
            if direction * (bar.close - threshold) <= 0 or direction * (frame.close.iloc[i - 1] - threshold) > 0:
                continue
            state = {"id": f"break-{direction}-{_date(frame, i)}", "direction": direction, "level": level,
                "atr": atr, "rvol": rvol, "start": i, "retest": None,
                "break_extreme": float(bar.high if direction == 1 else bar.low)}
            active[direction] = state
            emit(state, i, "Breakout" if direction == 1 else "Breakdown")
    return events


def contextual_candles(frame, rules=None):
    rules = rules or ResearchRules()
    events = []
    def trend_before(index):
        if index < rules.candle_trend_bars or index == 0:
            return 0
        atr = float(frame.atr_14.iloc[index - 1])
        move = float(frame.close.iloc[index - 1] - frame.close.iloc[index - rules.candle_trend_bars])
        return int(np.sign(move)) if np.isfinite(atr) and atr > 0 and abs(move) >= atr else 0
    def emit(i, start, name, direction, evidence):
        events.append({"id": f"context-candle-{name}-{_date(frame, i)}", "family": "candle", "name": name,
            "status": "Contextual geometry", "index": i, "formed_at": _date(frame, start), "detected_at": _date(frame, i),
            "price": float(frame.high.iloc[i]), "direction": direction, "evidence": evidence + " Geometry only; no reversal probability.", "rule_version": RULE_VERSION})
    for i in range(len(frame)):
        b = frame.iloc[i]
        body, width = abs(b.close - b.open), b.high - b.low
        upper, lower = b.high - max(b.open, b.close), min(b.open, b.close) - b.low
        trend = trend_before(i)
        if width > 0 and body > 0 and body <= .35 * width and trend:
            if lower >= 2 * body and upper <= body:
                emit(i, i, "Hammer" if trend < 0 else "Hanging man", -trend,
                     f"Body <=35% range, lower shadow >=2 bodies, upper <=1 body; preceding {rules.candle_trend_bars}-bar trend {'down' if trend < 0 else 'up'} by >=1 prior ATR.")
            if upper >= 2 * body and lower <= body:
                emit(i, i, "Inverted hammer" if trend < 0 else "Shooting star", -trend,
                     f"Body <=35% range, upper shadow >=2 bodies, lower <=1 body; preceding {rules.candle_trend_bars}-bar trend {'down' if trend < 0 else 'up'} by >=1 prior ATR.")
        if i < 2:
            continue
        first, middle = frame.iloc[i - 2], frame.iloc[i - 1]
        first_body, middle_body = abs(first.close - first.open), abs(middle.close - middle.open)
        atr = float(frame.atr_14.iloc[i - 3]) if i >= 3 else np.nan
        prior_trend = trend_before(i - 2)
        if not np.isfinite(atr) or first_body < .5 * atr or middle_body > .3 * first_body or body < .5 * first_body:
            continue
        midpoint = (first.open + first.close) / 2
        if prior_trend > 0 and first.close > first.open and b.close < b.open and b.close < midpoint and min(middle.open, middle.close) >= midpoint:
            emit(i, i - 2, "Evening Star", -1, "Prior uptrend, first bullish body >=0.5 ATR, middle body <=30% of first near its upper half, bearish third body >=50% of first closing below first midpoint. Gap not required in this variant.")
        if prior_trend < 0 and first.close < first.open and b.close > b.open and b.close > midpoint and max(middle.open, middle.close) <= midpoint:
            emit(i, i - 2, "Morning Star", 1, "Prior downtrend, first bearish body >=0.5 ATR, middle body <=30% of first near its lower half, bullish third body >=50% of first closing above first midpoint. Gap not required in this variant.")
    return events


def chart_formations(frame, pivots):
    """Fit/freeze 3 high and 3 low anchors as they become confirmed; no hindsight refit."""
    events, seen = [], set()
    grouped = {}
    for pivot in pivots:
        grouped.setdefault(pivot.confirmed_at, []).append(pivot)
    highs, lows = [], []
    for known, new in sorted(grouped.items()):
        highs = (highs + [p for p in new if p.kind == "high"])[-3:]
        lows = (lows + [p for p in new if p.kind == "low"])[-3:]
        if len(highs) < 3 or len(lows) < 3:
            continue
        anchors = sorted(highs + lows, key=lambda p: p.index)
        key = tuple((p.kind, p.index) for p in anchors)
        if key in seen or any(a.kind == b.kind for a, b in zip(anchors, anchors[1:])):
            continue
        seen.add(key)
        start = anchors[0].index
        span = anchors[-1].index - start
        atr = float(frame.atr_14.iloc[known])
        if not 10 <= span <= 120 or not np.isfinite(atr) or atr <= 0:
            continue
        ux, uy = np.array([p.index - start for p in highs]), np.array([p.price for p in highs])
        lx, ly = np.array([p.index - start for p in lows]), np.array([p.price for p in lows])
        upper, lower = np.polyfit(ux, uy, 1), np.polyfit(lx, ly, 1)
        if max(abs(np.polyval(upper, ux) - uy).max(), abs(np.polyval(lower, lx) - ly).max()) > .5 * atr:
            continue
        upper_change, lower_change = upper[0] * span, lower[0] * span
        width_start = float(upper[1] - lower[1])
        width_now = float(np.polyval(upper, known - start) - np.polyval(lower, known - start))
        if width_start < 2 * atr or width_now < .5 * atr:
            continue
        if abs(upper_change) <= .5 * atr and abs(lower_change) <= .5 * atr:
            name = "Rectangle consolidation"
        elif abs(upper_change) <= .5 * atr and lower_change >= atr:
            name = "Ascending triangle"
        elif upper_change <= -atr and abs(lower_change) <= .5 * atr:
            name = "Descending triangle"
        elif upper_change <= -atr and lower_change >= atr:
            name = "Symmetrical triangle"
        else:
            continue
        if name != "Rectangle consolidation" and width_now >= .85 * width_start:
            continue
        base = {"id": f"formation-{name}-{_date(frame, start)}-{_date(frame, known)}", "family": "chart", "name": name,
            "formed_at": _date(frame, anchors[-1].index), "formation_start": _date(frame, start),
            "coordinates": [[p.timestamp, p.price] for p in anchors], "rule_version": RULE_VERSION,
            "geometry": {"upper_slope_per_observation": float(upper[0]), "lower_slope_per_observation": float(lower[0]),
                "max_fit_residual": float(max(abs(np.polyval(upper, ux) - uy).max(), abs(np.polyval(lower, lx) - ly).max())),
                "reference_atr": atr, "anchor_span": span, "initial_width": width_start, "width_at_detection": width_now},
            "evidence": "Three alternating confirmed highs and lows; linear-fit residual <=0.5 ATR. Frozen boundary slopes/width and 10–120-bar span define this geometry; predictive value unvalidated."}
        for i in range(known, min(len(frame), known + 41)):
            top, bottom = float(np.polyval(upper, i - start)), float(np.polyval(lower, i - start))
            status = None
            if top <= bottom:
                status = "Invalidated: boundaries crossed"
            elif frame.close.iloc[i] > top + .1 * atr:
                status = "Confirmed upward break"
            elif frame.close.iloc[i] < bottom - .1 * atr:
                status = "Confirmed downward break"
            elif i == known + 40:
                status = "Expired"
            elif i == known:
                status = "Developing"
            if status:
                events.append({**base, "status": status, "index": i, "detected_at": _date(frame, i),
                    "price": float(frame.high.iloc[i]), "boundaries": {"upper": top, "lower": bottom},
                    "boundary_coordinates": {"upper": [[_date(frame, start), float(upper[1])], [_date(frame, i), top]],
                                             "lower": [[_date(frame, start), float(lower[1])], [_date(frame, i), bottom]]}})
                if status != "Developing":
                    break
    return events


def momentum_analysis(frame, pivots):
    last = frame.iloc[-1]
    facts = []
    for key, label in (("rsi_14", "RSI14"), ("macd_histogram", "MACD histogram"), ("roc_10", "10-observation ROC (%)"), ("stoch_k_14", "Fast stochastic %K14")):
        value = float(last[key])
        facts.append({"measure": label, "value": value if np.isfinite(value) else None,
                      "state": "Warming up / undefined" if not np.isfinite(value) else "Available"})
    interpretation = []
    if pd.notna(last.rsi_14):
        interpretation.append(f"RSI14 {last.rsi_14:.2f}: {'upper momentum band (>55)' if last.rsi_14 > 55 else 'lower momentum band (<45)' if last.rsi_14 < 45 else 'middle band (45–55)'}. These are descriptive thresholds, not probabilities.")
    if pd.notna(last.macd_histogram):
        previous = frame.macd_histogram.iloc[-2] if len(frame) > 1 else np.nan
        change = "increasing" if last.macd_histogram > previous else "decreasing" if last.macd_histogram < previous else "unchanged/undefined"
        interpretation.append(f"MACD histogram is {'positive' if last.macd_histogram > 0 else 'negative' if last.macd_histogram < 0 else 'zero'} and {change}; sign and change describe different aspects of momentum.")
    if pd.notna(last.roc_10):
        interpretation.append(f"Close changed {last.roc_10:+.2f}% over ten observed intervals.")
    events = []
    for kind, direction in (("low", 1), ("high", -1)):
        points = [p for p in pivots if p.kind == kind]
        for first, second in zip(points, points[1:]):
            if not 5 <= second.index - first.index <= 60:
                continue
            atr = float(frame.atr_14.iloc[second.confirmed_at])
            if not np.isfinite(atr) or direction * (second.price - first.price) >= -.25 * atr:
                continue
            for column, label, minimum in (("rsi_14", "RSI", 2.), ("macd", "MACD", .02 * atr)):
                a, b = float(frame[column].iloc[first.index]), float(frame[column].iloc[second.index])
                if not np.isfinite(a + b) or direction * (b - a) < minimum:
                    continue
                events.append({"id": f"div-{label}-{kind}-{second.timestamp}", "family": "momentum",
                    "name": f"{'Bullish' if direction == 1 else 'Bearish'} {label} divergence", "status": "Confirmed-pivot observation",
                    "formed_at": second.timestamp, "detected_at": second.detected_at, "index": second.confirmed_at,
                    "price": second.price, "direction": direction, "coordinates": [[first.timestamp, first.price], [second.timestamp, second.price]],
                    "evidence": f"Price {first.price:.4f} → {second.price:.4f}; {label} {a:.4f} → {b:.4f}, on 5–60-bar-separated pivots. Available only after second-pivot confirmation; reversal not guaranteed.", "rule_version": RULE_VERSION})
    return {"facts": facts, "interpretation": interpretation, "rule_version": RULE_VERSION}, events


def head_shoulders(frame, pivots, shoulder_tolerance_atr=1.0, head_margin_atr=0.5, expiry=40):
    """Head-and-shoulders (bearish) and inverse (bullish) from five alternating confirmed pivots.

    Shape: shoulder · trough · head · trough · shoulder (mirrored for inverse). The
    formation is knowable only when the right shoulder pivot is confirmed. The
    neckline through the two intervening pivots is frozen at that moment; later
    breaks are judged against that frozen line. No refit with later data.
    """
    events, ordered = [], sorted(pivots, key=lambda p: p.index)
    for direction, outer in ((-1, "high"), (1, "low")):
        name = "Head and shoulders" if direction == -1 else "Inverse head and shoulders"
        for j in range(len(ordered) - 4):
            seq = ordered[j:j + 5]
            kinds = [p.kind for p in seq]
            inner = "low" if outer == "high" else "high"
            if kinds != [outer, inner, outer, inner, outer]:
                continue
            ls, t1, head, t2, rs = seq
            known = rs.confirmed_at
            if known >= len(frame):
                continue
            atr = float(frame.atr_14.iloc[known])
            span = rs.index - ls.index
            if not np.isfinite(atr) or atr <= 0 or not 10 <= span <= 150:
                continue
            sign = -direction  # +1 when the outer points are highs
            if sign * (head.price - max(ls.price, rs.price, key=lambda x: sign * x)) < head_margin_atr * atr:
                continue
            if abs(ls.price - rs.price) > shoulder_tolerance_atr * atr:
                continue
            # Rough symmetry: neither shoulder-to-head leg more than 2.5x the other.
            left, right = head.index - ls.index, rs.index - head.index
            if max(left, right) > 2.5 * min(left, right):
                continue
            slope = (t2.price - t1.price) / (t2.index - t1.index)
            neck = lambda i: t1.price + slope * (i - t1.index)
            depth = sign * (head.price - neck(head.index))
            if depth < 1.5 * atr or abs(slope) * span > depth:  # neckline must be flatter than the pattern is deep
                continue
            # The pattern is void if price already closed through the neckline before it was knowable.
            if any(sign * (frame.close.iloc[i] - neck(i)) < -0.1 * atr for i in range(rs.index, known)):
                continue
            base = {"id": f"hs-{outer}-{ls.index}-{rs.index}", "family": "chart", "name": name,
                "formed_at": rs.timestamp, "formation_start": ls.timestamp, "direction": direction,
                "coordinates": [[p.timestamp, p.price] for p in seq], "rule_version": RULE_VERSION,
                "neckline": float(neck(known)),
                "measured_move": float(depth),
                "geometry": {"head_margin_atr": float(sign * (head.price - max(ls.price, rs.price, key=lambda x: sign * x)) / atr),
                    "shoulder_difference_atr": float(abs(ls.price - rs.price) / atr), "neckline_slope_per_observation": float(slope),
                    "depth_atr": float(depth / atr), "span": int(span), "reference_atr": atr},
                "evidence": f"Five alternating confirmed pivots; head beyond both shoulders by >= {head_margin_atr} ATR; shoulders within {shoulder_tolerance_atr} ATR; "
                            f"neckline frozen at right-shoulder confirmation; break needs a close 0.1 ATR through the neckline. Measured move {depth:.2f} is a reference distance, not a forecast."}
            for i in range(known, min(len(frame), known + expiry + 1)):
                close = float(frame.close.iloc[i])
                level = float(neck(i))
                status = None
                if sign * (close - head.price) > 0:
                    status = "Invalidated: beyond head"
                elif sign * (level - close) > 0.1 * atr:
                    status = "Confirmed neckline break"
                elif i == known + expiry:
                    status = "Expired"
                elif i == known:
                    status = "Developing"
                if status:
                    events.append({**base, "status": status, "index": i, "detected_at": _date(frame, i),
                        "price": float(frame.high.iloc[i]), "level": level,
                        "boundary_coordinates": {"neckline": [[t1.timestamp, t1.price], [_date(frame, i), level]]},
                        **({"measured_target": level - sign * depth} if status == "Confirmed neckline break" else {})})
                    if status != "Developing":
                        break
    return sorted(events, key=lambda e: (e["index"], e["id"]))
