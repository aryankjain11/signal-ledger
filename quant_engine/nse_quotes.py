"""Normalize offline NSE security-history exports, without guessing or price repair."""
import re

import pandas as pd

ALIASES = {"open price": "open", "high price": "high", "low price": "low",
           "close price": "close", "total traded quantity": "volume"}
MONTHS = {name: f"{i:02}" for i, name in enumerate(
    ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}
NUMBER = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+|(?:\d{1,3}(?:,\d{3})+|\d{1,2}(?:,\d{2})*,\d{3})(?:\.\d*)?)")
QUOTE_NAME = re.compile(r"Quote-Equity-(?P<symbol>[A-Z0-9&._-]{1,40})-(?P<series>[A-Z0-9]{1,4})-\d{2}-\d{2}-\d{4}-\d{2}-\d{2}-\d{4}(?: \(\d+\))?\.(?:csv|xlsx)", re.IGNORECASE)


def header_name(value):
    return " ".join(str(value).lstrip("\ufeff").strip().casefold().split())


def normalize_quote(frame, filename):
    """Return the original frame for standard OHLCV, or a normalized quote export.

    Scope recognition to the security-history signature, so generic CSV dates and
    comma formatting retain their strict contract. Extra market fields are ignored.
    """
    frame = frame.copy()
    frame.columns = [header_name(c) for c in frame.columns]
    if frame.columns.duplicated().any():
        raise ValueError("Column names must be unique after ignoring case and spaces.")
    markers = {"prev. close", "prev.close", "previous close", "ltp", "vwap", "52 week high", "52 weeks high"}
    if not {"date", "series"}.issubset(frame.columns) or not markers.intersection(frame.columns):
        return frame, {}, []
    frame = frame.rename(columns=ALIASES)
    if frame.columns.duplicated().any():
        raise ValueError("NSE export has ambiguous duplicate OHLCV column aliases.")
    required = ["date", "open", "high", "low", "close", "volume"]
    if any(c not in frame for c in required):
        raise ValueError("NSE security-history export needs DATE, OPEN, HIGH, LOW, CLOSE and VOLUME (traded quantity). VALUE and LTP are not substitutes.")
    if frame.empty:
        raise ValueError("NSE security-history export contains no observations.")
    series = frame["series"].fillna("").astype(str).str.strip().str.upper()
    if not series.eq("EQ").all():
        raise ValueError("NSE security-history uploads currently require EQ series on every row; mixed or other series cannot be combined.")
    normalized_dates = []
    for value in frame["date"]:
        if isinstance(value, str):
            value = value.strip()
            match = re.fullmatch(r"(\d{2})-([A-Za-z]{3})-(\d{4})", value)
            if match and match[2].casefold() in MONTHS:
                value = f"{match[3]}-{MONTHS[match[2].casefold()]}-{match[1]}"
            elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError("NSE dates must use DD-Mon-YYYY or YYYY-MM-DD; ambiguous numeric dates are not guessed.")
        normalized_dates.append(value)
    frame["date"] = normalized_dates
    for column in required[1:]:
        # Validate grouping before removing commas: 12,34 must not become 1234.
        values = frame[column].astype(str).str.strip()
        if not values.map(lambda v: bool(NUMBER.fullmatch(v))).all():
            raise ValueError(f"NSE {column.upper()} has missing or invalid numbers/comma grouping. No missing values were filled.")
        frame[column] = pd.to_numeric(values.str.replace(",", "", regex=False), errors="coerce")
    if (frame["volume"] % 1 != 0).any():
        raise ValueError("NSE VOLUME must be a whole number of shares.")
    metadata = {"input_format": "NSE security-history CSV/XLSX", "file_series": "EQ",
                "detected_nse_quote": True, "symbol_basis": "User research label; no symbol in export",
                "normalization": {"adapter": "nse-security-history/1", "dates": "DD-Mon-YYYY or ISO to session dates",
                                  "numbers": "Validated Indian/international comma grouping removed from OHLCV",
                                  "price_column": "CLOSE, not LTP or PREV. CLOSE", "volume_column": "VOLUME / Total Traded Quantity, not VALUE",
                                  "extra_columns": "Ignored; no adjustment or missing-bar filling"}}
    warnings = ["Detected NSE security-history format: converted date/number formatting; used CLOSE and traded share quantity. Extra columns were ignored. No price adjustment was applied."]
    name = str(filename).replace("\\", "/").rsplit("/", 1)[-1]
    match = QUOTE_NAME.fullmatch(name)
    if match:
        if match["series"].upper() != "EQ":
            raise ValueError("Download filename series conflicts with EQ records inside the file.")
        metadata.update(file_symbol=match["symbol"].upper(), symbol_basis="Download filename only; not independently authenticated")
        warnings.append("Stock label inferred from the download filename; this export has no authenticated security identity or ISIN.")
    if "symbol" in frame:
        supplied = frame["symbol"].fillna("").astype(str).str.strip().str.upper()
        if supplied.eq("").any() or supplied.nunique() != 1:
            raise ValueError("NSE export must contain exactly one nonblank symbol.")
        if match and supplied.iloc[0] != metadata["file_symbol"]:
            raise ValueError("Symbol column conflicts with the download filename; check security identity.")
        frame["symbol"] = supplied
        metadata.update(file_symbol=supplied.iloc[0], symbol_basis="Symbol column supplied by user; not independently authenticated")
    return frame, metadata, warnings
