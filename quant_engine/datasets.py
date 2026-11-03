"""Provider-neutral daily-data provenance. A passport records claims, not authenticity."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json

from .models import ValidatedData

ADAPTER_VERSION = "1.0.0"


@dataclass(frozen=True)
class Instrument:
    exchange: str
    symbol: str
    series: str = ""
    isin: str = ""
    currency: str = "INR"

    def __post_init__(self):
        if not self.symbol.strip() or len(self.symbol) > 80:
            raise ValueError("An instrument needs a symbol or an explicit research label (up to 80 characters).")
        if self.exchange not in {"NSE", "BSE", "Unknown", "Synthetic"}:
            raise ValueError("Unsupported exchange declaration.")
        if self.currency != "INR":
            raise ValueError("This build assumes INR. Currency conversion is not implemented.")


def canonical_bars_bytes(bars):
    """A stable normalized export for this adapter version, separate from raw bytes."""
    return bars.to_csv(index=True, date_format="%Y-%m-%d", lineterminator="\n").encode("utf-8")


def attach_passport(data: ValidatedData, *, instrument: Instrument, provider: str,
                    input_format: str, adjustment: str, sources: list[dict],
                    is_synthetic: bool = False, source_hash_kind: str = "raw-file SHA-256",
                    coverage: dict | None = None) -> ValidatedData:
    allowed = {"Unknown / unverified", "Consistently adjusted OHLC", "Unadjusted OHLC", "Synthetic example"}
    if adjustment not in allowed:
        raise ValueError("Unsupported adjustment declaration.")
    normalized_hash = sha256(canonical_bars_bytes(data.bars)).hexdigest()
    identity = {"adapter_version": ADAPTER_VERSION, "instrument": asdict(instrument),
                "source_hash": data.source_hash, "normalized_sha256": normalized_hash,
                "adjustment_basis": adjustment, "input_format": input_format,
                "provider_claim": provider, "is_synthetic": is_synthetic}
    dataset_id = sha256(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    data.metadata = {
        "schema_version": "daily-data-passport/1", "dataset_id": dataset_id,
        **identity, "source_hash_kind": source_hash_kind,
        "imported_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_files": sources, "timeframe": "1d",
        "session_timezone": "Asia/Kolkata", "date_semantics": "User-declared completed session date; not a UTC timestamp",
        "source_rows": len(data.bars), "source_start": data.bars.index[0].date().isoformat(),
        "source_end": data.bars.index[-1].date().isoformat(),
        "origin_verification": "Synthetic teaching fixture" if is_synthetic else "User-supplied origin; not independently authenticated",
        "adjustment_verification": "Synthetic fixture" if is_synthetic else "Declaration only; corporate actions not reconciled",
        "usage_rights": "Synthetic project fixture" if is_synthetic else "Not verified by this application; use according to your source's permissions",
        "calendar_status": "Not configured; missing sessions versus holidays cannot yet be determined",
        "coverage": coverage or {},
    }
    return data


def passport_for_analysis(data: ValidatedData) -> dict:
    """Keep source provenance stable while distinguishing the replayed analysis slice."""
    return {**data.metadata, "analyzed_rows": len(data.bars),
            "analyzed_normalized_sha256": sha256(canonical_bars_bytes(data.bars)).hexdigest(),
            "analyzed_start": data.bars.index[0].date().isoformat(),
            "analyzed_through": data.bars.index[-1].date().isoformat()}
