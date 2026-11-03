# Calendar and data-quality checks

Research → Data & exports now audits the analyzed data slice and includes the
result in the data passport, analysis/backtest JSON and a separate quality download.
This does not fetch market data or change indicator/strategy calculations.

## Current supported scope

- Exchange: NSE capital-market daily data, calendar year **2026 only**.
- Snapshot: `NSE-CM-2026/2026-11-03.1`, with a hash of its dates, policy and sources.
- Weekdays less capital-market trading holidays, with January 15 closure amendment.
- February 1 Budget and November 8 Muhurat Sunday live-session overrides.
- Other years, BSE, unknown exchange and synthetic fixtures remain unverified
  against this snapshot. Synthetic business dates are not treated as real sessions.

## What is reported

- Absent expected observations between the first/last visible observations.
- Bars on non-session dates, future dates and unsupported calendar dates.
- Zero-volume observations, short history and the adjustment declaration.
- Latest conservatively completed session and lag in sessions for a current view.
- Historical replay disables comparison with today's newest session and audits
  only visible rows. Source dataset provenance remains unchanged.

An absent observation is a review candidate. A stock can be newly listed, suspended
or untraded, and these histories are not independently reconciled yet. No price is
forward-filled; no holiday/weekend row is silently discarded. Currentness does not
establish complete history: a file can contain today's close and still omit an
earlier session. Conversely, a historical research upload can intentionally be old.

Freshness uses an explicit **18:00 Asia/Kolkata application cutoff**, later than
the cited trading windows. It is not the exchange close or proof that a source
published its final data. A same-day observation before the cutoff is flagged as
beyond the conservatively completed-session boundary, even if the user confirmed
it was complete. The clock/assessment time is exported for reproducibility.

The offline snapshot does not automatically learn later exchange amendments.
Dates scheduled after the snapshot's verification date are subject to amendments.
Wider calendar coverage and source-update checks remain pending. Weekly context
still uses conservative prior-calendar-week aggregation; this milestone does not
introduce new timeframe confirmation logic or corporate-action adjustments.

## Sources checked on 2026-11-03

- [NSE CMTR71775: 2026 CM trading holidays](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf).
- [NSE CMTR72260: January 15 closure amendment](https://nsearchives.nseindia.com/content/circulars/CMTR72260.pdf).
- [NSE CMTR72349: February 1 live session](https://nsearchives.nseindia.com/content/circulars/CMTR72349.pdf).
- [NSE CMTR76941: November 8 Muhurat session](https://nsearchives.nseindia.com/content/circulars/CMTR76941.pdf).

Trading holidays are intentionally separate from settlement holidays; for example,
the Budget circular specifies a live session while excluding its T0 session due
to settlement holiday. A general banking/settlement holiday list cannot replace
the CM trading calendar.

## Verification and remaining work

`tests/test_calendar.py` covers exact holiday/session exceptions, timezone/cutoff
boundaries, absence versus freshness, partial coverage, future observations,
replay isolation, synthetic/other-exchange exclusion, immutability and UI flags.
Actual measured results are logged in WORK_LOG.md after running the checks.
No new learning exercises are part of this milestone; assignments are paused.
