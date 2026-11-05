# After the pattern · historical outcome research

Implemented scope: `pattern-outcomes/1`. Updated 2026-11-05.

## Purpose and use

Choose **Workspace → After the pattern**. The page uses the existing synthetic,
generic CSV/XLSX, native NSE stock-history or report-preview data flow, source
declarations, research rules and replay cutoff. Select event types, context,
event dates, reference, horizons and spacing, then **Run event study**. The
synthetic default is an immediate demonstration, not market evidence.

The four views compare outcomes, show distributions/excursions, inspect an
individual occurrence and export the audit. One uploaded stock is studied at a
time; comparisons between its event types use explicit cohort rows. Multiple
stock files remain in the separate comparison workspace. This release does not
create a cross-stock pattern database or a pooled research universe.

## Event identity and information timing

The source detector's formation date describes when geometry formed. Its
knowledge date/index describes when all required evidence became available.
Measurements anchor to the latter. Three-right-bar pivot confirmation must not
be measured as if available three bars earlier. Current full-history RSI, trend
or the last event state is never substituted for the historical snapshot.

A cohort is **family + pattern name + event state + direction**. A breakout,
held retest and continuation are distinct observations at their respective
knowledge closes. Developing double-pattern geometry can be studied separately
from a later confirmed neckline break. Developing neutral triangle geometry and
Doji can be studied in upward-price mode. Confirmed triangle breaks take direction
from the actual boundary broken, rather than assuming the name predicts direction.

Failed, expired and invalidated lifecycle messages remain in the audit but are
excluded from the studied outcome population in this release. Importantly, a
later failure does not remove an earlier breakout. There is no filter for
"eventually successful breakouts." Such a filter would use future information.

Exact duplicate transitions do not increase n; conflicting copies are rejected.
Multiple geometries with the same cohort and knowledge date contribute only one
price path. Their exclusion remains visible. Different event types can describe
the same market episode and must not be added up as independent evidence.

## References, horizon and direction

For an event known at the close of observation **t**, horizon **h** ends at
**close[t+h]**. Defaults are 1, 5, 10 and 20; the page also offers 2, 3, 40 and60.
These are uploaded observations, not a guarantee of consecutive NSE sessions.
Calendar warnings are preserved; absent observations are never filled. Calendar
days between knowledge and the horizon endpoint are exported separately.

Default reference **P = open[t+1]**. Horizon1 therefore measures the next observed
bar's open-to-close change and excludes the overnight gap from close[t]. The
alternative **P = close[t]** is an observational comparison that includes the next
gap. Neither convention asserts that an order could have filled at that price.
Adjusted research prices use the same price basis throughout, not historical cash
fills. No slippage, charges, dividends, financing or short-sale availability is modeled.

Let **d=+1** for upward measurement and **d=−1** for bearish alignment:

- Forward movement: **d × (close[t+h]/P − 1)**.
- Upward MFE: **max(0, max(high[t+1:t+h])/P − 1)**.
- Upward signed MAE: **min(0, min(low[t+1:t+h])/P − 1)**.
- Bearish MFE: **max(0, 1 − min(low[t+1:t+h])/P)**.
- Bearish signed MAE: **min(0, 1 − max(high[t+1:t+h])/P)**.

Here intervals include both listed endpoints. The detection candle is excluded
from both excursions. Daily OHLC reveals extremes, not their order, order fills,
target-before-stop success or accessible liquidity. Signed MAE is nonpositive;
other systems sometimes report its positive magnitude, so compare conventions.
Bearish aligned movement negates price change; it is not a simulated short return.
Neutral patterns have no invented bearish/bullish direction. Use upward-price mode
to measure them; pattern-direction mode discloses their exclusion.

Invented example: a setup becomes knowable Monday, the next observed opening
price is100, and close[t+5] is104. The measured gross return is4%. If the following
five bars' highest high is108 and lowest low95, upward MFE is8% and signed MAE−5%.
The same path in bearish alignment has return−4%, MFE5% and signed MAE−8%.

## Eligibility, censoring and actions

Event-date filters restrict anchors; outcomes can extend beyond the event-date
end, up to the global replay cutoff. This distinction is explicit on the page.
Changing replay restricts all visible evidence and subsequent outcomes.

An unavailable full horizon is **Incomplete horizon**, never a negative result
or a forced early exit. Return/MFE/MAE are all null for that row. No partial
excursions enter a complete-horizon average. Each horizon therefore has its own
complete/incomplete counts; distributions at different horizons can have different
composition. Recent excluded observations can change averages through censoring.

For raw prices with a reviewed action ledger, a complete window crossing a known
ex-date in **(knowledge date, horizon date]** is separately excluded. No action
on/before the knowledge date is treated as a future crossing. The conservative
window starts at knowledge even in next-open mode. Split/bonus-adjusted research
uses its declared coherent price basis. Unverified adjustment completeness, cash
dividends and raw action effects on historical detector context remain limitations.
Execution restrictions on action-audited ranges remain in the strategy engine;
an observational study does not override them.

## Context and deterministic overlap spacing

The page snapshots these values at the knowledge close and exports their actual
numbers as well as category labels:

- Trend: **close > EMA50**, **close <= EMA50**, or unavailable EMA50.
- Volume: **RVOL >=1.2**, **RVOL <1.2**, or unavailable RVOL. RVOL uses the existing
  prior20-observation mean-volume convention; the event does not enter its own baseline.

These are simple stock-context buckets, not a broad market-regime model.
Filters use these snapshots, with unavailable values separate from low values.

Default spacing is greedy within each cohort: keep its earliest eligible index;
keep the next only if **new index > previous kept index + largest horizon**.
This conservatively avoids sharing even the closed interval's endpoint. Spacing
uses the largest selected horizon consistently for all outcome rows and occurs
before examining maturity or returns. Changing the largest horizon changes the
sample and is a research choice, recorded in the study definition. An incomplete
last occurrence still reserves its window. **Keep all** is an explicit alternative.

Baseline anchors are separately thinned with the same spacing within each context
pool. Spacing reduces direct window reuse; dependence remains between different
cohorts, context pools, shared controls and market observations. It is not a
portfolio capital/allocation rule or a proof of independent observations.

## Baseline construction and fair coverage

The baseline uses the **same stock, selected event-date range, reference mode,
horizon, perspective and price basis**. A candidate anchor has no selected
eligible event on that date. Matching uses only the anchor's trend and RVOL bucket.
Future event occurrences are allowed; rejecting a control because a pattern later
appeared would introduce a future-dependent selection rule. Diagnostic failure
messages do not independently make an anchor a selected study event.

Each complete event receives its matching context pool's mean movement if the
pool has enough complete, action-eligible outcomes (default minimum5, configurable).
Too few controls produces an unavailable baseline, with its count still reported.
Identical matching pools are reused, not misrepresented as new independent data.
Exports retain every control anchor, context, reference and outcome state.

Matched event mean = mean of returns only for events with an available pool.
Matched baseline mean = mean of those events' pool means, with one equal weight
per covered event. Difference = mean(event return − matched pool mean). This
preserves identical event coverage on both sides. The full-cohort mean can differ.

Invented example: covered event movements6% and−2%, with matching pool means2%
and1%, give event mean2%, baseline1.5% and difference0.5 percentage points.
An uncovered third event is excluded from both matched means, while remaining in
the full-cohort summary if its outcome is complete.

The pools use the whole chosen historical interval, including dates later than an
event. This is a **retrospective descriptive comparison**, not an earlier-only
forecast or held-out test. It is not a causal counterfactual, abnormal-return
market model, alpha estimate or a statistical-significance test. Baseline windows
can overlap event windows or other control pools, and sample selection changes
when the selected event catalogue changes. Save that definition before interpreting.

## Summary and uncertainty conventions

Each cohort/horizon reports selected, complete, incomplete and action-excluded
counts; mean, median, 25th/75th percentiles, positive fraction, flat count and
median excursions; matched event count, matched means and their difference.
Movement is positive above1e−12, flat within absolute1e−12, negative below−1e−12.
Missing samples yield unavailable means/fractions, not zero. The page multiplies
fractions by100 for percentages. The baseline difference is in percentage points.

Box plots/quartiles describe observed dispersion. They do not quantify uncertainty
about a population mean. Samples below5 are labelled very small, below30 small;
these thresholds are interface cautions, not guarantees of statistical sufficiency.
Even larger n can be dependent, selected and unstable. Positive fractions are
historical outcome frequencies, not trade win rates or calibrated probabilities.

No ordinary independent-sample standard errors, confidence intervals or p-values
are supplied. Dependence-aware uncertainty, multiple-experiment adjustment,
chronological held-out validation and stability studies need a separate protocol.
Gross event averages are not after-cost trading expectancy. Events do not form
a capital-constrained trade ledger and their returns must not be compounded into
a portfolio equity curve.

## Software design, records and acceptance

`quant_engine/event_study.py` is independent of Streamlit. `StudyRules` validates
configuration; `occurrence_ledger` adapts supported immutable detector events;
`build_study` returns occurrence, outcome, baseline and summary tables plus an
audit. Vectorized future extrema are deliberately used only for outcome labels,
not detector/context features. Future-append tests protect already complete
outcomes and selection; newly available outcomes and expanding retrospective
baseline summaries are expected to change.

`quant_engine/event_study_ui.py` supplies form controls, comparison bars, box plots,
occurrence charts, notes and export controls. Completed results are cached by
data, detector events, rules and provenance; changing source/replay changes the
calculation. A deterministic run ID hashes version, configuration, selected
visible-data SHA256, source/dataset identity, detector rules and occurrence snapshots.

JSON includes configuration, audit, all occurrence decisions, fractional outcomes,
baseline rows, summaries, full source-event evidence and passport/quality metadata.
CSV exports provide occurrence outcomes, controls and summaries. The run ID covers
calculation identity; extra contextual provenance is attached to the portable
record. Exports require an explicit local download and do not save a database or
upload market data to GitHub. Only source, tests, synthetic fixtures and documents
are published to the owner's existing private repository.

Numerical acceptance covers hand-specified price/knowledge/gap examples, bearish
and neutral modes, censoring, lifecycle identity/deduplication, matching coverage,
closed-window overlap, contexts/date filters, raw actions, summary arithmetic,
invalid inputs, replay invariance and real-detector compatibility. UI acceptance
covers navigation, changed definitions, empty selection, exports and short-history
behavior. Observed counts/results are recorded in WORK_LOG.md and BUILD_REPORT.md
after the runs; a test pass is software evidence, not investment-performance evidence.

## Remaining research and next feature

This milestone completes a bounded descriptive research view. Still planned:
database/history, cross-stock/time-specific universes, target/stop/expiry outcome
labels, first-hit ambiguity treatment, market/sector-adjusted studies, dependence-
aware inference, hypothesis/experiment registry and held-out/walk-forward studies.
The recommended next product feature is a versioned breakout-retest strategy with
entry, stop, exit, expiry and costs in the existing execution simulator, followed
by fair strategy comparison. Existing learning exercises remain paused.

## Sources and implementation choices

- [CFA Institute: Backtesting and Simulation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation)
  explains why historical evaluation needs explicit assumptions and attention to
  look-ahead/survivorship and other biases. It does not endorse these detector rules.
- [EventStudyTools: Introduction to event studies](https://www.eventstudytools.com/introduction-event-study-methodology)
  describes the estimation-window/normal-return/abnormal-return approach used in
  formal financial event studies. This simpler pattern-outcome research deliberately
  does not claim that model, formal causal identification or its statistical tests.

Sources checked 2026-11-05. All worked examples and implementation conventions
above are original, labelled hypothetical definitions; no trading edge is asserted.
