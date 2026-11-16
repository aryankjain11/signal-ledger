"""Provider-independent daily-data acquisition.

A provider returns plain daily OHLCV rows. They are then passed through exactly the
same validation (`data.load_bars`) as an uploaded file, so a fetched dataset gets
the same checks, hashes and passport as a CSV. Nothing is filled or invented:
rows the provider returns with missing prices are dropped and counted, and a
still-forming current session is excluded.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pandas as pd

IST = ZoneInfo("Asia/Kolkata")
# Same conservative cut-off the calendar module uses for "today's bar is complete".
COMPLETED_AFTER = time(18, 0)
EXCHANGE_SUFFIX = {"NSE": ".NS", "BSE": ".BO", "As typed": ""}
PERIODS = {"1 year": "1y", "2 years": "2y", "5 years": "5y", "10 years": "10y", "Max available": "max"}
PROVIDER_ADJUSTMENT = "Split-adjusted by provider; dividends not adjusted"


@dataclass
class FetchResult:
    provider_symbol: str
    display_symbol: str
    exchange: str
    csv_bytes: bytes
    rows: int
    first: str
    last: str
    notes: list[str] = field(default_factory=list)


def provider_symbol(symbol: str, exchange: str) -> str:
    """Map a user ticker to Yahoo's convention without guessing beyond the suffix."""
    clean = symbol.strip().upper().replace(" ", "")
    if not clean:
        raise ValueError("Enter a ticker symbol, for example RELIANCE or TCS.")
    # Letters, digits and the few symbols NSE tickers use (M&M, BAJAJ-AUTO, ^NSEI, RELIANCE.NS).
    if len(clean) > 30 or not all(c.isalnum() or c in "&-^._" for c in clean):
        raise ValueError("That does not look like a ticker symbol.")
    if exchange not in EXCHANGE_SUFFIX:
        raise ValueError(f"Unsupported exchange: {exchange}")
    if clean.startswith("^") or "." in clean or exchange == "As typed":
        return clean
    return clean + EXCHANGE_SUFFIX[exchange]


def _yahoo_history(ticker: str, period: str) -> pd.DataFrame:  # pragma: no cover - network
    import yfinance as yf
    return yf.Ticker(ticker).history(period=period, interval="1d", auto_adjust=False,
                                     actions=False, raise_errors=True)


def normalize_history(raw: pd.DataFrame, now: datetime | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Turn a provider frame into completed daily date/open/high/low/close/volume rows."""
    if raw is None or raw.empty:
        raise ValueError("The provider returned no daily rows for this symbol. Check the ticker and exchange.")
    frame = raw.rename(columns=str.lower)
    missing = [c for c in ("open", "high", "low", "close", "volume") if c not in frame]
    if missing:
        raise ValueError(f"Provider response lacks {', '.join(missing)}.")
    index = pd.DatetimeIndex(frame.index)
    if index.tz is not None:
        index = index.tz_convert(IST).tz_localize(None)
    frame = frame[["open", "high", "low", "close", "volume"]].copy()
    frame.index = index.normalize()
    notes = []
    blank = frame[["open", "high", "low", "close"]].isna().any(axis=1) | (frame[["open", "high", "low", "close"]] <= 0).any(axis=1)
    if blank.any():
        notes.append(f"{int(blank.sum())} provider row(s) without valid prices were dropped, not filled.")
        frame = frame[~blank]
    frame["volume"] = frame.volume.fillna(0)
    if frame.index.duplicated().any():
        notes.append(f"{int(frame.index.duplicated().sum())} duplicate provider date(s) dropped; first kept.")
        frame = frame[~frame.index.duplicated(keep="first")]
    now = (now or datetime.now(IST)).astimezone(IST)
    if len(frame) and frame.index[-1].date() >= now.date() and now.time() < COMPLETED_AFTER:
        frame = frame.iloc[:-1]
        notes.append(f"Today's session ({now.date()}) is still forming before {COMPLETED_AFTER:%H:%M} IST and was excluded.")
    # Provider rounding can leave high/low a hair inside open/close; widen only by that rounding.
    eps = frame[["open", "close"]].abs().max(axis=1) * 1e-6
    over = frame[["open", "close"]].max(axis=1) - frame.high
    under = frame.low - frame[["open", "close"]].min(axis=1)
    fix = ((over > 0) & (over <= eps)) | ((under > 0) & (under <= eps))
    if fix.any():
        frame.loc[:, "high"] = frame[["high", "open", "close"]].max(axis=1).where(fix, frame.high)
        frame.loc[:, "low"] = frame[["low", "open", "close"]].min(axis=1).where(fix, frame.low)
        notes.append(f"{int(fix.sum())} row(s) had high/low inside open/close by rounding only (<0.0001%) and were widened to contain them.")
    frame.index.name = "date"
    return frame, notes


def fetch_daily(symbol: str, exchange: str = "NSE", period: str = "5 years", *,
                history=None, now: datetime | None = None) -> FetchResult:
    ticker = provider_symbol(symbol, exchange)
    history = history or _yahoo_history
    if period not in PERIODS:
        raise ValueError(f"Unsupported period: {period}")
    try:
        raw = history(ticker, PERIODS[period])
    except ModuleNotFoundError as exc:
        raise ValueError("Ticker fetching needs the yfinance package: run pip install -r requirements.txt") from exc
    except Exception as exc:
        raise ValueError(f"Could not fetch {ticker} from Yahoo Finance: {exc}") from exc
    frame, notes = normalize_history(raw, now)
    if len(frame) < 3:
        raise ValueError(f"Only {len(frame)} completed daily rows were returned for {ticker}.")
    out = frame.reset_index()
    out["date"] = out.date.dt.strftime("%Y-%m-%d")
    display = ticker.split(".")[0].lstrip("^") if exchange != "As typed" else ticker
    return FetchResult(ticker, display, exchange, out.to_csv(index=False).encode(), len(out),
                       out.date.iloc[0], out.date.iloc[-1], notes)
