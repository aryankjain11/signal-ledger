# Signal Ledger · complete project and AI handoff report

Prepared: **16 November 2026, Asia/Calcutta**. Audience: the owner, a replacement
AI coding assistant, or a human developer. This is a transfer of an existing
working project, not a proposal to start it again.

## 1. Read this first

**Continue the existing Python/Streamlit application. Do not rebuild from a short
description of its UI.** The numerical engines, causal timing conventions, tests,
source provenance, educational catalogue and historical decisions are essential
parts of the product. A prettier replacement without those properties would lose
much of the work already done.

The original ambition remains an interpretable quantitative technical-analysis
and trading-research platform. The implemented product is a useful **local,
deterministic, daily-data research prototype for Indian-stock swing research**.
It is not yet the complete AI-powered terminal described in the first prompt.
No strategy has a demonstrated trading edge, and no calibrated success probability
is produced. Passing software tests is separate from validating a trading idea.

The owner asked for this handoff because their current assistant subscription is
ending. They want another assistant to retain the entire vision, understand the
choices and corrections made, and keep building professionally. This handoff does
not implement the next feature or authorize every item on the long-term roadmap.

Use these companion deliverables:

| File | Purpose |
| --- | --- |
| `docs/NEXT_ASSISTANT_START_HERE.md` | Ready-to-paste continuation request, reading order and first-session expectations |
| `docs/ORIGINAL_BRIEF.md` | The owner's complete first prompt, preserved without editing |
| `docs/NEXT_MILESTONE_STRATEGY_COMPARISON.md` | Proposed next feature and precise acceptance gates; **not implemented** |
| `docs/PROJECT_STATUS.md` | Every one of the original 43 phase bullets, with scope and status |
| `docs/MASTER_CHECKLIST.md` | Expanded 361-task, 21-stage roadmap |
| `docs/WORK_LOG.md` | Chronological decisions, implementation, failures, corrections and measured checks |
| `docs/BUILD_REPORT.md` and `docs/PLATFORM_CONTEXT.md` | Living architecture/current-state summary and compact continuation context |
| `docs/GITHUB_SYNC.md` | Observed private publication and remote test evidence |
| Handoff ZIP root `PROJECT_SNAPSHOT.json` | Machine-readable source checkpoint, counts, complete task/phase inventory, dependencies and file hashes |
| Handoff ZIP root `SOURCE_MANIFEST.json` and `VERIFY_HANDOFF.py` | Portable integrity verification for all packaged source files |

The ZIP contains the complete reviewed source under `project/`, including tests,
synthetic data, all documents and the original brief. It intentionally excludes
`.venv`, credentials, private/real uploads, runtime JSON, screenshots and old output
probes. It contains enough source to install and run independently of this chat.

## 2. Connection to the first prompt

The first attachment was titled **AI-POWERED QUANTITATIVE TECHNICAL ANALYSIS &
TRADING STRATEGY ENGINE**. It specifies 22 numbered sections and a final objective.
Its central principle is analytical rigour, statistical validation, interpretability
and reliability ahead of impressive-looking predictions. It expressly says the
product is more than a stock-price prediction model.

On this handoff date, `docs/ORIGINAL_BRIEF.md` was compared with the original
attachment. Both are **50,000 bytes and byte-for-byte identical**, with SHA-256:

`f2c7c3286b7fcd14725b2412f8af5a3dcbad227de38a509626a437173442f160`

The recipient does not need access to the original assistant's attachment folder.
The complete text is in the project archive. This report summarizes it; it does
not replace or quietly narrow its long-term acceptance criteria.

### Original end-user promise

A user should eventually provide a ticker/company, OHLCV CSV/Excel, a chart image,
or data through an authorized provider integration. The platform should explain:
trend and structure; support/resistance; developing/confirmed/invalidated chart
and candle formations; volume, momentum and volatility; alignment/conflicts across
timeframes; the historical evidence for similar setups; exact conditional entry,
stop, target, sizing and invalidation; and reasons to avoid a trade.

The output should combine annotated charts with a coherent report. A no-trade
conclusion is valid. A recognizable shape alone must not become a recommendation.
An LLM may explain numerical evidence but must never invent prices, indicator
values, probabilities, levels or signals. The core must work without a paid LLM.

### Original modules and where they stand

| Original section | Original scope | Implemented boundary and remaining work |
| --- | --- | --- |
| §4 Market data | CSV/Excel, validation, broad timeframes, later provider APIs | Daily generic/NSE uploads work; data passports and a bounded calendar/action layer exist. Broad intraday/monthly acquisition and APIs do not. |
| §5 Trend/price action | Meaningful swings, zones, breakouts, large chart-pattern catalogue | Confirmed pivots, basic structure/zones, breakout lifecycle, doubles and triangle/rectangle prototypes exist. Full catalogue, causal trendlines and richer significance scoring remain. |
| §6 Candles | Single-, two- and three-candle families with context/evidence | Doji/engulfing plus six contextual shadow/star variants exist. The full list and statistical validity do not. |
| §7 Indicators | Configurable trend/momentum/volume/volatility catalogue and interpretation | A tested fixed starter set and momentum/divergence interpretation exist. Many indicators and general period configuration remain. |
| §8 Multiple timeframes | Aligned top-down analysis and conflicts | Daily plus conservative completed prior-week context only; no general confirmation framework. |
| §9 Quantitative pattern research | Occurrence database, target/stop labels, conditional research | Single-stock descriptive forward outcomes and retrospective context baselines exist. Persistent cross-stock database, target-before-stop labels and inference remain. |
| §10 ML | Interpretable baselines, time-safe labels, held-out/walk-forward calibration | Not implemented. No model training, forecasts or calibrated probabilities. |
| §11 Strategies | Multiple exact strategy families and conditional plans | Two long-only daily simulations: fixed breakout and versioned breakout-retest. Other strategies/short execution and general registry remain. |
| §12 Confidence/risk | Separate heuristic scores, trend evidence and validated probabilities | Cost-aware risk/reward and position sizing exist. No validated aggregate confidence score or outcome probability. |
| §13 Images/annotations | Screenshot observations and annotated structured charts | Structured-data Plotly charts/annotations exist. No screenshot input or interpretation. |
| §14 Dashboard/history | Analyzer, report, strategy, research/backtest labs, saved history | Five task-linked workspaces and two strategy labs exist. Session continuity is temporary; permanent history/reopen is absent. |
| §15 AI interpretation | Evidence-bound explanations and question answering | Deterministic explanations/Markdown reports only. No connected language model or chat-over-analysis. |
| §16 Validation/paper | Realistic testing, many performance metrics, prospective paper tracking | Explicit exploratory execution/cost rules and software tests exist. Independent economic validation and paper ledger remain. |
| §17–18 Technology/structure | Python-first modular core, Streamlit initially, later DB/optional React | Python/Streamlit selected; smaller real modules rather than empty proposed directories. No database yet. |
| §19–22 Roadmap/constraints | Incremental delivery, 43 phase bullets, 18 initial gates, no fabricated evidence | Original plan preserved and mapped; no entire phase or all 18 initial gates declared complete. |

## 3. The owner's goals and continuing instructions

1. **Build a useful research site while understanding finance and engineering.**
   Explain exact rules, concepts, examples, limitations and why a design was chosen.
   Maintain the Education and Concepts reference alongside current functionality.
2. **Work incrementally and actually build.** Do not spend the next sessions only
   writing architecture, nor attempt the whole original terminal in one change.
3. **Document meaningful work.** Keep the build log, current report, detailed
   checklist, original-plan status and private repository current.
4. **Learning is not compulsory homework.** The owner explicitly paused learning
   exercises/assignments on 3 November. Existing reference content and optional
   old labs may remain. Do not add quizzes, require answers to progress, or infer
   that the owner has mastered a concept. This overrides earlier exercise steps
   still visible in historical records and numbered items in `AGENTS.md`.
5. **Prioritize features over more data plumbing.** The owner specifically rejected
   automatic/direct corporate-action download work as the next priority. Add file
   adapters only when they enable a selected feature or repair a real defect.
6. **Be professionally careful in finance and code.** Preserve chronology, expose
   assumptions, distinguish observation/signal/trade/evidence, and improve actual
   research usability. Do not force a confident recommendation.
7. **Preserve privacy and scope.** Keep the GitHub repository private; publish only
   reviewed source/tests/synthetic material/docs. No real account data, credentials
   or licensed datasets. No paid service, public deployment or live order execution
   has been authorized by this handoff.
8. **Report actual status.** End completed increments with done/partial/planned
   items tied to the original plan, evidence actually observed, and a sensible next
   step. Do not equate a glossary entry with implemented software.

`AGENTS.md` is the continuing repository agreement. Later explicit owner steering
has priority. Older dated logs are history, not competing current requirements.

## 4. How the scope evolved

The final vision has not been abandoned. The initial implementation was deliberately
narrowed, and the owner added product/reference/research priorities along the way.
Dates below come from the durable work log; the earliest prototype entry is explicitly
retrospective, not a reconstructed minute-by-minute transcript.

| Recorded stage | Decision or owner request | Result / consequence |
| --- | --- | --- |
| Starting prototype, documented retrospectively on 3 Nov | Refine the broad first prompt into a reliable first build | Indian-stock daily, long-only swing research; CSV/XLSX, small deterministic core, charts/report, one explicit simulator; 35 tests recorded at that stage |
| 3 Nov · learning/documentation foundation | Complete checklist, ongoing log, financial explanations, Education page, private GitHub | Shared roadmap/concept catalogues, generated handbook/checklist, two reference/build pages, first lessons, private Signal Ledger repository; 49-test acceptance recorded |
| 3 Nov · daily-data contract | Clarify source/security/session/adjustment provenance | Generic daily contract, passports/hashes and separate NSE UDiFF report preview |
| 3 Nov · unchanged NSE stock-history download | Owner supplied the real download and did not want manual cleanup | Native NSE headers, Indian number formatting, dates, row order and filename-based symbol support; no need to edit that format manually |
| 3 Nov · learning pause | Owner said stop learning exercises and continue product work | Assignments paused; reference and documentation retained; original-plan status becomes a routine deliverable |
| 3 Nov · calendar and actions | Correct actual data-quality/adjustment risks | Offline NSE CM 2026 audit and conservative freshness; reviewed manual split/bonus normalization with execution restrictions |
| 3 Nov · feature-value steering | Owner said corporate-action download support adds too little product/learning value | Further download plumbing deferred; visible analytical and strategy features prioritized |
| 4 Nov · analytical feature bundle | Build breakout/retest, chart/candle/momentum analysis and side-by-side stock correlation | Causal event lifecycle, limited new pattern/candle families, ROC/stochastic/divergence, matched-interval two-stock comparison; 201-test acceptance recorded |
| 5–6 Nov · After the pattern | Turn observations into inspectable historical evidence | Descriptive forward movements, excursions, context baselines, overlap/censoring, occurrence inspection and portable study records; 240 tests and browser/export gates recorded |
| 15 Nov · thorough researcher inspection | Evaluate purpose, usability, working/broken features and current vision | Detailed platform inspection/current-context documents; real chart-bound/state issues distinguished from future scope |
| 15 Nov · reliability increment | Repair the highest-value defects before adding more analysis | Bounded chart geometry, actual counts/readiness, baseline snapshot/stale warnings and task/concept links; 268-test acceptance recorded |
| 15 Nov · next strategy | Build a professional breakout-retest execution strategy | `long-breakout-retest/1`, structural stop, next-open cancellation/expiry/capacity audit, frozen-price inspection and record; 323-test acceptance recorded |
| 15–16 Nov · second usability audit | Check the site like a researcher and reduce effort | File/date/rule/tab continuity, exact-input confirmation, explicit recovery, compact controls, reference-first concepts and clearer outcome/trade presentation; 336 tests |
| 16 Nov · this handoff | Enable continuation with another AI assistant | This report, starter prompt, next-feature specification, verified source package and machine-readable snapshot; no new trading feature |

Important refinements relative to the first prompt:

- **Indian equities and swing research** replace an unspecified market/style for
  the first releases. INR is assumed, with no currency conversion.
- **Deterministic analysis before AI/ML** is both an original principle and an
  explicit implementation choice. Current deterministic reports are useful in
  their own right, not a hidden LLM integration.
- **Custom sequential simulators** make two bounded execution hypotheses auditable;
  a third-party backtest framework was not installed merely to tick a technology box.
- **No empty SQLite/ML/vision modules** were created. Those are real future gates,
  not implemented architecture because folders are named in the original proposal.
- **Two-stock comparison** is an owner-requested addition beyond the main
  single-stock research flow. It does not create a multi-asset portfolio simulator.
- **Education and build transparency** became explicit product deliverables; they
  support research without requiring homework.
- **Research event studies precede predictions.** Historical shapes can now be
  investigated without relabeling descriptive averages as probabilities.

## 5. Exact current status

The original five phases contain **43 implementation bullets**:

| Phase | Done | Partial | Planned | Meaning |
| --- | ---: | ---: | ---: | --- |
| Core technical analysis | 2 | 8 | 0 | Ingestion and confirmed swing gate done; broader analysis families partial |
| Visual analysis/dashboard | 3 | 3 | 3 | Charts/volume/indicator overlays done; catalogue/annotations partial; trendlines/images planned |
| Strategy generation | 3 | 4 | 2 | Sizing, bounded risk/reward and no-trade gate done; strategy catalogue partial |
| Quantitative research/ML | 0 | 3 | 5 | Descriptive research/features/outcomes partial; DB/models/calibration/validation planned |
| Advanced integration | 0 | 2 | 5 | Reports/dashboard partial; AI, paper/history/API/monitoring planned |
| **Total** | **8** | **20** | **15** | **No entire original phase is complete** |

Read `docs/PROJECT_STATUS.md` for each exact bullet. Counts are not estimates of
remaining effort or meaningful completion percentages.

The expanded catalogue has **361 tasks across 21 stages:54 Done,48 Partial,
247 Planned,12 Optional**. There are **131 concepts**. Optional extensions are
separate from the original product's completion criteria. S20 practice items stay
on the historical roadmap but assignments are paused. The machine-readable snapshot
includes every task/status and original phase row, not only these totals.

## 6. The website as a user experiences it

The application runs locally at `http://127.0.0.1:8501/`. It is not a public hosted
service. The sidebar Workspace menu and Research steps navigation lead to five pages.
Typing a research label/ticker does **not** fetch a quote. The app explains this.

### Research dashboard

Start with a labelled 600-row synthetic walkthrough or upload daily data. Review
validation, source/adjustment declaration, replay cutoff and calculation readiness.
The dashboard displays candlesticks, volume, indicators, confirmed structure,
zones and supported observation annotations, with report/evidence/export views.
Patterns & momentum shows lifecycle/candle/chart observations and evidence.
Backtest lab offers the two separate long strategies. Quick references and selected
observations link to concepts and the relevant historical study/strategy.

An older replay slices input **before** analysis. Later uploaded observations
are excluded. The latest-bar button now updates both computation and slider.
Chart geometry is clipped to displayed observations without altering the original
event's anchors/evidence. Captions show actual displayed counts.

Capital/risk/charges/slippage are inside a collapsed simulation expander with a
compact assumption summary. These affect the strategy simulations, not gross event
studies or stock-correlation statistics. Advanced action/descriptive-rule controls
are grouped in the sidebar. Supported controls are not a general indicator editor.

### After the pattern

Uses the single-stock source, replay and descriptive rules. Choose event cohorts,
reference price, direction, horizons, date/context filters and overlap policy;
submit the study definition. Inspect summaries, matched non-event comparisons,
distributions/excursions, individual occurrences and portable evidence.
Form edits become committed settings when the study is submitted.

This is an observational research tool, not simulated trade performance. Outcomes
are gross price movements; charts explicitly identify direction, observation horizon
and actual coverage. Neutral shapes have no fabricated trade direction. Recent
incomplete horizons are reported separately rather than counted as failures.

### Compare two stocks

Use an invented synthetic pair or two generic/NSE daily CSV/XLSX files. Declare
each price basis and confirm completed daily INR observations. Select a shared
period and correlation window. Views show rebased price performance, common-date
drawdown, relative price ratio, Pearson/Spearman/rolling matched-return correlation,
side-by-side technical charts and evidence/price/return downloads.

The two charts are separate Plotly charts, **not synchronized crosshairs**. This
workspace does not import UDiFF ZIPs or apply the single-stock action ledger.
Correlation is descriptive co-movement, not causation, cointegration or a pairs
strategy. Dividends and total returns are not included.

### Education and Concepts

Opens to the searchable Concept library. Each entry distinguishes definition,
calculation/rule, hypothetical worked example, interpretation, common mistake,
source and actual application status. Search/category/coverage filters and clear
filters are available. RSI, MACD and Evening Star are examples, not the whole library.
Some future-feature entries are introductory and do not imply an implemented detector.

The old Start here/Learning lab/lesson material remains optional. Displayed concept
articles omit exercise prompts. Do not turn the paused-learning instruction into
a reason to delete financial explanations or to assign new exercises.

### Build checklist & log

Shows original-plan progress, the expanded roadmap, stage filters and build records.
It reads shared sources/documents. It does not silently mark features done or infer
learner comprehension. These reference/build pages work without any upload.

## 7. Data, analysis and research boundaries

### Accepted data and provenance

- One instrument's completed daily OHLCV observations per standard CSV/XLSX.
  Canonical fields are date/open/high/low/close/volume. See `data.py` for exact
  aliases/rejections; do not promise every arbitrary spreadsheet format.
- Native NSE security-history CSVs work unchanged: mapped headers, day-first dates,
  Indian thousands separators, reversed row ordering and original filename symbol
  handling. The owner supplied an ATHERENERG export and explicitly wanted no manual
  cleaning. The previous browser gate accepted its 21 rows; the file is not bundled.
- EQ-series NSE CM UDiFF-style daily CSV/ZIP input is a **separate schema-subset
  preview**. Real-report acceptance remains incomplete; do not conflate it with
  the accepted security-history download path.
- Strict date/numeric/OHLCV validation, source SHA-256, canonical analyzed-data
  identities, security/source declarations, passports and warnings are present.
  Bad or missing prices are not silently fabricated or forward-filled.
- User declarations are not independent verification of source authenticity,
  completed bars, full history or coherent adjustments. Future/unsupported/zero-volume
  observations and missing expected sessions have distinct meanings.
- The offline calendar snapshot covers **NSE CM 2026 only**, with documented
  amendments/special sessions. Other years/exchanges and synthetic weekdays remain
  unverified. The conservative application freshness cutoff is18:00 Asia/Kolkata;
  this is not an assertion about an exchange's actual close/publication time.
- Reviewed manual split/bonus ledgers can create a coherent adjusted research view.
  Original prices/factors/audits remain available. Dividend-inclusive total return,
  automatic action download/reconciliation and execution share accounting are absent.
  Preserve action-audited execution blocks; do not bypass them for attractive results.

Valid input does not guarantee enough history. For example, a hypothetical21-row
file may support RSI14/RVOL but still need29 more observations for EMA50. Adding
calendar days is different from adding observations. No qualifying setup is a
valid result, not evidence that the website failed.

### Implemented indicators and structure

The current engine computes SMA20/50/200; EMA20/50; Wilder RSI14 and ATR14;
MACD12/26 with9 signal; Bollinger20 at2 population-standard deviations; OBV;
relative volume against the **previous**20 volumes; ROC10; fast stochastic%K14
and%D3. Warm-up/undefined values remain unavailable, not zero. EMA conventions
are pandas `adjust=False` with declared minimum periods. Broader indicator families
and general period configuration remain planned.

Pivots use a fixed three-left/three-right confirmation window. Formation and
first-knowable timestamps are separate. Basic HH/HL/LH/LL structure, approximate
pivot-cluster zones and double-top/bottom geometry exist. Triangles/rectangles use
bounded confirmed-pivot line geometry and lifecycle rules. The wider catalogue
in the original brief is unimplemented, including head-and-shoulders.

Doji and engulfing are initial geometric observations. Hammer, Hanging man,
Inverted hammer, Shooting star, Morning Star and Evening Star add explicit preceding
trend/context variants. The implemented star variant does not require a gap.
Do not silently substitute a textbook's different rule and retain the old version.
RSI/MACD divergence samples indicator values at pivot formation but is only knowable
after the second pivot's confirmation. Detection is not proof of future reversal.

### Three distinct kinds of result

| Result | What it means | What it does not mean |
| --- | --- | --- |
| Descriptive observation (`research-events/1` and legacy event families) | A declared shape/state became knowable at a particular close | An entry, a fill, a validated probability or eventual success |
| Event study (`pattern-outcomes/1`) | Gross movements/excursions after eligible knowledge-time anchors, with coverage/context conventions | Portfolio P&L, executable short returns, target-before-stop labels or causal alpha |
| Strategy run (`long-breakout/1` or `long-breakout-retest/1`) | A chronological simulation under exact fill/cost/position rules | A live trade, held-out validation or a calibrated forecast |

Do not merge these layers because the words breakout or retest appear in all three.
Changing descriptive `ResearchRules` does not redefine either execution strategy.

### Event-study conventions to preserve

Default reference is the next observed open after knowledge close t; horizon h
ends at close[t+h]. Horizon1 is therefore that next bar's open-to-close move.
Detection-close reference is also available as an observational convention.
Excursions exclude the detection bar. Signed MAE is nonpositive. Bearish direction
alignment negates price change; it is not a costed/executable short trade.

Incomplete full horizons remain null/censored, not failed events or partial-window
averages. Multiple geometries can share a price path and are not independent samples.
Deterministic within-cohort spacing reduces selected overlap but does not create
independence across cohorts/stocks. Context controls are retrospective same-stock
non-event references; they are not randomized controls or market-model alpha.
Known raw-price action crossings have conservative exclusion rules. See
`EVENT_STUDIES.md` for exact context matching, limits and exports.

### Correlation conventions to preserve

Compute each stock's return on its own native observation interval, then match
**both start and end dates**. A Friday-to-Tuesday return must not be paired with
Monday-to-Tuesday simply because both end Tuesday. No fill/bridge/shift is allowed.
Overall coefficients require10 matched intervals; constant returns are unavailable.
Spearman ranks round returns to12 decimals to stabilize ties. Rolling windows are
5–252 matched intervals, default20. Small-sample and unmatched-coverage warnings
are intentional. Volatility is per matched interval, not annualized.

## 8. The two strategies that actually exist

### Fixed breakout baseline · `long-breakout/1`

After a completed close exceeds the prior20 highs, is above EMA50 and has
RVOL>=1.2 with valid ATR14, try entry at the next observed open. Default stop is
2 signal-bar ATR below the slipped entry; target is2 gross risk multiples; maximum
hold10 observations. Reference levels displayed at the latest close are illustrative
and must be recomputed from the actual next open. The existing baseline engine is
a control: do not change its rules accidentally while adding comparisons.

### Breakout-retest · `long-breakout-retest/1`

At a fresh bullish close crossing the prior range high plus0.1 prior-bar ATR,
require volume1.2 and close above EMA50. Freeze the prior level and ATR. Wait for
a **later** band-touching held retest that closes at/above the level and above EMA50.
Freeze a structural stop below min(retest low, level), with0.25 ATR buffer. Make
one entry attempt at the next observed open. Lost level, excessive gap, invalid
stop, nonpositive net reward, zero affordable shares, expiry and busy capacity
have explicit audited outcomes. No hindsight purchase at the earlier retest low.

Defaults: lookback20, breakout buffer0.1 ATR, retest tolerance0.25 ATR,
invalidation0.5 ATR, retest window10, stop buffer0.25 ATR, maximum entry gap1 ATR,
target2 grossR, maximum hold10. Expiry is checked before accepting a retest on
the deadline; default retest ages are1–9. A scheduled next-open attempt has its
own boundary convention. Read the full frozen specification before changing any
chronology or asserting equivalence with the baseline.

### Shared execution assumptions and limits

Default capital₹100,000; risk budget1%; blended charges10bps/side; adverse
slippage5bps/side; prior-volume participation cap1%. Whole shares are constrained
by risk, cash and prior observed volume. There is one position and no leverage,
pyramiding or overnight short-stock execution. Planned risk is not maximum loss.
Adverse gaps can exceed it; same-bar stop/target ambiguity uses stop-first logic.
Opening gap/exit/holding/cutoff precedence is documented and tested.

This is not a statutory tax/brokerage calculator, a spread/auction/circuit model,
partial-fill simulator or portfolio engine. End-of-file exits are artificial and
labelled; they must not be confused with naturally completed setups. Pending retest
setups remain pending at the replay cutoff. Equity includes declared liquidation
cost conventions rather than only realized trade profit.

## 9. Session continuity is not permanent history

Baseline and retest each have one immutable session result slot. Original-run
inputs/settings and outputs remain together; changed actual numerical inputs
make the corresponding record stale. Stale downloads belong to the original run.
Retest inspection uses saved original prices, not a newly uploaded chart.

Files are copied into immutable `SessionUpload` objects in session memory. This
survives tested reference/workspace visits, including when Streamlit omits a file
picker. Recreated picker generations and active workspace/source/render guards
prevent delayed cleanup from erasing retained bytes. An intentional current-picker
removal or explicit Clear forgets the session copy. Original disk files are unchanged.

Completed-bar declarations attach to exact filename/content-hash identities;
replacing/renaming files needs confirmation again. Reordering multi-report input
alone does not. Date ranges are remembered per source/pair and recovered against
real observed options. Programmatic resets explicitly update the frontend control.

**No database, permanent save/reopen workflow, archived-record importer or
append-only research history exists.** Do not promise continuity across a server
restart, browser refresh/reconnect or expired session. Download JSON/CSV to keep
external records. These distinctions were central to the latest reliability fixes.

## 10. Engineering architecture and source map

The application uses Python3.13; locally recorded runtime3.13.7. Pinned direct
dependencies: NumPy2.3.3, pandas2.3.2, Plotly6.9.0, Streamlit1.66.1 and
openpyxl3.1.5. Development adds pytest9.2.0. Pin files are authoritative; version
availability/compatibility must be checked in a new environment before upgrading.
TA-Lib, scikit-learn, FastAPI, React and a database are not current dependencies.

| Source area | Responsibility |
| --- | --- |
| `app.py` | Streamlit composition, source/declaration/replay, task routing, analysis/cache coordination |
| `quant_engine/models.py` | Dataclasses: Settings, ValidatedData, Pivot, Analysis, ResearchRules, BacktestResult |
| `data.py`, `nse_quotes.py`, `nse_files.py` | Generic daily parsing/validation, accepted NSE security-history mapping, separate report preview |
| `datasets.py`, `calendar.py`, `corporate_actions.py` | Passports/hashes, bounded quality/freshness, reviewed action research/policy |
| `indicators.py`, `patterns.py`, `research.py`, `analysis.py` | Indicators, causal structure/geometry, versioned descriptive events, assembled analysis and deterministic reports |
| `strategy.py` | Original fixed breakout signal, sizing and sequential simulator |
| `retest_strategy.py` | Versioned chronological retest simulator and decision/transition/trade/equity tables |
| `saved_backtest.py`, `retest_records.py` | Immutable strategy records, identities and original-run serialized evidence |
| `event_study.py` | Pure occurrence/cohort/measurement/context/coverage research logic |
| `comparison.py` | Pure two-stock alignment, metrics and synthetic-pair fixture |
| `charts.py` | Data-grounded Plotly geometry with visible-period bounds |
| `*_ui.py`, `readiness.py`, `workflow_ui.py` | Presentation, controls, readiness, navigation and direct reference/task links |
| `ui_state.py` | Narrow session upload/date/tab/selection continuity and explicit recovery |
| `learning/concepts.py`, `roadmap.py`, `progress.py` | Shared concept, expanded-task and original-43-phase sources of truth |
| `learning/pages.py` | Reference and read-only build-journal UI |
| `scripts/export_learning_docs.py` | Generates handbook, master checklist and original-plan status |
| `scripts/source_manifest.py`, `package_source.py`, `package_handoff.py` | Reviewed publication allow-list/credential scan, source ZIP and portable handoff ZIP |
| `tests/` and `.github/workflows/tests.yml` | Numerical, chronology, UI, provenance and documentation checks; clean Linux regression workflow |

Conceptual pipeline:

```text
file bytes → parse/validate → source passport + declarations
           → observed replay slice → optional reviewed research adjustment/policy
           → causal indicators / confirmed events → Analysis
           ├─ charts + deterministic report/evidence
           ├─ descriptive event study
           └─ one of two exact strategy simulators → immutable session record

two independent daily files → native returns / matched intervals → comparison

shared concept/roadmap sources → website reference/status + generated Markdown
```

Source hashes, analyzed/visible hashes, study IDs, calculation/request identities
and strategy versions serve different purposes. Do not replace them all with a
single convenient timestamp or a random run identifier. Consult the actual record
builders before changing serialization. Current schemas include `saved-backtest/1`,
`breakout-retest-run/1`, `pattern-outcomes/1`, and detector rule versions.

The local workspace is an exported working directory, **not a local Git checkout**
at this checkpoint. Previous uploads used the connected GitHub Git-data API because
the local Git client had no saved login. A replacement assistant may use a normal
authenticated clone in a new folder; compare first and preserve owner changes.
Do not assume access to the previous assistant's tools, credentials or chat.

## 11. Verification and what it proves

Latest accepted local application regression before this documentation handoff:
**336 passed in211.85s**, all323 prior cases plus13 new usability cases.
Accepted source commit:
`48c9b9d44f70cec696f8ad53dc49e5b78605fe23`.
GitHub Actions run43748677879/job132917552071: **336 passed in57.30s**, inspected
successful job and decoded log on Ubuntu26.04.1/Python3.13.18.

Before this handoff's edits, private `main` was independently read as
`0442e36912ca37bcb34d03760b61d82280745a55`, the later documentation audit.
All87 reviewed local source files matched its tree. Its separate push run43749507116
was also observed completed/successful; no separate test count is inferred without
reading that log. The handoff documents/packager are later additions. The archive
snapshot records their published head separately to avoid calling an old hash latest.

For the handoff-only increment, **15 documentation/reference checks passed in12.03s**.
The91-source-file archive passed ZIP integrity and every payload SHA256. Its
standalone verifier passed after extraction and correctly rejected an intentionally
modified README test copy; the copy was restored and reverified. These checks are
separate from the historical full336-case application regression. No new numerical
engine/UI behavior was introduced during this transfer.

| Test module | Main evidence |
| --- | --- |
| `test_engine.py` | Input failures, indicator arithmetic/seeds, pivots/geometry, sizing, original execution/P&L and causal invariance |
| `test_app.py` | Core Streamlit upload/replay/report/backtest flows |
| `test_learning.py` | Concept integrity/search, generated docs, original-phase map and reference/build pages |
| `test_nse_files.py`, `test_nse_quotes.py` | Separate report-preview and native security-history contracts/negative cases |
| `test_calendar.py`, `test_corporate_actions.py` | Scope/cutoff/replay and action identity/normalization/execution blocks |
| `test_research.py` | Descriptive lifecycle/chart/candle/momentum timing and evidence |
| `test_comparison.py` | Native interval alignment, correlation/constant/coverage cases and comparison UI |
| `test_event_study.py` | Measurement/coverage/censoring/context/overlap/action conventions and study UI |
| `test_reliability.py` | Narrow-period chart clipping, readiness/counts, retained/stale baseline and workflow links |
| `test_retest_strategy.py` | Independent arithmetic, chronological every-prefix behavior, cancellation/capacity/expiry/fill boundaries |
| `test_retest_workspace.py` | Immutable records, saved-price inspection, stale rules and strategy/reference switching |
| `test_usability.py` | Exact-file confirmation, retained bytes/settings, explicit clear, retired callbacks, valid dates/options and outgoing frontend reset values |

The browser audit manually exercised the main synthetic/user-file routes, both
strategy labs, reference navigation, correlation setting/file retention, explicit
clear, concept search and real downloads. The last usability pass downloaded and
parsed comparison JSON and visibly checked slider date/600-row analysis agreement.
The real21-row NSE file's acceptance/no-trade behavior was checked in the prior
strategy release, not uploaded again in the last usability audit.

Recorded synthetic trade counts are demonstrations of code paths, never market
performance evidence. No valid phone-width acceptance, comprehensive screen-reader
review, production penetration/load test or independent financial validation has
been completed. Existing screenshots are historical proof, not automated certification.

### Important bugs already fixed

- Older pattern geometry previously stretched selected chart ranges. Drawing
  vertices are now bounded while original evidence stays intact.
- A baseline run disappeared after ordinary UI reruns; immutable per-strategy
  session results now survive tested paths and display staleness correctly.
- Replay dates, correlation window and omitted-widget rules/tabs reset after
  reference visits. They now retain tested session context.
- Initial mocked uploader tests missed real cleanup callbacks. Retired-picker
  generations/context guards now distinguish cleanup from deliberate removal.
- A latest-date action originally updated calculation but left the visible slider
  behind. Regression now checks outgoing widget `set_value` and serialized date.
- Range mode requires an explicit single/range default in the pinned runtime;
  initializing Session State alone once collapsed a range handle.
- Earlier test probes used widget positions or treated unsubmitted form edits as
  committed. Corrected tests use intended labels/keys/submission. Historical failures
  and corrections are retained in the log rather than hidden.

Do not simplify these guards just because one happy-path screenshot still works.
File lifecycle, state and causality regression tests protect user effort and trust.

## 12. Remaining work and recommended sequence

**Next bounded product feature: fair baseline-versus-retest strategy comparison.**
The two stock-comparison page and the two strategy selectors do not implement this.
See `NEXT_MILESTONE_STRATEGY_COMPARISON.md` for a continuation-ready proposal.

Then build durable dataset/run/experiment persistence and independent chronological
validation in an order consistent with their dependencies. A minimal versioned
experiment record helps freeze evaluation before testing held-out periods. Do not
postpone useful deterministic features until an entire data vendor stack exists.

Broader pending families include:

- Additional chart/candle patterns, trendlines/channels, richer zones/structure and
  more indicators with explicit rules, evidence, warm-up and time-availability tests.
- General resampling/complete higher-period availability and multi-timeframe
  strategy confirmation; intraday is a separate timezone/session/data-quality scope.
- Additional stop/target/entry/strategy families and a common versioned registry.
- Persistent occurrences, target-before-stop labels, dependent-data uncertainty,
  selection-bias/benchmark/held-out/walk-forward evaluation and experiment records.
- Calibrated ML only after label/data/validation gates; evidence-bound LLM narration
  only after structured evidence interfaces. Neither is a shortcut to validation.
- Screenshot mode kept visibly separate from precise structured-data research.
- Prospective paper setups with append-only timing, triggered/not-filled/expired/
  invalidated states and actual subsequent outcomes. No live broker orders.
- Licensed provider adapters, wider verified calendars and action/total-return
  handling where required by a chosen research question.
- Phone/keyboard/screen-reader/contrast work, dense-table simplification and remaining
  contextual terminology help. A full web-framework migration is not the default
  next step; the existing core is intentionally independent enough to permit it later.
- Production security, accounts/isolation, deployment, backups, monitoring and
  licensing review before a multi-user/public service.

### Original initial acceptance gates remain bounded

§21 gates1–4 are implemented for supported daily files and starter indicators.
Gates5–7 cover basic supported structure/zones/candles. Gate8 remains partial:
doubles and triangle/rectangle prototypes do not implement head-and-shoulders.
Gate9 has coordinates/status for supported observations, not a universal completed
schema/catalogue. Gate10 is partial daily/prior-week context. Gates11–14 apply to
bounded deterministic reports, conditional strategies, risk math and actual-data
annotations. Gate15 has explicit insufficiency/readiness and limited calendar
assessment, not independent provider verification. Gates16–18 have current numerical/
chronology tests and documented local launch; new features must pass independently.
This is not a claim that all18 original gates or the final product are complete.

## 13. Setup, migration and practical continuation

### Existing Windows computer

Workspace:
`C:/Users/aryan/OneDrive/Documents/ChatGPT/Projects to Build/quant-research-engine`.
An existing `.venv` is prepared. `Start App.cmd` launches the app. Or:

```powershell
cd 'C:\Users\aryan\OneDrive\Documents\ChatGPT\Projects to Build\quant-research-engine'
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Do not assume the server is currently running solely because this address was used
in earlier checks. Inspect current state and avoid launching a duplicate server.
Bind locally as configured; public exposure is a separate decision.

### Fresh Windows setup from the ZIP or authenticated clone

Extract the archive, enter `project/`, then:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Fresh macOS/Linux setup

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m streamlit run app.py
```

Open the loopback URL shown by Streamlit. `requirements-dev.txt` includes runtime
dependencies plus pytest. No API key, broker account or paid AI service is required.
An installed environment is platform-specific; do not transfer the Windows `.venv`.
Fresh target-machine installation is a recipient acceptance step, not something
this handoff can certify before that machine is available.

The historical Windows restricted runner sometimes hung while initializing
Streamlit/AppTest socket support. Running with authorized local socket access
resolved that environment issue; it was not repaired by changing finance code.
Another assistant's permissions/tooling differ. Browser selector deadlines and
stale intermediate reruns were also observed; verify the completed UI before
classifying an automation timeout as an application crash.

### Documentation and packaging

After editing shared catalogues, regenerate and run relevant checks:

```sh
python scripts/export_learning_docs.py
python -m pytest tests/test_learning.py -q
python scripts/package_source.py
```

Use `scripts/package_handoff.py --help` to reproduce a dated portable handoff with
source hashes and full status snapshot. ZIP verification needs only Python's
standard library; application installation/tests need the pinned dependencies.

### GitHub and access

Repository: `https://github.com/aryankjain11/signal-ledger`, branch`main`, **private**.
The next assistant needs owner-authorized access through its own supported GitHub
connection or an authenticated local clone. It does not inherit this assistant's
connector login. Do not request a token to paste into a chat, scrape credentials,
make the repository public or overwrite a changed remote head.

The portable package is a working source snapshot, not complete `.git` history.
The private repository contains the publication commits; the chronological work
log records intent/corrections that commit messages alone cannot explain.
Use normal non-forced updates and verify what actually reached the branch.
Never interpret a tool request as proof of successful publication.

## 14. First session for the replacement assistant

1. Read the starter prompt, `AGENTS.md`, this report, original brief and current
   status/priorities. Confirm that the owner wants continuation rather than a rewrite.
2. Verify the package hashes or inspect a fresh authenticated clone/current head.
   Preserve changes newer than this snapshot. Read the tail of `WORK_LOG.md`.
3. Install/use the correct environment; run the baseline suite and report actual
   results. Do not claim336 tests passed on the new machine before running them.
4. Launch the app and inspect the main user journey. Keep real data local; the
   labelled synthetic fixtures are sufficient for initial development.
5. State a bounded acceptance gate for fair strategy comparison. Read both execution
   engines and frozen record builders before deciding what is genuinely comparable.
6. Implement a usable increment with meaningful arithmetic, chronology, policy,
   empty/small-sample, saved-state and browser checks. Keep the app working.
7. Update the shared catalogue/status only for gates actually passed, regenerate
   records as needed, append the work log/current report and publish verified
   reviewed changes to the private repository using available authorized tools.
8. Return a concise done/partial/pending update. Explain relevant finance through
   product/reference content; do not restart homework.

## 15. Document precedence and remaining unknowns

Newest owner instructions override this snapshot. `AGENTS.md` plus current source,
shared catalogues and measured evidence govern implementation. Latest sections of
living reports supersede older historical snapshots. Dates in earlier reports are
not claims that the feature set stopped changing then. Some earlier notes recommend
the retest strategy; it is now implemented, so strategy comparison is next.

Unknowns are explicit: whether either strategy generalizes; a licensed historical
universe/survivorship policy; final production hosting/accounts/licensing; the
eventual provider/LLM/model choice; the exact return of the paused learning scope;
and the next assistant's environment/access. Do not invent answers to make the
handoff appear more complete. Ask only when a real dependent decision cannot be
resolved from current source and owner instructions.

The next assistant should leave the owner with a stronger, understandable research
tool after each increment, with claims no stronger than the evidence.
