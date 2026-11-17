"""Watchlist scanner: the same analysis as the Analyze page, one summary row per stock."""
from __future__ import annotations

import math
from concurrent.futures import ThreadPoolExecutor

from .analysis import analyze
from .data import load_bars
from .market_read import market_read
from .models import Settings
from .providers import fetch_daily

# NIFTY 50 constituents after the 30 Sep 2026 change (BSE in, WIPRO out), per NSE Indices'
# 10 Aug 2026 notice and published weight lists. Index membership changes twice a year: edit freely.
NIFTY_50_AS_OF = "30 Sep 2026"
NIFTY_50 = ["HDFCBANK", "ICICIBANK", "RELIANCE", "BHARTIARTL", "LT", "SBIN", "INFY", "AXISBANK", "KOTAKBANK",
            "BAJFINANCE", "M&M", "ITC", "ETERNAL", "TCS", "SUNPHARMA", "TITAN", "HINDUNILVR", "TATASTEEL", "MARUTI",
            "NTPC", "ADANIPORTS", "BEL", "HINDALCO", "SHRIRAMFIN", "BSE", "HCLTECH", "ULTRACEMCO", "JSWSTEEL",
            "POWERGRID", "BAJAJ-AUTO", "GRASIM", "INDIGO", "ASIANPAINT", "COALINDIA", "BAJAJFINSV", "ADANIENT",
            "EICHERMOT", "NESTLEIND", "TECHM", "ONGC", "APOLLOHOSP", "TRENT", "SBILIFE", "CIPLA", "DRREDDY",
            "MAXHEALTH", "JIOFIN", "TATACONSUM", "TMPV", "HDFCLIFE"]
MAX_SYMBOLS = 100
VERDICT_ORDER = {"Bullish": 0, "Leaning bullish": 1, "Mixed / conflicting": 2, "Leaning bearish": 3,
                 "Bearish": 4, "Insufficient evidence": 5}
LIVE = ("Developing", "Confirmed", "Breakout", "Breakdown", "Retest held", "Continuation", "Confirmed upward break",
        "Confirmed downward break", "Confirmed neckline break")


def parse_watchlist(text: str) -> list[str]:
    seen, out = set(), []
    for raw in text.replace("\n", ",").replace(";", ",").replace(" ", ",").split(","):
        symbol = raw.strip().upper()
        if symbol and symbol not in seen:
            seen.add(symbol)
            out.append(symbol)
    return out[:MAX_SYMBOLS]


def _num(value, digits=2):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return round(value, digits) if math.isfinite(value) else None


def summarize(symbol: str, data, recent: int = 10, provider_symbol: str = "") -> dict:
    analysis = analyze(data, Settings())
    read = market_read(analysis)
    frame = analysis.frame
    last = frame.iloc[-1]
    close = float(last.close)
    day = 100 * (close / frame.close.iloc[-2] - 1) if len(frame) > 1 else None
    month = 100 * (close / frame.close.iloc[-22] - 1) if len(frame) > 22 else None
    high52 = _num(last.get("high_52w"))
    reads = {r["timeframe"]: r for r in read["mtf"]["reads"]}
    latest = {}
    for event in sorted(analysis.events, key=lambda e: e["index"]):
        latest[event["id"]] = event
    live = [e for e in latest.values() if e["index"] >= len(frame) - recent and e.get("direction") in (1, -1)
            and e["status"].startswith(LIVE)]
    newest = max(live, key=lambda e: e["index"]) if live else None
    return {
        "Symbol": symbol, "As of": frame.index[-1].date().isoformat(), "Close": _num(close),
        "Day %": _num(day), "1M %": _num(month),
        "Market read": read["verdict"], "Up votes": read["bullish"], "Down votes": read["bearish"],
        "Daily trend": reads["Daily"]["label"], "Weekly": reads["Weekly"]["label"], "Monthly": reads["Monthly"]["label"],
        "Alignment": short_alignment(read["mtf"]["higher_signal"], reads["Daily"]["signal"]),
        "RSI": _num(last.get("rsi_14"), 1), "ADX": _num(last.get("adx_14"), 1),
        "Rel. volume": _num(last.get("relative_volume")),
        "From 52w high %": _num(100 * (close / high52 - 1)) if high52 else None,
        "Recent pattern": (f"{'▲' if newest['direction'] == 1 else '▼'} {newest['name']} · {newest['status']} · {newest['detected_at']}"
                           if newest else ""),
        "Recent patterns (n)": len(live),
        "Breakout setup": analysis.setup["status"],
        "Sessions": len(frame), "Error": "",
        "ATR": _num(last.get("atr_14"), 4), "Provider symbol": provider_symbol or symbol,
    }


def short_alignment(higher, daily):
    if higher is None or daily is None:
        return "n/a"
    if higher == 0:
        return "No larger trend"
    word = "up" if higher == 1 else "down"
    if daily == higher:
        return f"Aligned {word}"
    if daily == -higher:
        return f"Counter-trend (larger {word})"
    return f"Pause in {word}trend"


def _fetch(symbol, exchange, period, history):
    try:
        return symbol, fetch_daily(symbol, exchange, period, history=history), None
    except ValueError as exc:
        return symbol, None, str(exc)


def scan(symbols, exchange="NSE", period="2 years", *, history=None, workers=6, progress=None) -> list[dict]:
    """Fetch in parallel (network-bound), analyze sequentially; failures become rows with an error."""
    rows = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        fetched = list(pool.map(lambda s: _fetch(s, exchange, period, history), symbols))
    for i, (symbol, result, error) in enumerate(fetched):
        if progress:
            progress(i, len(fetched), symbol)
        if result is None:
            rows.append({"Symbol": symbol, "Error": error})
            continue
        try:
            data = load_bars(result.csv_bytes, f"{result.provider_symbol}.csv")
            rows.append(summarize(result.display_symbol, data, provider_symbol=result.provider_symbol))
        except Exception as exc:  # one bad series must not sink the scan
            rows.append({"Symbol": symbol, "Error": f"Analysis failed: {exc}"})
    return rows
