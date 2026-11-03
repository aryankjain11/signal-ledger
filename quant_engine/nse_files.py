"""Offline NSE CM UDiFF-style CSV/ZIP adapter; no network, extraction or price repair.

Header conformity is not proof of origin. Current scope is one EQ series/security
at a time. Test with synthetic reports; real-file/provider acceptance is separate.
"""
import csv
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO, StringIO
import json
from pathlib import PurePosixPath
import re
import stat
import zipfile

import pandas as pd

from .data import validate_daily
from .datasets import Instrument, attach_passport

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_INPUT_BYTES = 40 * 1024 * 1024
MAX_EXPANDED_BYTES = 80 * 1024 * 1024
MAX_REPORTS = 1000
MAX_TOTAL_ROWS = 1_000_000
FIELDS = {"traddt": "date", "tckrsymb": "symbol", "sctysrs": "series", "isin": "isin",
          "opnpric": "open", "hghpric": "high", "lwpric": "low", "clspric": "close",
          "ttltradgvol": "volume", "sgmt": "segment", "src": "source"}
REPORT_NAME = re.compile(r"BhavCopy_NSE_CM_0_0_0_(\d{8})_([FP])_0000\.csv", re.IGNORECASE)


def _safe_name(name):
    return PurePosixPath(str(name).replace("\\", "/")).name[:240]


def _csv_records(content: bytes, name: str):
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("A report exceeds the 20 MB uncompressed limit.")
    try:
        text = content.decode("utf-8-sig")
        header = next(csv.reader(StringIO(text)))
    except (UnicodeError, StopIteration, csv.Error) as exc:
        raise ValueError("Expected a nonempty UTF-8 UDiFF CSV report.") from exc
    columns = [c.strip().casefold() for c in header]
    if len(columns) != len(set(columns)):
        raise ValueError("Report contains duplicate column names after normalization.")
    missing = set(FIELDS) - set(columns)
    if missing:
        raise ValueError("Unsupported report schema; missing UDiFF fields: " + ", ".join(sorted(missing)))
    try:
        raw = pd.read_csv(StringIO(text), dtype=str, keep_default_na=False, nrows=MAX_TOTAL_ROWS + 1)
    except (pd.errors.ParserError, ValueError) as exc:
        raise ValueError("Could not parse the UDiFF report.") from exc
    if raw.empty or len(raw) > MAX_TOTAL_ROWS:
        raise ValueError("Report is empty or exceeds the row limit.")
    raw.columns = columns
    if "ssnid" in raw and raw["ssnid"].str.strip().str.upper().str.startswith("I").any():
        raise ValueError("Interim/provisional sessions are not supported; supply completed final reports.")
    result = raw[list(FIELDS)].rename(columns=FIELDS).copy()
    for column in result:
        result[column] = result[column].str.strip()
    if not result.date.str.fullmatch(r"\d{4}-\d{2}-\d{2}").all():
        raise ValueError("TradDt must use YYYY-MM-DD exchange-session dates.")
    try:
        pd.to_datetime(result.date, format="%Y-%m-%d", errors="raise")
    except ValueError as exc:
        raise ValueError("TradDt contains an invalid calendar date.") from exc
    if result.date.nunique() != 1:
        raise ValueError("Each daily report must contain exactly one TradDt; upload multiple daily reports for history.")
    if not result.segment.str.upper().eq("CM").all() or not result.source.str.upper().eq("NSE").all():
        raise ValueError("This adapter requires NSE capital-market reports: Sgmt=CM and Src=NSE.")
    match = REPORT_NAME.fullmatch(_safe_name(name.split("::", 1)[-1]))
    if match and match.group(2).upper() == "P":
        raise ValueError("Provisional report filenames are not supported; supply completed final reports.")
    if match and result.date.iloc[0].replace("-", "") != match.group(1):
        raise ValueError("Report filename date disagrees with TradDt inside the file.")
    result["symbol"] = result.symbol.str.upper()
    result["series"] = result.series.str.upper()
    result["isin"] = result["isin"].str.upper()
    selected = result.loc[result.series.eq("EQ")].copy()
    if not selected.symbol.str.fullmatch(r"[A-Z0-9&._-]{1,40}").all():
        raise ValueError("An EQ row has a missing or unsupported ticker symbol.")
    if not selected["isin"].str.fullmatch(r"[A-Z]{2}[A-Z0-9]{9}[0-9]").all():
        raise ValueError("An EQ row has a missing or malformed 12-character ISIN. Check source identity.")
    record = {"name": name, "sha256": sha256(content).hexdigest(), "bytes": len(content),
              "raw_rows": len(result), "eligible_eq_rows": len(selected), "session": result.date.iloc[0]}
    return selected, record


@dataclass
class ReportBundle:
    rows: pd.DataFrame
    sources: list[dict]
    reports: list[dict]
    source_hash: str

    def instruments(self):
        return [{"symbol": symbol, "series": series, "sessions": group.date.nunique(),
                 "isins": sorted(group["isin"].unique())}
                for (symbol, series), group in self.rows.groupby(["symbol", "series"], sort=True)]

    def select(self, symbol: str, series: str = "EQ", *, is_synthetic: bool = False):
        chosen = self.rows.loc[self.rows.symbol.eq(symbol.upper()) & self.rows.series.eq(series.upper())]
        if chosen.empty:
            raise ValueError("The selected instrument/series is not present in these reports.")
        if chosen["isin"].nunique() != 1:
            raise ValueError("The selected symbol/series has multiple ISINs. Review security changes before combining this history.")
        if chosen.date.duplicated().any():
            raise ValueError("Duplicate sessions for the selected instrument; no rows were merged or dropped.")
        raw = chosen[["date", "open", "high", "low", "close", "volume"]]
        data = validate_daily(raw, self.source_hash, min_rows=1)
        all_dates = sorted({r["session"] for r in self.reports})
        missing = sorted(set(all_dates) - set(chosen.date))
        if missing:
            data.warnings.append(f"Selected security is absent from {len(missing)} uploaded report dates. This does not by itself prove a missing trading session.")
        data.warnings += ["UDiFF OHLC imported as quoted/unadjusted; no split/dividend adjustment was applied.",
                          "ISIN format was checked, not its check digit, listing validity or historical continuity."]
        return attach_passport(data, instrument=Instrument("NSE", symbol.upper(), series.upper(), chosen["isin"].iloc[0]),
                               provider="Synthetic UDiFF-format fixture" if is_synthetic else "User-supplied NSE CM UDiFF-style reports",
                               input_format="NSE CM UDiFF CSV/ZIP; EQ series", adjustment="Synthetic example" if is_synthetic else "Unadjusted OHLC",
                               sources=self.sources, is_synthetic=is_synthetic,
                               source_hash_kind="SHA-256 of the sorted raw-file manifest (each original file has its own hash)",
                               coverage={"report_sessions": len(all_dates), "selected_security_sessions": len(chosen),
                                         "report_dates_without_security": missing, "report_members": self.reports})


def read_reports(files: list[tuple[str, bytes]]) -> ReportBundle:
    if not files or len(files) > MAX_REPORTS:
        raise ValueError("Supply between 1 and 1,000 daily CSV/ZIP files.")
    if sum(len(content) for _, content in files) > MAX_INPUT_BYTES:
        raise ValueError("Combined compressed/input size exceeds 40 MB.")
    rows, reports, sources = [], [], []
    expanded = 0
    raw_count = 0

    def consume(content, name):
        nonlocal expanded, raw_count
        expanded += len(content)
        if expanded > MAX_EXPANDED_BYTES or len(reports) >= MAX_REPORTS:
            raise ValueError("Expanded report bundle exceeds the 80 MB / 1,000 report limit.")
        frame, record = _csv_records(content, name)
        raw_count += record["raw_rows"]
        if raw_count > MAX_TOTAL_ROWS:
            raise ValueError("Combined reports exceed one million raw rows.")
        rows.append(frame)
        reports.append(record)

    for original_name, content in files:
        name = _safe_name(original_name)
        if len(content) > MAX_FILE_BYTES:
            raise ValueError("Each input file must be at most 20 MB.")
        sources.append({"name": name, "sha256": sha256(content).hexdigest(), "bytes": len(content)})
        if name.lower().endswith(".csv"):
            consume(content, name)
        elif name.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(BytesIO(content)) as archive:
                    if len(archive.infolist()) > MAX_REPORTS * 2:
                        raise ValueError("ZIP contains too many entries, including directories.")
                    members = [m for m in archive.infolist() if not m.is_dir()]
                    if not members or len(members) > MAX_REPORTS or len(reports) + len(members) > MAX_REPORTS:
                        raise ValueError("ZIP must contain 1–1,000 CSV reports within the bundle limit.")
                    if sum(m.file_size for m in members) + expanded > MAX_EXPANDED_BYTES:
                        raise ValueError("ZIP expands beyond the 80 MB limit.")
                    for member in members:
                        path = PurePosixPath(member.filename.replace("\\", "/"))
                        if (path.is_absolute() or ".." in path.parts or ":" in member.filename or
                                stat.S_ISLNK(member.external_attr >> 16) or member.flag_bits & 1 or
                                not member.filename.lower().endswith(".csv")):
                            raise ValueError("ZIP supports plain CSV members only; unsafe paths, links, encryption and nested archives are rejected.")
                        if member.file_size > MAX_FILE_BYTES or member.file_size / max(1, member.compress_size) > 200:
                            raise ValueError("ZIP member exceeds the per-report size or expansion-ratio limit.")
                        # Read in memory only; never extract uploaded paths to disk.
                        with archive.open(member) as handle:
                            data = handle.read(MAX_FILE_BYTES + 1)
                        consume(data, f"{name}::{member.filename}")
            except (zipfile.BadZipFile, RuntimeError, NotImplementedError, OSError) as exc:
                raise ValueError("Invalid, unsupported or corrupt report ZIP.") from exc
        else:
            raise ValueError("NSE reports must be CSV or ZIP files.")
    combined = pd.concat(rows, ignore_index=True)
    if combined.empty:
        raise ValueError("No EQ-series instruments were found in the uploaded reports.")
    if combined.duplicated(["date", "symbol", "series"]).any():
        raise ValueError("Overlapping or duplicate date/symbol/series rows found. Upload each report once; no duplicate was silently removed.")
    sources.sort(key=lambda r: (r["name"], r["sha256"]))
    manifest_hash = sha256(json.dumps(sources, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return ReportBundle(combined, sources, reports, manifest_hash)


def synthetic_reports() -> bytes:
    """Original teaching fixture, generated in memory; no real symbols or market prices."""
    buffer = BytesIO()
    headers = ["TradDt", "Sgmt", "Src", "TckrSymb", "SctySrs", "ISIN", "OpnPric", "HghPric", "LwPric", "ClsPric", "TtlTradgVol"]
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for i, date in enumerate(pd.bdate_range("2024-01-02", periods=80)):
            text = StringIO()
            writer = csv.writer(text)
            writer.writerow(headers)
            for j, symbol in enumerate(("DEMOALPHA", "DEMOBETA")):
                price = 100 + 20 * j + i * 0.15 + (i % 7 - 3) * 0.4
                writer.writerow([date.date().isoformat(), "CM", "NSE", symbol, "EQ", f"ZZ000000000{j + 1}",
                                 round(price, 4), round(price + 2, 4), round(price - 2, 4), round(price + 0.5, 4), 100_000 + i * 300])
            member = zipfile.ZipInfo(f"SYNTHETIC_{date:%Y%m%d}.csv", date_time=(2024, 1, 1, 0, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(member, text.getvalue())
    return buffer.getvalue()
