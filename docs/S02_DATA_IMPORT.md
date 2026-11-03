# S02-A · Offline daily reports and data passports

Status: implemented and verified with synthetic fixtures. Full S02 remains partial.

Current follow-ons: S02-022 adds the offline NSE CM 2026 calendar/quality snapshot
(`DATA_QUALITY.md`). S02-023 adds reviewed split/bonus-ledger research normalization,
cutoff-aware replay and raw/factor/audit exports (`CORPORATE_ACTIONS.md`). Broader
calendar years, automatic action reconciliation and execution accounting remain pending.

Follow-on S02-021: direct NSE security-history CSV/XLSX upload is now supported
through Upload daily data, checked against an owner-supplied real stock-history
export locally. See `NSE_CSV_UPLOAD.md`. This is a different file format and does
not complete the UDiFF real-file/full-current-schema gate below.

## What is usable

Research offers a synthetic NSE-format walkthrough and an offline CSV/ZIP importer.
Multiple daily reports become one selected EQ security's OHLCV history. The adapter
uses TradDt, checks required source/segment claims, rejects conflicting identity
and duplicate dates, and validates selected prices. It preserves quoted prices.
One/two-row histories are preview-only. Existing one-stock CSV/XLSX import remains.

Passports record source files/hashes, instrument/series/ISIN, normalized-data hash,
stable dataset ID, UTC import time, Asia/Kolkata date semantics, adjustment and
permission declarations, and coverage of uploaded report dates. Historical replay
preserves source identity and separately hashes its analyzed CSV. Evidence JSON
includes the passport. This is not an immutable dataset store or origin certificate.

The fake ZIP contains 80 business-date reports and two invented securities. Those
dates do not implement an exchange calendar; identifiers are not real listings.
Lesson 2 connects financial meaning, code, failure cases and owner exercises.

## Verification gate

`tests/test_nse_files.py` checks independent exact fixture values, file-order
determinism, CSV/ZIP normalized equivalence, trade versus business date, EQ
selection, security absences without filling, identity changes, duplicates,
malformed schemas/dates/prices, provisional markers, hostile/corrupt ZIP inputs,
resource limits, preview gating, replay hashes and application flows.

Actual complete-suite results and remote evidence are recorded in WORK_LOG.md and
GITHUB_SYNC.md after observation. A synthetic software pass demonstrates the
implementation's tested behavior, not real-feed compatibility or investment value.

## Checklist interpretation

- S02-001 Partial: source pages/policy inspected; no licensed historical feed selected.
- S02-002 Partial: data contract and file-driven ticker selection exist; company resolver pending.
- S02-003 Partial: basic ISIN consistency exists; listings/corporate identity history pending.
- S02-005 Done: explicit daily session dates and Asia/Kolkata semantics; no UTC-date substitution.
- S02-010 Partial: hashes and normalized exports exist; durable raw/normalized store pending.
- S02-012 Partial: reject-all duplicate policy exists; correction/version audit pending.
- S02-019 Partial: uploaded-date coverage, declarations and bounded 2026 calendar/freshness checks exist; wider coverage and adjustment-quality gates remain.
- S02-020 Done: unavailable fields/absences are disclosed; no interpolation or fabricated bars.

## Limits and next increments

Required: accept a permitted real report against the current full NSE specification.
The linked official workbook download failed during research (reset/timeout).
Shared UDiFF tag meanings were cross-checked against an official NCDEX document;
that is not proof of the complete current NSE equity schema. See Lesson 2 sources.

The bounded calendar and reviewed split/bonus research layers are implemented.
Remaining: wider calendar snapshots, real UDiFF report acceptance, automatic action
reconciliation, dividends/total returns and share-accounting execution. Licensed provider selection, automatic
updates, retries, full listing history and persistent dataset storage remain future
work. No live orders, broker access or paid service has been added.
