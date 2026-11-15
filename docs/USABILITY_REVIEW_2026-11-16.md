# Signal Ledger · workflow and usability review

Review begun 15 November and completed 16 November 2026, Asia/Calcutta.
This follows the broader [platform inspection](PLATFORM_INSPECTION_2026-11-15.md).
It records a bounded improvement release, not certification that every possible
input, device or market scenario works. Read [platform context](PLATFORM_CONTEXT.md)
for the vision and [original-plan status](PROJECT_STATUS.md) for unfinished scope.

## Outcome and purpose

The main daily-file research journey is usable: upload or explore the labelled
demo, inspect price/structure/momentum, study what followed observations, test an
explicit long strategy, compare two stocks and consult financial definitions.
The audit found avoidable context loss and confusing presentation around that
journey. This release improves continuity and recovery, rather than adding another
indicator or silently changing a trading rule.

The long-term aim remains an interpretable quantitative research platform for
Indian-stock swing research: observable data → causal observations → descriptive
historical evidence → exact strategies/risk → independent validation → prospective
paper evaluation. The current software is a deterministic local prototype. It has
two exploratory long simulators and descriptive event studies; it has no trained
model, calibrated probabilities, live feed, broker orders or durable run database.

## Findings and changes

| Finding | Effect on a researcher | Implemented response |
| --- | --- | --- |
| Research replay date reset after a reference visit | A different dataset slice could appear without the researcher choosing it | Keep replay per source and preserve rules, strategy selection and selected tabs in the live session; show historical-replay status |
| Comparison window reset from 10 to 20 | Repeated settings and a changed rolling statistic | Retain comparison mode, window, labels, declarations, range and tab |
| Pickers disappeared on other workspaces | Returning could lose comparison files or an action ledger | Retain immutable byte copies outside widget state; recreate retired pickers with fresh generations |
| An old picker could emit an empty callback | A delayed cleanup could erase a valid retained file | Ignore callbacks from retired generations and inactive workspace/source contexts; regression covers stale versus intentional removal |
| Completed-bar confirmation was not tied to replaced inputs | A declaration about an earlier file could carry forward | Bind the declaration to exact file names and SHA-256 bytes; replacing a file requires confirmation again |
| Recovery was obscure | Users had to drag dates or reconfigure a failed search | Add clear-file, latest-bar, all-shared-dates and clear-concept-filter actions; clamp retired dates to actual observations |
| Latest-bar action changed computation but initially left the slider behind | The displayed date contradicted the analysis | Send an explicit widget-value update; browser verifies slider and 600-row analysis both end on 18 April 2025 |
| Landing controls competed with the result | Financial inputs and advanced rules obscured the chart workflow | Collapse capital/risk/costs and advanced action/detector controls; keep a compact monetary assumption summary |
| Synthetic data appeared beside an unknown adjustment selector | Conflicting provenance cues | Use the explicit Synthetic example basis for demo data; retain real-file adjustment declarations |
| Reference entry point emphasized practice | Extra steps to find a term; assignments are paused | Default to the searchable Concept library; remove exercise prompts from displayed articles; retain existing optional labs |
| Outcome plots did not make direction/coverage immediate | A positive bearish-aligned number could be read as an upward return or short profit | Name gross direction-aligned/upward movement, observation horizon, matched/complete/selected counts and distribution sample sizes |
| Trade tables led with technical identifiers | Entry, exit and P&L were harder to find | Put human-readable entry/exit, shares, net P&L and reason first; keep full evidence and unchanged raw exports |

## What was exercised

| Area | Evidence and result | Boundary |
| --- | --- | --- |
| Launch and navigation | All five workspaces inspected; reference/checklist work without an upload | Local single-user app only |
| Research chart/replay | Synthetic chart, metrics, replay cutoff, readiness and latest-date recovery inspected; automated preservation and calculation tests | No claim that every chart family or screen width was manually inspected |
| Data inputs | Existing standard/NSE/XLSX parsing and invalid-input tests retained; new byte-identity/replacement/clear tests | The owner's original NSE file was not uploaded again in this audit; its 21-row acceptance was observed in the prior strategy release |
| Upload lifecycle | Real two-file synthetic upload → Education → comparison retained A/B, completed declaration and rolling window 10; explicit clear removed A and requested both inputs | Retention lasts only in the current live session; browser refresh/restart/reconnect durability is not promised |
| Two-stock comparison | Common-date/matched-interval metrics and exports rendered; real 4,856-byte JSON download parsed with comparison, labels and source passports | Price comparison, not total returns, causation, cointegration or a pairs-trade recommendation |
| Strategy labs | Baseline and retest runs observed; saved result/strategy/tab/rule/reference paths tested; stale-input warnings retained | Exploratory same-dataset simulations; no superiority claim |
| Corporate-action restriction | Regression verifies retained ledger/research view still blocks execution after reference navigation | No new action accounting or feed was added |
| After the pattern | Committed form/range/horizon/cohort state, retired selections, direction/horizon/sample chart labels and unchanged plotted values tested | Form edits take effect when Run event study is submitted; statistical validation remains unfinished |
| Concepts | Evening Star search visibly selected its implemented-variant article and returned 3 related matches; clear filters and reference return checked | 131 reference concepts remain; optional historical labs are not newly assigned work |
| Build records | Shared checklist, original-plan map, handbook, work log and report regenerated/updated | Counts measure named gates, not effort-weighted completion |

## State and data contract

`ui_state.py` centralizes a narrow session-only contract. Bytes are copied into
immutable `SessionUpload` values; original files on disk are never modified.
An absent fresh picker is different from a user clearing an active picker.
Generation/last-render/workspace/source guards separate these cases. A visible
Retained in this session caption and Clear button explain the stored copy.
Clearing one comparison input removes the current comparison view until both are
provided; it does not turn the older result into a new result.

Confirmation identities include sorted file-name/content-hash pairs. Reordering
multiple report files alone does not change the declaration; renaming or replacing
bytes does. Declaring completed daily INR observations remains a user statement,
not independent source verification. Source replacement restores its own observed
date context or defaults to available history. Retired dates are clamped to real
observations; no prices or missing sessions are invented.

Strategy results remain independent immutable snapshots. Navigation continuity is
not recomputation. Changed numerical inputs still mark the corresponding saved
result stale; its downloads/charts use original assumptions/prices. There is one
session slot per strategy, not an append-only database. Download records to keep
an external copy. Archive import, reopening and permanent history remain planned.

## Verification record and mistakes corrected

Fresh pre-change suite: **323 passed in90.96s**. Intermediate broad acceptance:
**335 passed in214.51s**, before the final picker-lifecycle and slider-render fixes.
Final post-fix regression: **336 passed in211.85s**, including all323 prior cases
and13 new usability cases. Remote commit and observed CI are recorded separately
in `GITHUB_SYNC.md`; they must not be inferred from local results.

The first date helper incorrectly initialized a range through session state
without an explicit range default. A focused test caught a collapsed end handle;
the helper now declares single/range mode explicitly. A later browser check caught
the separate frontend-reset mismatch described above. The regression now asserts
the explicit outgoing widget value as well as the analysis date. Two initial new
form tests incorrectly treated unsubmitted form edits as committed settings; they
were corrected to submit the intended edits together. No application requirement
was relaxed. A test edited while an older process had already collected it was
rerun from the corrected source.

Mocked empty-pickers alone initially missed real browser cleanup callbacks. The
manual reference round trip exposed this gap; generation/context guards and an
additional stale/current-removal regression address it. Browser automation also
encountered short selector/CDP deadlines and stale snapshots during Streamlit
reruns. Fresh completed-page observations resolved them; these automation failures
are not recorded as application crashes. Windows restricted AppTest runs can hang
while initializing socket support; the authorized test runner with local socket
support was used. No source data was changed to make a test pass.

No numerical strategy, event-study, comparison, indicator or parser engine was
changed in this release. Presentation formatting/column order differs; numerical
exports retain their original schemas. Software tests do not validate investment
performance.

## Remaining friction and highest-value work

1. **Fair strategy comparison:** evaluate baseline and retest using a declared
   common data/cost/exposure/coverage protocol, with frozen definitions and clear
   differences in timing. This remains the next feature, not part of this audit.
2. **Durable research:** save/reopen datasets, exact runs and definitions, with
   versioned identities and migration/privacy rules. Session memory is temporary.
3. **Independent validation:** chronological held-out evaluation, overlap-aware
   uncertainty, benchmarks and experiment discipline before predictive claims.
4. **More analytical scope:** remaining pattern/indicator families, causal
   trendlines, completed multi-timeframe strategy confirmation and further
   strategies, one tested feature at a time.
5. **Usability coverage:** real phone-width testing, keyboard-only end-to-end
   research, screen-reader/contrast review, dense-table/plot simplification and
   contextual help for remaining jargon. Existing skip link/control labels do
   not certify accessibility. No valid mobile viewport was obtained in the
   prior inspection and none is newly certified here.
6. **Later integrations:** licensed feeds, prospective paper ledger, evidence-bound
   AI narration/models, screenshot inputs and production accounts/monitoring.
   Live orders remain outside the current authorization.

Original-plan mapping remains **43 bullets:8 Done,20 Partial,15 Planned**. The
expanded map is **361 tasks:54 Done,48 Partial,247 Planned,12 Optional**; four narrow
workflow gates were added. No whole phase is complete. Learning exercises remain
paused; financial reference content remains available.

## Sources and implementation map

Pinned runtime behavior was checked against local Streamlit1.66.1 signatures and
implementation, with official [widget behavior](https://docs.streamlit.io/develop/concepts/architecture/widget-behavior)
and [file uploader](https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader)
documentation. Later online versions may differ from the pinned runtime.

Coordination: `app.py`, `quant_engine/ui_state.py`; affected presentation:
`actions_ui.py`, `research_ui.py`, `comparison_ui.py`, `event_study_ui.py`,
`backtest_ui.py`, `retest_ui.py`, `learning/pages.py`. Regression:
`tests/test_usability.py`. Shared records: `learning/concepts.py`,
`learning/roadmap.py`, `learning/progress.py` and generated documents. Proof images,
synthetic browser inputs and downloaded runtime JSON remain local under outputs
or Downloads and are excluded from private source publication.
