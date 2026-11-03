"""Versioned NSE CM session-date snapshot, not a settlement or live calendar feed."""
from datetime import datetime, time, timedelta, timezone
from hashlib import sha256
import json

import pandas as pd

IST = timezone(timedelta(hours=5, minutes=30), "Asia/Kolkata")
CALENDAR_VERSION = "NSE-CM-2026/2026-11-03.1"
START, END = "2026-01-01", "2026-12-31"
SOURCES = [
    "https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf",
    "https://nsearchives.nseindia.com/content/circulars/CMTR72260.pdf",
    "https://nsearchives.nseindia.com/content/circulars/CMTR72349.pdf",
    "https://nsearchives.nseindia.com/content/circulars/CMTR76941.pdf",
]
HOLIDAYS = {
    "2026-01-15": "Maharashtra municipal election", "2026-01-26": "Republic Day",
    "2026-03-03": "Holi", "2026-03-26": "Ram Navami", "2026-03-31": "Mahavir Jayanti",
    "2026-04-03": "Good Friday", "2026-04-14": "Ambedkar Jayanti", "2026-05-01": "Maharashtra Day",
    "2026-05-28": "Bakri Id", "2026-06-26": "Muharram", "2026-09-14": "Ganesh Chaturthi",
    "2026-10-02": "Gandhi Jayanti", "2026-10-20": "Dussehra", "2026-11-10": "Diwali Balipratipada",
    "2026-11-24": "Guru Nanak Jayanti", "2026-12-25": "Christmas",
}
SPECIAL_SESSIONS = {"2026-02-01": "Union Budget live session", "2026-11-08": "Muhurat live session"}
# Application availability policy, deliberately later than the cited trading windows.
# This is neither the exchange closing time nor a guarantee that a feed is final.
DAILY_READY_AFTER = time(18, 0)
CALENDAR_HASH = sha256(json.dumps({"version": CALENDAR_VERSION, "start": START, "end": END,
    "holidays": HOLIDAYS, "special_sessions": SPECIAL_SESSIONS, "sources": SOURCES,
    "availability_policy": "18:00 Asia/Kolkata"}, sort_keys=True).encode()).hexdigest()


def session_dates(start, end):
    """Reject unsupported coverage rather than pretending weekdays are verified."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    if start.tz is not None or end.tz is not None or start != start.normalize() or end != end.normalize():
        raise ValueError("Calendar needs timezone-free session dates.")
    if start < pd.Timestamp(START) or end > pd.Timestamp(END) or start > end:
        raise ValueError("Calendar snapshot supports NSE CM session dates in 2026 only.")
    return pd.DatetimeIndex([d for d in pd.date_range(start, end)
        if d.date().isoformat() in SPECIAL_SESSIONS or
        (d.weekday() < 5 and d.date().isoformat() not in HOLIDAYS)], name="date")


def latest_ready_session(now):
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Quality assessment needs a timezone-aware clock.")
    local = now.astimezone(IST)
    today = pd.Timestamp(local.date())
    if not pd.Timestamp(START) <= today <= pd.Timestamp(END):
        return None
    eligible_end = today if local.time() >= DAILY_READY_AFTER else today - pd.Timedelta(days=1)
    if eligible_end < pd.Timestamp(START):
        return None
    dates = session_dates(START, eligible_end)
    return dates[-1] if len(dates) else None


def assess_data_quality(data, *, now=None, replay=False):
    """Audit the visible slice only; never fill bars or infer a stock's listing history."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Quality assessment needs a timezone-aware clock.")
    local = now.astimezone(IST)
    bars = data.bars
    dates = bars.index
    result = {"schema": "daily-data-quality/1", "assessed_at": now.isoformat(),
        "scope": "Analyzed slice only", "observed_rows": len(bars), "replay": replay,
        "short_history": len(bars) < 60, "zero_volume_dates": _dates(dates[bars.volume.eq(0)]),
        "adjustment_status": data.metadata.get("adjustment_basis", "Unknown / unverified"),
        "calendar_version": None, "calendar_status": "Not assessed: no supported NSE calendar declaration",
        "missing_expected_dates": [], "unexpected_dates": [], "unsupported_dates": [],
        "future_dates": [], "freshness": "Not assessed", "lag_sessions": None,
        "latest_ready_session": None, "notes": []}
    instrument = data.metadata.get("instrument", {})
    if data.metadata.get("is_synthetic") or instrument.get("exchange") != "NSE":
        result["notes"].append("Synthetic, unknown-exchange and other-exchange data are not checked against the NSE calendar.")
        return result
    result.update(calendar_version=CALENDAR_VERSION, calendar_sha256=CALENDAR_HASH,
                  calendar_sources=SOURCES, calendar_coverage={"start": START, "end": END},
                  availability_policy="18:00 Asia/Kolkata; conservative application policy, not exchange close or verified source finality")
    inside = dates[(dates >= pd.Timestamp(START)) & (dates <= pd.Timestamp(END))]
    result["unsupported_dates"] = _dates(dates.difference(inside))
    result["future_dates"] = _dates(dates[dates > pd.Timestamp(local.date())])
    result["calendar_status"] = "Checked within NSE CM 2026 snapshot" if not result["unsupported_dates"] else "Partial: dates outside NSE CM 2026 snapshot are unverified"
    ready = latest_ready_session(now)
    if len(inside):
        expected = session_dates(inside[0], inside[-1])
        result["unexpected_dates"] = _dates(inside.difference(expected))
        # Today's bar may have been user-declared complete, but is not required by
        # our conservative availability policy until its cutoff has elapsed.
        elapsed = expected[expected <= ready] if ready is not None else expected[:0]
        if local.date().isoformat() > END:
            elapsed = expected
        result["expected_elapsed_sessions"] = len(elapsed)
        result["missing_expected_dates"] = _dates(elapsed.difference(inside))
        if len(inside[inside.date == local.date()]) and local.time() < DAILY_READY_AFTER:
            result["notes"].append("Today's bar is before the conservative availability cutoff; source finality is unverified.")
    if replay:
        result["freshness"] = "Historical replay: current-date freshness comparison disabled"
    elif ready is None or result["unsupported_dates"]:
        result["freshness"] = "Not assessed: clock or data range outside supported calendar coverage"
    else:
        result["latest_ready_session"] = ready.date().isoformat()
        last = dates[-1]
        if last > ready:
            result["freshness"] = "Contains observations beyond the conservative completed-session cutoff"
        elif last == ready:
            result.update(freshness="Current through the latest expected completed session", lag_sessions=0)
        else:
            lag = session_dates(last, ready)
            result.update(freshness="Behind latest expected completed session (historical uploads may be intentional)",
                          lag_sessions=int((lag > last).sum()))
    result["notes"] += ["Absent observations are candidates for review, not proof of source failure: listing dates, suspension and no-trade days are not independently reconciled.",
        "Calendar snapshot is versioned and offline; later exchange amendments require an update. No bars were filled or removed."]
    return result


def _dates(index):
    return [d.date().isoformat() for d in index]


def attach_quality(data, *, now=None, replay=False):
    quality = assess_data_quality(data, now=now, replay=replay)
    data.metadata["data_quality"] = quality
    data.metadata["calendar_status"] = quality["calendar_status"]
    if quality["calendar_version"]:
        data.warnings = [w for w in data.warnings if not w.startswith("No exchange calendar is configured")
                         and not w.startswith("Gaps longer than four calendar days")]
    for key, description in (("missing_expected_dates", "expected observations absent; review listing, suspension and source coverage"),
                             ("unexpected_dates", "observations on calendar non-session dates"),
                             ("future_dates", "future-dated observations")):
        if quality[key]:
            data.warnings.append(f"Calendar review: {len(quality[key])} {description}. No rows were changed.")
    return quality
