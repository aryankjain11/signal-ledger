"""Small geometric observations, with explicit formation and knowledge times."""
import pandas as pd

from .models import Pivot


def swings(frame: pd.DataFrame, window: int = 3) -> list[Pivot]:
    result = []
    for i in range(window, len(frame) - window):
        block = frame.iloc[i - window:i + window + 1]
        for kind, column, extreme in (("high", "high", block.high.max()),
                                       ("low", "low", block.low.min())):
            price = float(frame[column].iloc[i])
            # Strict uniqueness keeps flat plateaus from becoming spurious pivots.
            if price == extreme and int((block[column] == price).sum()) == 1:
                result.append(Pivot(kind, i, i + window, price,
                                    frame.index[i].date().isoformat(),
                                    frame.index[i + window].date().isoformat()))
    return sorted(result, key=lambda p: (p.confirmed_at, p.kind))


def market_structure(pivots: list[Pivot]) -> tuple[str, str]:
    highs = [p for p in pivots if p.kind == "high"]
    lows = [p for p in pivots if p.kind == "low"]
    if len(highs) < 2 or len(lows) < 2:
        return "Insufficient structure", "Need two confirmed highs and two confirmed lows."
    high_change = highs[-1].price - highs[-2].price
    low_change = lows[-1].price - lows[-2].price
    high = "HH" if high_change > 0 else "LH" if high_change < 0 else "equal highs"
    low = "HL" if low_change > 0 else "LL" if low_change < 0 else "equal lows"
    trend = "Bullish structure" if high_change > 0 and low_change > 0 else (
        "Bearish structure" if high_change < 0 and low_change < 0 else "Mixed / range structure")
    return trend, f"Latest confirmed swings: {high} + {low}."


def support_resistance(frame: pd.DataFrame, pivots: list[Pivot]) -> list[dict]:
    atr = frame.atr_14.iloc[-1]
    if pd.isna(atr) or atr <= 0:
        return []
    tolerance = float(atr * 0.5)
    clusters: list[dict] = []
    for pivot in sorted(pivots[-100:], key=lambda p: p.price):
        if clusters and abs(pivot.price - clusters[-1]["center"]) <= tolerance:
            cluster = clusters[-1]
            cluster["prices"].append(pivot.price)
            cluster["center"] = sum(cluster["prices"]) / len(cluster["prices"])
        else:
            clusters.append({"center": pivot.price, "prices": [pivot.price]})
    close = float(frame.close.iloc[-1])
    zones = [{"low": c["center"] - tolerance / 2, "high": c["center"] + tolerance / 2,
              "center": c["center"], "pivot_count": len(c["prices"]),
              "role": "Support" if c["center"] <= close else "Resistance"}
             for c in clusters if len(c["prices"]) >= 2]
    return sorted(zones, key=lambda z: abs(z["center"] - close))[:6]


def candle_events(frame: pd.DataFrame) -> list[dict]:
    events = []
    for i in range(len(frame)):
        bar = frame.iloc[i]
        names = []
        width = bar.high - bar.low
        if width > 0 and abs(bar.close - bar.open) <= 0.1 * width:
            names.append("Doji")
        if i > 0:
            previous = frame.iloc[i - 1]
            if (previous.close < previous.open and bar.close > bar.open and
                    bar.open <= previous.close and bar.close >= previous.open):
                names.append("Bullish engulfing")
            if (previous.close > previous.open and bar.close < bar.open and
                    bar.open >= previous.close and bar.close <= previous.open):
                names.append("Bearish engulfing")
        for name in names:
            events.append({"id": f"candle-{i}-{name}", "name": name,
                           "status": "Observed geometry", "index": i,
                           "formed_at": frame.index[i].date().isoformat(),
                           "detected_at": frame.index[i].date().isoformat(),
                           "price": float(bar.high),
                           "evidence": "Body/wick geometry only; no success probability or standalone trade signal."})
    return events


def double_patterns(frame: pd.DataFrame, pivots: list[Pivot]) -> list[dict]:
    """Emit immutable state events rather than rewriting an earlier observation."""
    events = []
    for kind, name, direction in (("low", "Double bottom", 1), ("high", "Double top", -1)):
        points = [p for p in pivots if p.kind == kind]
        for first, second in zip(points, points[1:]):
            if not 5 <= second.index - first.index <= 60:
                continue
            known = second.confirmed_at
            atr = float(frame.atr_14.iloc[known])
            if pd.isna(atr) or atr <= 0 or abs(first.price - second.price) > 0.75 * atr:
                continue
            inside = frame.iloc[first.index + 1:second.index]
            neckline = float(inside.high.max() if direction == 1 else inside.low.min())
            rebound = (neckline - max(first.price, second.price) if direction == 1
                       else min(first.price, second.price) - neckline)
            if rebound < 1.5 * atr:
                continue
            middle_date = inside.high.idxmax() if direction == 1 else inside.low.idxmin()
            base = {"id": f"double-{kind}-{first.index}-{second.index}", "name": name,
                    "formed_at": second.timestamp, "price": second.price,
                    "neckline": neckline, "direction": direction,
                    "coordinates": [[first.timestamp, first.price],
                                    [middle_date.date().isoformat(), neckline],
                                    [second.timestamp, second.price]],
                    "evidence": "Consecutive same-kind confirmed pivots, 5–60 sessions apart; difference <= 0.75 ATR; intervening recovery >= 1.5 ATR. Geometry is unvalidated."}
            # If confirmation/invalidation already happened during pivot confirmation,
            # expose it only NOW, when all geometric prerequisites became knowable.
            terminal = None
            for i in range(second.index + 1, min(len(frame), known + 41)):
                close = float(frame.close.iloc[i])
                invalid = (close < min(first.price, second.price) - 0.5 * atr if direction == 1
                           else close > max(first.price, second.price) + 0.5 * atr)
                confirmed = direction * (close - neckline) > 0.1 * atr
                if invalid or confirmed:
                    terminal = (max(known, i), "Invalidated" if invalid else "Confirmed")
                    break
            if terminal is None or terminal[0] > known:
                events.append({**base, "status": "Developing", "index": known,
                               "detected_at": frame.index[known].date().isoformat()})
            if terminal is not None:
                i, status = terminal
                events.append({**base, "status": status, "index": i,
                               "detected_at": frame.index[i].date().isoformat()})
            elif len(frame) > known + 40:
                i = known + 40
                events.append({**base, "status": "Expired", "index": i,
                               "detected_at": frame.index[i].date().isoformat()})
    return sorted(events, key=lambda e: (e["index"], e["id"]))
