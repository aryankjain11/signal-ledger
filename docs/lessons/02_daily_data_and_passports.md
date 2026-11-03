# Lesson 2 · Daily reports, identity and data passports

All prices, quantities, identifiers and scenarios below are invented teaching examples.
The walkthrough contains no real Indian-stock observations. This lesson introduces
the data foundation needed before interpreting RSI, MACD or a chart pattern.

## 1. Why begin with data?

An indicator is a calculation on observations. A correct RSI calculation on the
wrong security, duplicated sessions or incompatible price histories still gives
the wrong research result. Before asking what a candle means, ask whose candle
it is, which session it represents, what its prices mean and where it came from.

Our new offline importer accepts NSE CM UDiFF-style daily CSV reports, individually
or inside ZIP files. It selects one EQ-series security and constructs its daily
open, high, low, close and traded-volume history. It makes no network requests.
The old one-stock CSV/XLSX path remains available.

The implementation is a **schema-subset preview**. Synthetic acceptance tests
exercise the supported fields and failure cases. Acceptance against a permitted
real report and the current complete NSE format remains pending. A file having
the expected headers is not proof that NSE produced it.

## 2. A daily report is different from a historical series

A bhavcopy is a daily market report. Think of each report as a page with many
securities for one session. To make one security's history, select that security
from successive pages and place those observations in date order.

| Invented report date | ALPHA EQ close | BETA EQ close |
| --- | ---: | ---: |
| 2024-01-02 | ₹103 | ₹123 |
| 2024-01-03 | ₹104 | ₹121 |
| 2024-01-04 | ₹102 | ₹124 |

Selecting ALPHA creates three bars. Combining all six records into one price
sequence would mix securities. Averaging ALPHA and BETA would create prices that
neither stock actually traded at. This importer does neither.

The supported field mapping is:

| Report field | Meaning in this build |
| --- | --- |
| `TradDt` | Daily trade/session date, YYYY-MM-DD |
| `Sgmt`, `Src` | Required claims CM and NSE |
| `TckrSymb`, `SctySrs`, `ISIN` | Ticker, selected EQ series and security identity |
| `OpnPric`, `HghPric`, `LwPric`, `ClsPric` | Quoted daily OHLC |
| `TtlTradgVol` | Reported traded quantity, not turnover in rupees |

Additional columns can be present but are not silently turned into supported
features. Delivery percentage, VWAP and number of trades are separate future fields.

## 3. Symbol, series and ISIN

A symbol is a readable trading label. The same apparent company name does not
guarantee the same security across time. A series is another dimension of the
record; this first adapter accepts EQ and excludes other series rather than
merging them. An ISIN is a security identifier, distinct from the company name.

Suppose ALPHA EQ has invented ISIN ZZ0000000001 in January and ZZ0000000002 in
February. There might have been a security change, or a bad source record. The
importer rejects that combined selection for review. It cannot decide the economic
mapping automatically. Symbol changes, mergers, delistings and historical index
membership require a proper reference-data history later.

The present check validates a 12-character ISIN structure and consistency. It does
not validate its check digit, listing status or authenticity. The walkthrough's
ZZ identifiers are deliberately fake teaching identifiers. Passing a format check
does not turn them into actual NSE securities.

## 4. Trade date, business date and completed sessions

`TradDt` identifies the trade date used for bars. Another field such as `BizDt`
must not silently replace it. A daily bar uses an exchange-session date associated
with Asia/Kolkata, rather than pretending that the date is a UTC instant.

You must confirm uploaded observations are completed daily sessions. Recognized
provisional filenames and interim session markers are rejected, but arbitrary
filenames cannot establish finality. This is still a user declaration.

A weekday is not automatically an exchange trading session: holidays and
exceptional sessions matter. Our fake ZIP uses 80 business dates purely to make
a deterministic software fixture. It is **not an NSE calendar**.

If ALPHA is absent from one uploaded report but BETA is present, the passport
records the absence. It does not invent an ALPHA bar or conclude that the date
was an exchange holiday. Suspension, listing history, no trading or an incomplete
source can require different explanations. Calendar reconciliation is next work.

## 5. Quoted versus adjusted prices

Imagine owning one share priced at ₹200. In a hypothetical 2-for-1 split, you
receive two shares and the price becomes approximately ₹100 before other market
movement. The holding is still about ₹200. A raw price ratio of 100/200 − 1 gives
−50%, but that is not the economic return caused by the split alone.

A consistently back-adjusted historical series might transform the earlier
prices and share volumes according to a documented event factor. It must apply
the appropriate policy across OHLC; replacing only the close can produce impossible
candle relationships. Dividends require a distinct return convention and must not
be treated as share splits. A sharp move alone is insufficient evidence to invent
an adjustment.

This importer preserves quoted prices. Its passport says **Unadjusted OHLC** for
uploaded reports and explicitly states that corporate actions are not reconciled.
The standard CSV path records your adjustment declaration, without verifying it.
Indicators remain exploratory until the data's price basis is understood.

## 6. What the passport proves

A passport is a record of input identity and assumptions:

- The instrument, source/provider claim and input format.
- Original file names, byte counts and SHA-256 hashes.
- A deterministic hash of normalized daily bars.
- A dataset ID based on stable identity, declarations and adapter version.
- Import time, date range, source count, calendar/adjustment limitations and rights status.
- The actual analysis date range and a separate hash for its exported CSV.

A hash is a fingerprint of bytes. Re-importing exactly the same inputs and
declarations gives the same dataset ID even though import time changes. Reordering
the same uploaded files does not change it. Putting the same CSVs in a different
ZIP changes the raw-container fingerprint while the normalized bars can match.

Matching hashes establish content equality, not correct market prices, lawful
redistribution, independent source authentication or profitability. Those are
different questions requiring different evidence.

In historical replay, an 80-row source might be analyzed only through row 40.
The passport retains `source_rows=80` and the full-source normalized hash while
reporting `analyzed_rows=40` and `analyzed_normalized_sha256` for the downloaded
analysis CSV. This prevents a full-dataset fingerprint from being mistaken for
the fingerprint of the slice you actually inspected.

## 7. Try it in the app

1. Open Research and choose **Synthetic NSE report walkthrough** in Data source.
2. Observe the prominent synthetic label. Select DEMOALPHA, then DEMOBETA.
3. Open the data-quality tab and inspect the passport, source hashes and limitations.
4. Download the passport and analyzed daily CSV. No real report is required.
5. Move historical replay earlier and compare the source and analyzed row counts.
6. Open **Import NSE daily reports** to see instructions and download the fake ZIP.
7. Upload it there and confirm completed sessions to practice the upload workflow.
   That upload path cannot independently detect a fake file's origin; keep using
   the explicitly labelled walkthrough for synthetic research.

One or two valid sessions produce an import preview, not analysis. Three is the
minimum analysis input; longer indicator windows still need their own warm-up.
Aim for at least 60 sessions for the baseline and substantially more for research.

## 8. Builder walkthrough and safeguards

`nse_files.py` reads CSV bytes, validates report headers/date/source claims,
filters EQ and builds an instrument list. `ReportBundle.select` checks security
continuity and validates selected OHLCV. `datasets.py` attaches provenance.
`data_ui.py` presents the controls; `analysis.py` includes the passport in evidence.

Duplicate date/symbol/series records are rejected, even if their prices match.
There is no silent winner-selection rule for conflicting reports. Original
uploads stay in memory; there is not yet an immutable raw-file storage database.
Keep your originals according to your source permissions and retention policy.

The importer reads ZIP members in memory and never extracts uploaded paths. It
rejects traversal paths, links, encryption and nested archives, with limits of
20 MB per file, 40 MB combined input, 80 MB expanded content, 1,000 reports and
one million raw rows. These boundaries control workload rather than expanding
the supported schema.

A useful implementation mistake: pandas already has a method called `isin`.
Accessing a column as `frame.isin` selects that method, not the security-ID column.
The implementation now uses `frame["isin"]`. The regression tests verify actual
identity selection so this mistake cannot hide behind a superficial page load.

## 9. Exercises and answers

1. Why do 80 reports containing two stocks produce 80 bars after selecting one?
2. If one stock disappears from a report, should we copy its previous close?
3. Does a valid-looking ISIN establish that a security is listed?
4. What changes when replay moves from 80 observations to 40?
5. One share at ₹200 becomes two at ₹100 after a split. What is the holding value?

**Answers:** (1) Each selected stock contributes at most one observation per report
date. (2) No: preserve the absence and investigate its cause. (3) No: format,
check digit, listing and historical continuity are separate checks. (4) Analyzed
rows/range and slice hash change; source identity remains fixed. (5) About ₹200
before other market movement, costs or additional events.

Your understanding is not automatically marked complete. Bring back one answer
or a question before we extend the data contract.

## Sources and remaining acceptance

- [NSE reports](https://www.nseindia.com/all-reports): current daily-report entry point; the page directs users from legacy reports to CM-UDiFF final ZIPs.
- [NSE format resources](https://www.nseindia.com/static/resources/forms-formats-members): official format-document entry point.
- [NSE data policy](https://www.nseindia.com/static/market-data/nse-data-policy): source permissions need separate consideration; an accessible file is not an assumed redistribution license.
- [NCDEX UDiFF specification](https://ncdex.com/public/uploads/downloads/1727930832.pdf): checked shared tag meanings only; this commodities document is not evidence of the full current NSE equity schema.

The linked current NSE workbook could not be retrieved during this build because
the archive connection reset/timed out. That limitation is recorded rather than
calling the full schema verified. Next: accept a permitted real NSE report against
the current specification, then add a versioned exchange calendar with exceptional
session fixtures. Corporate-action reconciliation follows as a separate milestone.
