"""Daily session-date ingestion. Never fill, aggregate duplicates, or mix adjustments."""
from hashlib import sha256
from io import BytesIO
import csv
from io import StringIO
import re

import numpy as np
import pandas as pd

from .models import ValidatedData

REQUIRED = ["open", "high", "low", "close", "volume"]


def validate_daily(raw: pd.DataFrame, source_hash: str = "", *, min_rows: int = 3) -> ValidatedData:
    if type(min_rows) is not int or not 1 <= min_rows <= 50_000:
        raise ValueError("Minimum row count must be a positive integer up to 50,000.")
    frame = raw.copy()
    frame.columns = [str(c).strip().lower() for c in frame.columns]
    if frame.columns.duplicated().any():
        raise ValueError("Column names must be unique after ignoring case and spaces.")
    date_names = [c for c in ("date", "timestamp", "datetime") if c in frame]
    if len(date_names) != 1 or any(c not in frame for c in REQUIRED):
        raise ValueError("Expected one date/timestamp/datetime column and open, high, low, close, volume.")
    if not min_rows <= len(frame) <= 50_000:
        raise ValueError(f"Supply between {min_rows} and 50,000 daily observations for one symbol.")
    if "symbol" in frame:
        if frame.symbol.isna().any() or frame.symbol.astype(str).str.strip().eq("").any():
            raise ValueError("Symbol values cannot be missing or blank when the column is supplied.")
        if frame.symbol.nunique(dropna=False) != 1:
            raise ValueError("Only one symbol per file is supported.")
    dates = frame[date_names[0]]
    if dates.isna().any():
        raise ValueError("Dates cannot be missing.")
    # CSV dates are intentionally strict: no locale guessing or implicit timezone conversion.
    for value in dates:
        if isinstance(value, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value.strip()):
            raise ValueError("Daily CSV dates must use YYYY-MM-DD, without times or timezones.")
        if isinstance(value, (int, float, np.number)):
            raise ValueError("Numeric date serials are ambiguous; use Excel date cells or YYYY-MM-DD.")
    try:
        index = pd.DatetimeIndex(pd.to_datetime(dates, errors="raise", format="ISO8601"))
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid dates; use daily session dates in YYYY-MM-DD format.") from exc
    if index.tz is not None or (index != index.normalize()).any():
        raise ValueError("This version supports timezone-free daily session dates only.")
    if index.duplicated().any():
        raise ValueError("Duplicate session dates found; provide one candle per session.")
    frame.index = index
    warnings = []
    if not index.is_monotonic_increasing:
        warnings.append("Rows were sorted by session date; no values were filled.")
    result = frame[REQUIRED].apply(pd.to_numeric, errors="coerce").astype(float).sort_index()
    result.index.name = "date"
    if not np.isfinite(result.to_numpy()).all():
        raise ValueError("OHLCV must contain finite numeric values with no missing cells.")
    if (result[REQUIRED[:4]] <= 0).any().any() or (result.volume < 0).any():
        raise ValueError("Prices must be positive and volume must be nonnegative.")
    bad = ((result.high < result[["open", "close", "low"]].max(axis=1)) |
           (result.low > result[["open", "close", "high"]].min(axis=1)))
    if bad.any():
        raise ValueError(f"Invalid OHLC relationships on {result.index[bad][0].date()}.")
    if "adj close" in frame or "adjusted close" in frame:
        warnings.append("Adjusted-close column ignored. All four OHLC columns must use one consistent adjustment basis.")
    if len(result) < 60:
        warnings.append("Fewer than 60 sessions: long indicators and baseline signals may be unavailable.")
    if (result.volume == 0).any():
        warnings.append("Zero-volume sessions exist; volume evidence and liquidity estimates may be unreliable.")
    gaps = result.index.to_series().diff().dt.days
    if (gaps > 4).any():
        warnings.append("Gaps longer than four calendar days exist; verify against the exchange calendar. Nothing was filled.")
    if (result.close.pct_change().abs() > 0.25).any():
        warnings.append("A close-to-close move exceeds 25%; check corporate actions and data quality before research.")
    warnings.append("No exchange calendar is configured: missing sessions and holidays cannot be distinguished.")
    return ValidatedData(result, warnings, source_hash)


def load_bars(content: bytes, filename: str) -> ValidatedData:
    from .nse_quotes import header_name, normalize_quote
    if len(content) > 20 * 1024 * 1024:
        raise ValueError("File exceeds the 20 MB limit.")
    try:
        if filename.lower().endswith(".csv"):
            header = next(csv.reader(StringIO(content.decode("utf-8-sig"))), [])
            cleaned = [header_name(c) for c in header]
            if len(cleaned) != len(set(cleaned)):
                raise ValueError("CSV column names must be unique after ignoring case and spaces.")
            frame = pd.read_csv(BytesIO(content))
        elif filename.lower().endswith(".xlsx"):
            frame = pd.read_excel(BytesIO(content), engine="openpyxl")
        else:
            raise ValueError("Upload a CSV or XLSX file.")
    except (pd.errors.ParserError, UnicodeError, OSError, ImportError) as exc:
        raise ValueError("Could not read file; check its encoding and format.") from exc
    frame, metadata, warnings = normalize_quote(frame, filename)
    result = validate_daily(frame, sha256(content).hexdigest())
    result.metadata.update(metadata)
    result.warnings = warnings + result.warnings
    symbol_columns = [c for c in frame.columns if str(c).strip().casefold() == "symbol"]
    if symbol_columns:
        result.metadata["file_symbol"] = str(frame[symbol_columns[0]].iloc[0]).strip()
    return result


def completed_weeks(bars: pd.DataFrame) -> pd.DataFrame:
    """Discard the latest calendar week conservatively; no exchange calendar inference."""
    periods = bars.index.to_period("W-SUN")
    prior = bars.loc[periods < periods[-1]]
    if prior.empty:
        return bars.iloc[:0].copy()
    grouped = prior.groupby(prior.index.to_period("W-SUN"))
    result = grouped.agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    result.index = pd.DatetimeIndex(grouped.apply(lambda x: x.index[-1]).to_numpy())
    return result

