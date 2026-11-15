# Signal Ledger: product vision, current state and researcher inspection

**Inspection date:** 15 November 2026, Asia/Calcutta. **Audience:** the owner, future users, developers and AI collaborators. **Review type:** hands-on researcher walkthrough, reproducible application probes, source review and a fresh regression run. **Scope:** the existing local application, not a newly implemented feature release.

## 1. Overall assessment

**Post-inspection follow-up, 15 November:** the later reliability increment repairs
F01/F02 and the bounded F03/F04 readiness/count scope; F05–F07 receive task/reference
links and clearer baseline/detector/cost scope. See [implemented rules and current
acceptance](RESEARCH_RELIABILITY.md). The body below records the earlier inspection,
not current claims that repaired defects remain open. Other findings remain.

**Evidence correction:** the original supplemental F02 probe selected the first
checkbox, which enabled an action ledger rather than toggling Bollinger bands.
The stated overlay interaction was inaccurate. A later label-based reproduction
against published pre-change `a482bc7` confirmed the backtest result disappearing
after the actual overlay change, with zero exceptions. The finding was valid;
the new regression checks use the labelled control. Also, the inspection's narrow
Research/Compare state probe did not establish all-workspace retention: a later
browser check found reference-page input resets, now repaired for sidebar inputs.

Signal Ledger is a working, local technical-research prototype for Indian-stock swing research using daily uploaded prices. It can turn a supported file into indicators, confirmed price structure, a limited set of pattern observations, charts, a conditional baseline trade plan and an exploratory backtest. It also supports descriptive pattern-outcome studies and two-stock comparisons. Its numerical foundations are more developed than its end-to-end user experience.

It is useful today for an individual who already understands basic technical analysis and is willing to inspect assumptions. A beginner can learn from its reference library, but still needs help connecting the controls and tables into a coherent research process. It is not yet the complete AI-powered, statistically validated research and strategy platform described in the original brief.

The most valuable strengths are explicit information timing, input checks, reproducible evidence, restrained probability claims and separation of observations from trade simulation. The most urgent product gaps are chart-window correctness, result continuity, data-readiness communication and clearer connections between workspaces. Broader missing capabilities include saved research history, a strategy catalogue, held-out validation, a historical pattern database, automatic data acquisition and AI interpretation.

**Verdict:** suitable as an exploratory personal research workbench; promising engineering foundation; incomplete as a polished research product; no demonstrated investment edge. Passing software tests is not evidence of profitable trading.

### What was actually observed

- All five workspaces opened: Research dashboard, After the pattern, Compare two stocks, Education and Concepts, and Build checklist & log.
- The original owner-supplied NSE security-history CSV loaded in the browser without editing. Completed-bar confirmation was required before analysis.
- The file contained 21 observations. RSI was available; EMA50 was unavailable. The quality page explained short history and reported eight-session staleness relative to its current offline calendar assessment.
- The synthetic baseline backtest ran and displayed a trade ledger, returns and drawdown. A separate application probe reproduced its results disappearing after an unrelated overlay change.
- Event-study defaults produced 21 included occurrences, six overlap exclusions and 19 complete outcomes at the 20-observation horizon. A downloaded record contained 84 outcome rows, 536 baseline rows and 24 summary rows.
- Two-stock defaults showed 150 common price dates, 149 matched return intervals and Pearson correlation rounded to 0.682. These are synthetic demonstration values.
- Concept search for RSI returned 17 related entries, including its calculation, worked example and misconception warning.
- A chart-component reproduction found annotation coordinates outside a selected three-observation window. Details and a repair gate appear below.
- Fresh regression: **240 passed in 99.08 seconds**. All 70 audited files matched the published source snapshot.

## 2. The intended product and final vision

The project began as an **AI-powered quantitative technical analysis and trading strategy engine**, not simply a price predictor. Its purpose is to help a researcher move through an explicit chain:

**Data → trustworthy context → observable patterns → historical evidence → conditional strategy → risk evaluation → understandable explanation → prospective review.**

In the intended finished product, a user could supply structured price data, identify a ticker for licensed retrieval, or provide a chart screenshot for an appropriately limited visual interpretation. The system would examine trend, support/resistance, chart formations, candles, volume, momentum and multiple timeframes. It would compare similar historical setups, distinguish strong evidence from weak evidence, construct exact conditional trading plans and explain when no trade is justified.

Statistical models and an optional language model would sit on top of reliable numerical outputs. They would not invent values, fabricate historical evidence or attach arbitrary success probabilities. A complete platform would preserve experiments, reproduce prior runs, evaluate rules chronologically, account for costs, and track prospective paper outcomes before suggesting that a predictive relationship generalizes.

### The questions it ultimately intends to answer

1. What is the stock doing, and what observations support that description?
2. Where are important price levels, and how were those levels obtained?
3. Which patterns are developing, which are confirmed, and when were they knowable?
4. What do momentum, volatility and volume add—or contradict?
5. Do completed higher timeframes agree with the proposed interpretation?
6. How did sufficiently comparable historical setups behave, with what sample limitations?
7. Is there an exact strategy hypothesis with entry, invalidation, exits and expiry?
8. What exposure, potential loss, costs and gap risks does that hypothesis imply?
9. Does the hypothesis survive suitable independent evaluation?
10. Can a reader inspect and reproduce the evidence behind the explanation?

The current application answers meaningful portions of questions 1–4 and 10, a conservative portion of 5, a descriptive portion of 6, and one narrow experimental version of 7–8. It does not yet establish question 9.

### Scope decisions made during development

- Indian stocks, daily observations and swing research are the chosen initial focus. INR is assumed; there is no currency conversion.
- One symbol per uploaded daily-data file is the basic analytical unit. A separate comparison page handles two files.
- Numerical analysis, outcome research, execution simulation and explanation remain distinct components.
- Structured OHLCV is authoritative for calculations. Screenshot analysis remains planned.
- Feature development takes priority over further file adapters unless data reliability blocks a selected feature.
- Reference explanations remain important. New learning exercises and assignments are paused at the owner's request; existing lessons/labs remain available.
- Live order placement is outside current authorization. A broker connection or public deployment is not implied by a working local website.

## 3. What the product currently does

The most accurate current description is:

> A local, deterministic daily-price research workbench with supported file ingestion, technical observations, a single strategy experiment, descriptive outcome research, two-stock comparison and a shared reference library.

The website is built with Streamlit and Plotly. Python, pandas and NumPy perform the calculations. There is no connected LLM, trained predictive model, automatic stock-price feed or persistent research database. Entering a research label does not retrieve prices. A private GitHub repository stores the reviewed software and documentation; it does not host the running application or the user's market-data uploads.

### Feature inventory

| Area | Current capability | Boundary / remaining work |
| --- | --- | --- |
| Standard uploads | Single-stock daily CSV and XLSX | Explicit supported columns/dates; no general data-mapping wizard |
| NSE security history | Native export formatting, newest-first sorting, number/date normalization | Identity may come from filename; source authenticity and adjustment basis remain declarations |
| NSE daily reports | UDiFF CSV/ZIP preview, instrument selection and synthetic walkthrough | Separate from security-history support; full permitted real-report acceptance remains pending |
| Validation | Duplicate dates, invalid OHLC, nonfinite/missing values, negative volume and ambiguous daily dates rejected | No independent verification of vendor truth or security listing history |
| Data provenance | Raw/source and visible-data hashes, passport, normalization/quality records | File records do not provide saved-run history or a permanent data store |
| Calendar checks | Bounded offline NSE CM 2026 snapshot, missing/unexpected/future-date review and freshness | Other years/exchanges and automatic amendment updates remain pending |
| Corporate actions | Reviewed manual split/bonus ledger; optional adjusted research; audit/factor exports | No automatic reconciliation, dividend-inclusive total returns or share-accounting execution |
| Indicators | SMA20/50/200, EMA20/50, Wilder RSI14/ATR14, MACD, Bollinger20, OBV, RVOL, ROC10 and fast stochastic | Most periods are fixed; larger indicator catalogue and general configuration remain incomplete |
| Structure | Confirmed swings, HH/HL/LH/LL and basic trend/range classification | Broader strength, channel and regime framework pending |
| Levels | Approximate pivot-cluster support/resistance zones | Not a complete dynamic trendline/level-scoring system |
| Breakouts | Explicit break, retest, failure, continuation and expiry observations | Descriptive detector; changing it does not replace the fixed baseline strategy |
| Chart patterns | Double top/bottom; rectangle; ascending, descending and symmetrical triangles | Heuristic geometry; head-and-shoulders, flags, wedges and other requested families missing |
| Candles | Doji/engulfing geometry plus six contextual shadow/star variants | Remaining catalogue and stronger location/conflict research pending |
| Momentum | RSI/MACD/ROC/stochastic facts; delayed confirmed-pivot RSI/MACD divergences | Not a calibrated directional score or complete volume-flow framework |
| Timeframes | Daily analysis and conservative prior-week context | Latest calendar week excluded; no general intraday/monthly confirmation workflow |
| Charts | Interactive candles, volume, RSI, averages, optional bands and annotations | No editing/synchronized crosshairs; selected-window annotation issue identified |
| Trade plan | Conditional reference plan or explicit no-trade state | One baseline only; no broad strategy generator |
| Risk/sizing | Whole-share cash, risk and prior-volume caps; estimated fees/slippage | No full exchange/broker-specific charges, tick/lot model or portfolio risk engine |
| Backtest | One long breakout strategy, next-open chronology, stop/target/time exits, gap handling and marked equity | Same-data exploratory evaluation; results are transient in the UI |
| Event studies | Forward movements, MFE/signed MAE, contexts, censoring, spacing, matched non-event baselines and inspection | Descriptive single-stock research; no causal alpha, independent inference or predictive validation |
| Two stocks | Common-date indexing, relative performance, drawdowns, matched-return Pearson/Spearman/rolling correlations and two technical charts | Two files only; not cointegration/pairs trading, a correlation matrix or sector/universe research |
| Reports/exports | Deterministic Markdown, JSON and CSV evidence/ledgers | No unified polished PDF/HTML product report or re-importable saved-study workflow |
| Education | 126 searchable concepts; worked definitions; explicit implementation labels; existing labs | Contextual one-click explanations are not integrated throughout analytical pages |
| Progress records | Shared checklist, phase mapping, journal, GitHub and automated tests | Development history is not user analysis history |
| AI/ML | Original architecture and reference material describe future roles | No connected narration, trained models, calibrated probabilities or model registry |
| Operations | Local startup, loopback binding, pinned dependencies and private source repository | No production hosting, accounts, multi-user isolation or operational monitoring acceptance |

## 4. A researcher's journey through the five workspaces

### 4.1 Research dashboard

**Useful today:** choose a synthetic walkthrough or supported file, confirm completed bars, declare a price basis, review indicators/structure, inspect patterns, read a report, test the baseline and export evidence. Replay moves the information cutoff, rather than merely moving a visual cursor over a fixed future-aware result.

The 600-row synthetic walkthrough loads immediately. Synthetic labeling is prominent and the current engine can produce an explicit no-trade decision. The page avoids manufacturing a probability. The original NSE upload worked without manual column changes and identified the file format, dates and sorting automatically.

**Friction:** the landing page does not clearly present a short sequence such as upload → check readiness → inspect evidence → research outcomes → test a strategy. The workspace selector is in the sidebar, which was initially collapsed in the observed browser session. Important data-quality information is under Data & exports. Large charts, several tab layers, raw field names and long evidence tables require considerable scrolling and financial vocabulary.

In the 21-observation file, the top summary showed an insufficient structure state and a numeric RSI; EMA50 was not available. More explanation existed lower down and in the quality page. A new user would benefit from a top-level readiness panel naming which analyses are available and exactly which require more history. Successful ingestion should not look like complete analytical readiness.

The sentence “Latest 250 sessions shown” is hard-coded even when only 21 observations are uploaded. It should state the actual displayed and available counts. This is a small but visible trust issue.

### 4.2 After the pattern

**Useful today:** define event cohorts, timing reference, direction convention, horizons, overlap policy, trend/volume filters and event-date range. Review complete versus incomplete samples, forward movements, excursions, context-matched non-event comparisons, individual examples and a portable audit.

The default synthetic run reproduced its previous counts. Empty horizon selection returned an understandable warning. Neutral Doji observations produced zero included events in pattern-direction mode with an explanation; switching to upward-price mode produced a valid study. Those are good examples of the product declining to invent an interpretation.

**Friction:** the user needs to understand “cohort,” detection versus formation, next observed open, directional alignment, thinning and matching coverage before reading the charts correctly. The definition form is long. The page also retains capital, risk-budget, fee and slippage controls from the shared sidebar even though its gross outcome calculations do not use them. The exclusion is stated, but the visual relationship remains confusing.

A positive bearish-aligned outcome means a favourable downward price move. That is a reasonable research convention, but each graph/table should repeat its active perspective prominently. The same percentage can otherwise be mistaken for an ordinary long-stock return.

The matched baseline is retrospective, same-stock and context-bucket based. It is not a forecast trained only on earlier observations, a market/sector abnormal-return model or causal evidence. Controls and cohorts can share market episodes. The application discloses these limitations; the interface should keep the coverage and sample cautions close to the chart, not require interpretation across several sections.

The audit is detailed but saves only when downloaded. There is no saved study list, rerun-from-record interface or persistent experiment catalogue.

### 4.3 Compare two stocks

**Useful today:** compare two uploaded stocks over a common observation period, index both to 100, examine drawdowns and relative performance, inspect both technical charts and calculate return correlation on matching intervals. Both the start and end of each return interval must match; prices are not forward-filled to manufacture pairs.

The demo displayed 150 common price dates and 149 matched return intervals, with correlation rounded to0.682. A single-date selection returned an explicit error explaining the two-common-date minimum rather than crashing. Identical-content upload handling and constant/short/missing-date cases have coverage in the existing regression tests.

**Friction:** two dense technical charts are difficult to compare comfortably with the sidebar open. There are no synchronized crosshairs or a shared hover cursor. The time-window correctness issue described below can undermine a user's belief that both plotted histories respect the chosen period. Common-date drawdown can miss extremes on dates absent from the paired sample; the current disclosure correctly limits the claim.

This page does not accept an action ledger or UDiFF ZIPs, unlike parts of the research dashboard. The difference is disclosed but should be clearer before users attempt to reuse every supported input flow. The selected stock files do not automatically populate a cross-stock event-study database.

### 4.4 Education and Concepts

**Useful today:** a large searchable reference library with original definitions, worked examples, mistakes to avoid, sources and implementation coverage. Searching RSI yielded17 related matches and the relevant concept explained both the numerical rule and why RSI is not a probability. Filters distinguish current engine behaviour from concepts that are only explained.

**Friction:** understanding a term in a chart generally requires navigating away to a separate workspace and searching manually. Some entries remain concise vocabulary rather than a detailed applied guide. The default Start here material still leads with a learning route, practical milestone and existing exercises. That material was intentionally retained, but the analytical workflow should present reference help first and make optional lessons distinct from active assignments.

The current reference page is a strength. It is not a substitute for a clear answer to “what does this result mean for the file I just uploaded?” within the research page itself.

### 4.5 Build checklist & log

**Useful today:** inspect the implementation roadmap, original phase mapping and chronological work record. Counts are explicitly described as work items rather than effort percentages or learning mastery. The page states that assignments are paused.

**Friction:** 351 tasks and a long development journal are appropriate for the owner/developer but not an onboarding path for a new researcher. The default stage is the learning/version-control foundation, not the latest usable feature. It is a build-management workspace; users should not mistake it for analysis history or saved studies.

## 5. Reproducible issues and improvement register

Priority meanings: **P1** = address before relying on the affected research workflow; **P2** = address in the next usability/reliability increment; **P3** = later polish or maintenance. These are review priorities, not claims of financial loss. No critical crash was observed in the exercised paths. Existing tests can pass while a new behavioural defect remains.

| ID | Priority / evidence | Finding and impact | Proposed acceptance criterion |
| --- | --- | --- | --- |
| F01 | P1; component reproduction plus source review | Chart overlays can extend outside a selected date range. A three-candle slice beginning 2023-03-28 included a double-pattern coordinate from 2023-02-15 and breakout reference from 2023-03-02. Autoscaling can show an earlier time span despite “selected period” language. Outcome calculations were not shown to be wrong by this probe; this is a visual-window defect. | Clip overlays to the selected viewport or explicitly fix axis bounds while retaining full formation evidence separately. Test all trace/axis bounds on a narrow selection with a detected pattern. |
| F02 | P2; application probe | A completed backtest disappears after toggling Show Bollinger bands. Rendering is conditional on the run button's current rerun. This interrupts inspection and downloading. | Keep an immutable result keyed to source/replay/strategy/settings. Unrelated display changes retain it; changed calculation inputs mark it stale or rerun explicitly. Test overlay changes and downloads. |
| F03 | P2; browser on original NSE file | Readiness is fragmented: file acceptance, warm-up, short history, calendar, freshness and adjustment status are spread across top alerts and Data & exports. A new user can overinterpret a partial analysis. | One visible readiness summary with available/unavailable features, needed observations, actual cutoff, declared basis and review flags; a clear path to details. |
| F04 | P2; browser and code | Fixed “Latest 250 sessions shown” wording is inaccurate for shorter files. | Render actual plotted/total counts and the plotted date range; verify21-row and600-row files. |
| F05 | P2; expert usability judgment | Workspace navigation and the next research action are insufficiently prominent, especially when the sidebar is collapsed. | A visible task-oriented entry route and contextual links between chart, occurrence research and strategy testing; keyboard-accessible navigation. |
| F06 | P2; browser and source | A study participant sees monetary strategy assumptions beside gross event studies that ignore them. | Hide, collapse or clearly scope irrelevant controls; changing a study's cost field must never silently imply after-cost results. |
| F07 | P2; browser and source | Breakout/retest detection controls and the fixed backtest use different rule sets. A caption explains this, but users can still assume a “global” threshold changed the traded rule. | Distinct detector and strategy sections, versioned rule summaries adjacent to results, and a clear list of active parameters in each export. |
| F08 | P2; browser / judgment | Jargon and raw-field tables dominate over a compact explanation of what changed, what conflicts and what remains unavailable. | Beginner-readable summary plus optional advanced evidence. Inline definitions/deep links for RSI, ATR, RVOL, confirmation delay, baseline, MFE and signed MAE. |
| F09 | P2; browser / judgment | Historical frequency, gross movement, directional alignment and matched baseline coverage require careful interpretation across multiple sections. | Every relevant visual identifies gross/net basis, upward/directional convention, complete sample n and matched coverage; missing baseline is explained near that visual. |
| F10 | P2 before stronger performance claims; scope confirmed in code | Current backtests and outcome studies do not establish held-out economic performance. A five-trade synthetic win fraction is demonstration output, not a prediction. | Freeze hypotheses and labels, separate development/validation/test periods, handle temporal overlap and costs, and record every experiment before promoting predictive claims. |
| F11 | P2 product gap; source confirmed | There is no persistent study/history workflow. Downloading JSON preserves evidence but does not provide reopening, comparison, notes or a saved experiment registry. | Save/reopen a run, verify its data/rule identity, compare versions and retain an immutable audit. |
| F12 | P3; browser / source | Existing lessons and quiz prompts remain prominent although new assignments are paused. Some captions understate the newer descriptive event-study capability. | Keep references available, label optional labs clearly, and audit wording against implemented descriptive research versus still-unavailable calibrated probabilities. |
| F13 | P3; runtime log observation | The event date selector can emit a Streamlit warning about supplying both a default and Session State value. No crash was observed. | Use one controlled initialization/update path; rerun and replay tests produce no duplicate-state warning. |
| F14 | P3; browser / judgment | Dense charts/tables, tiny annotation text and truncated metric labels reduce readability. The synthetic status box appeared visually faint in the observed theme. | Review spacing, text hierarchy, contrast, visible labels, tab order and small screens with actual rendering; do not claim accessibility conformance without an appropriate audit. |
| F15 | P2 before public/multi-user release; not a current loopback failure | Operational readiness is unestablished: user isolation, authentication, concurrency, storage/recovery, operational monitoring and deployment controls have no acceptance evidence here. | A separately scoped deployment/readiness review with explicit data handling and operational tests before expanding beyond the current local use. |

F01–F04 are concrete behavioural or communication issues observed or reproduced in this inspection. F05–F09 and F12/F14 are reasoned usability assessments. F10/F11/F15 are missing maturity gates, not unexpected runtime defects. F13 is a runtime-maintenance observation, not a confirmed user-visible warning banner. This distinction matters when choosing what to fix.

### Detailed reproductions for the two principal behavioural defects

**F01:** use the existing original synthetic price fixture; locate its first bullish breakout, truncate analysis through that detection date, and select the last three price observations (starting2023-03-28). Construct the same `price_chart` component used by side-by-side comparison. The candlestick trace has three observations, but retained pattern traces include earlier coordinates. `quant_engine/charts.py` filters an event by its detection date and then draws its full coordinates; the selected x-axis range is not fixed. Full formation history can be valuable, but it must be an explicit view choice rather than an undisclosed expansion.

**F02:** open the default research dashboard; run the exploratory backtest; verify that Completed trades appears; toggle the unrelated Bollinger overlay. The completed-trade metric and result block disappear without an application exception. The source renders the block only inside `if st.button(...)`. This is a state-management issue, not evidence that the original backtest's financial arithmetic changed.

## 6. Is it understandable and user-friendly?

This is a single expert walkthrough acting as a researcher, not a study with recruited users. The judgments below are qualitative; no invented usability score or completion percentage is assigned.

| User | Current experience | What would help most |
| --- | --- | --- |
| Beginner learning finance | Can find strong definitions, but must understand many terms and move between workspaces to interpret a result | Data-readiness guidance, inline help and a short evidence summary tied to the uploaded file |
| Technically literate swing researcher | Can inspect daily structures, pattern states, exports and a baseline experiment | Reliable chart bounds, persistent results, better linked workflows and saved studies |
| Quantitative researcher | Can audit timing and data conventions; descriptive cohorts are a useful starting point | Dataset/event persistence, experiment registry, reproducible environment/code identity, benchmarks and temporal validation |
| Someone expecting a trading terminal | Will not find live prices, ticker retrieval, execution, watchlists or a broad strategy catalogue | Set expectations immediately; these capabilities should not be implied by branding |

### What is easy

The synthetic demonstration avoids a blank screen. Original NSE file support removes tedious preprocessing. The five workspace names broadly reflect their tasks. Basic invalid files and missing confirmations yield explicit messages. Comparison minimums and neutral-pattern behaviour explain what the user must change. Reference definitions actively correct common financial misconceptions. Exports and source passports support a user who wants to inspect how a number was obtained.

### What is hard

The first page offers several controls before explaining the user's research journey. “Insufficient” does not immediately say how to recover. A user must distinguish a geometric pattern observation from a strategy trigger, a descriptive outcome from an executable return, and a stock-context baseline from validated predictive evidence. These distinctions are technically important but should be carried by clear design, not only by lengthy captions.

Results are spread across separate tabs and workspaces rather than linked to one selected event. A researcher cannot yet click a chart event and automatically open its definition, historical cohort, strategy hypothesis and saved record. There is no meaningful persistent “my research” space. Fixed indicator parameters and one strategy constrain exploration even though the overall brief suggests a broad research engine.

### Routine interaction observations

- The 1280×720 desktop layout was inspected with the sidebar both collapsed and expanded. With it open, paired technical charts become narrow and several labels compete for space.
- Keyboard entry and Enter submission worked for concept search. This is limited keyboard evidence, not a full keyboard/screen-reader accessibility pass.
- A phone-width 390×844 override was attempted, but the browser still reported1280×720. The override was reset. **No valid mobile rendering result was obtained**, and the desktop screenshot initially associated with that attempt is not mobile evidence.
- Form-based event-study settings apply on submission, as stated by the page. This protects a clear study definition but benefits from an obvious active-definition summary.
- Label and account-capital values survived the tested same-session Research → Compare → Research round trip. Do not generalize the backtest-result defect into a claim that all navigation state is lost.
- Fresh-session recovery, user accounts, actual mobile devices, screen readers and multiple browsers were not comprehensively exercised.

## 7. Financial and research integrity

### Existing safeguards worth retaining

The application differentiates formation and knowability, freezes breakout references, uses delayed confirmed pivots and has future-append/replay regression coverage. Input validation rejects misleading numerical data instead of filling it silently. Indicator warm-up and undefined quantities remain unavailable. The engine can say no trade. Study horizons beyond the data cutoff remain incomplete rather than becoming losses or artificial early closes.

Two-stock return pairing respects both interval endpoints. Same-stock study baselines disclose shared controls and matching coverage. The event-study summary compares matched event means against baseline means covering the same events. Directional bearish outcomes are distinguished from short-trade returns. Known raw corporate-action crossings can be excluded, and action-audited execution remains restricted where share accounting is not implemented.

The baseline simulator handles costs, cash/risk/volume caps, next-open entry, adverse gaps and ambiguous daily-bar exits using an explicit stop-first convention. A cost-sensitivity probe retained five synthetic trades but changed gross-zero-cost return from approximately+1.47% to −1.27% with deliberately high 1%-per-side fees and1%-per-side slippage. This is an invented-fixture software test, not an estimate of actual Indian trading charges or market performance.

### What these safeguards do not establish

- A pattern detector's geometric confirmation is not a validated profitable trigger.
- A high RSI, stronger MACD or more indicator agreement is not a calibrated success probability.
- Historical positive fractions and box plots are descriptive statistics; the current research does not supply dependence-aware confidence intervals or a causal identification design.
- Single-stock cohorts and shared market episodes do not create a point-in-time cross-sectional universe. Survivorship and selection questions remain.
- The backtest's same-dataset outcome is not independent evaluation. Its gross buy-and-hold comparison has different exposure/cost conventions and is labelled accordingly; it is not yet a full fair-benchmark framework.
- Daily OHLC cannot identify intrabar order sequence or actual liquidity. The simulator's explicit conventions do not turn those assumptions into observed fills.
- Manual price-basis/source declarations do not authenticate vendors or guarantee complete corporate-action reconciliation. Price returns are not dividend-inclusive total returns.
- An offline2026 calendar cannot be assumed to cover other years or every later amendment. A historical file can intentionally be stale; freshness should be visible without automatically forbidding historical research.

The current restraint around probabilities is appropriate. The next research work should improve evidence and usability before adding impressive-looking scores.

## 8. Engineering and operational assessment

### Architecture

`app.py` coordinates navigation, input, replay and the main dashboard. `quant_engine/data.py` and the NSE adapters validate/normalize files. `datasets.py`, `calendar.py` and `corporate_actions.py` handle source declarations, bounded quality checks and reviewed action research. `indicators.py`, `patterns.py`, `research.py` and `analysis.py` produce analytical observations. `charts.py` renders shared visualizations. `strategy.py` defines the baseline simulation. `event_study.py` and `comparison.py` perform independent numerical research, with separate UI modules. `learning/` supplies shared reference and roadmap content.

This separation is practical and understandable. Core numerical modules can be tested without browser interaction. Reusing a single chart component also means its window defect can affect several views, so boundary tests belong at the shared component and user-workflow levels.

### Evidence quality

The existing test suite covers meaningful numerical and chronological cases, not merely whether pages render. All 240 tests passed during this inspection. They include indicator fixtures, invalid inputs, pivots/events, backtest assumptions, calendar/action behaviour, comparisons and event studies. The two new behavioural findings show why workflow/state and visual-boundary cases need to supplement those tests. The number of passing tests is not a percentage of correctness, a security certification or a performance-validation result.

The local 70-file snapshot matched the private repository at commit `6a64fed3f28fa397ed889417eb84fa73d911eb9f`. The original source release's remote run passed 240 tests; that is historical remote evidence, while99.08 seconds is this inspection's new local run. Publishing this report creates a later documentation commit; it does not change the tested analytical source.

### Performance and scale

A separate uncached computational probe used5,000 repeated synthetic bars. Analysis took 9.852 seconds and the event study7.780 seconds on this local environment. It produced 2,289 source transitions and 908 included occurrences. These are one-run measurements on artificial data, excluding browser rendering/network and not representing a concurrency, maximum-file-size or scalability guarantee.

The declared input limits are20 MB and50,000 daily observations. The full 50,000-row UI workflow was not benchmarked. Eager tab rendering, large event/JSON tables, a shared Streamlit process and long analyses deserve profiling before scale claims. Changing every parameter should not unnecessarily recompute unrelated research or discard completed work.

### Security, privacy and deployment boundaries

The application currently binds to127.0.0.1, disables Streamlit usage statistics and uses a private repository. The source publication allow-list excludes runtime outputs and uploaded datasets. No configured live data/broker/LLM connection or live-order workflow was found in the inspected implementation. No paid service or public deployment was added by this inspection.

This was not penetration testing. Authentication, multi-user isolation, dependency vulnerabilities, malicious workbook/ZIP handling, cache isolation under multiple users, rate limits, backups and incident recovery were not certified. They need their own evidence before changing the product's local operating model. GitHub source publication and the Streamlit Deploy button do not mean the site has been deployed for others.

## 9. Progress against the original plan

The current original-plan mapping has **43 bullets:8 Done,20 Partial,15 Planned**. The expanded implementation/learning checklist has **351 items:43 Done,45 Partial,251 Planned,12 Optional**. These are different inventories, not competing completion percentages. A small finished task and a large research stage have different effort and value. No complete original phase is claimed.

| Original phase | Current position | What remains central |
| --- | --- | --- |
| 1. Core technical analysis | Usable limited daily engine | Full catalogue, configurable/contextual methods, broader data/timeframe reliability |
| 2. Visual analysis/dashboard | Interactive charts, observations and exports work | Chart-bound correctness, trendlines, screenshot mode, linked/editable annotations and richer interaction |
| 3. Strategy generation | One coherent conditional long-breakout experiment plus risk math | Breakout-retest and other strategies, versioned orders/exits, multi-timeframe confirmation and comparison |
| 4. Quantitative research/ML | Descriptive outcome research is now usable | Database, fixed labels, universe/benchmarks, uncertainty, temporal validation, models and calibration |
| 5. Advanced integration | Deterministic reports, reference/build workspaces and private source workflow | AI narration, saved research/history, licensed automatic feeds, paper tracking, monitoring and deployment readiness |

### Development history in context

| Milestone | What it added |
| --- | --- |
| Initial prototype and learning foundation | Daily analysis, chart/report, one simulator, reference library and reproducible software workflow |
| Data-foundation increments | Passports, offline report preview, native NSE history compatibility, bounded calendar audit and manual split/bonus research |
| 4 November analytical increment | Breakout/retest lifecycle, triangles/rectangle, contextual candles, momentum/divergence and two-stock comparison |
| 5–6 November research increment | After the pattern, outcome/baseline/overlap/censoring logic, occurrence inspection and portable records;240-test source release |
| 15 November inspection | Fresh user/workflow review,240-test regression, source-match verification, behavioural issues and prioritized improvement gates; no analytical implementation changes |

### Original initial-acceptance criteria

| Criterion | Audit interpretation |
| --- | --- |
| 1. Valid CSV upload | Demonstrated, including unchanged original NSE export |
| 2. Correct validation/preprocessing | Strong bounded support; not independent source/completeness authentication |
| 3. Candlestick construction | Demonstrated |
| 4. Principal indicators | Starter set implemented; complete requested catalogue not finished |
| 5. HH/HL/LH/LL | Implemented with explicit confirmation delay |
| 6. Support/resistance zones | Implemented approximate clustering, broader level system partial |
| 7. Initial candle patterns | Supported subset implemented; full intended catalogue partial |
| 8. Double patterns, triangles and head-and-shoulders | Partial: the first two groups exist; head-and-shoulders does not |
| 9. Coordinates and detection status | Supported geometric families have evidence; universal event schema/catalogue remains incomplete |
| 10. Multiple timeframes | Partial: daily and conservative prior-week context, not the requested general workflow |
| 11. Coherent technical report | Deterministic starter report exists; consolidated researcher experience needs improvement |
| 12. Opportunity/entry/stop/target explanation | One baseline demonstrated; broader strategy catalogue pending |
| 13. Risk/reward arithmetic | Supported baseline tested; wider instrument/cost assumptions remain scoped |
| 14. Annotations correspond to data | Data-based annotations exist; F01 adds a visual-window correctness gate |
| 15. Insufficient/unreliable-data messaging | Present, but discovery and feature-specific recovery need improvement |
| 16. No future information in testing | Targeted causality/replay coverage passes; not blanket proof for all future modules or predictive validation |
| 17. Documented local run | Relaunched successfully here; fresh-machine installation not repeated in this inspection |
| 18. Automated analytical/financial tests |240 existing tests pass; newly reproduced workflow issues need additional tests when repaired |

## 10. Recommended work order and measurable gates

The following is a recommendation from this inspection, not a claim that any new feature has been implemented.

| Order | Milestone | Why it matters / completion gate |
| --- | --- | --- |
| 1 | Repair chart bounds and retain completed results | Narrow periods remain honest on every trace/axis. Unrelated display changes retain a completed backtest; changed calculation inputs are visibly stale. Add regression reproductions forF01/F02. |
| 2 | Make research readiness and navigation clear | A new user can upload, identify basis/cutoff/history limits, explain what is available and reach the next task without reading source files. Test the21-row NSE workflow and a zero-event slice. |
| 3 | Add the dedicated breakout-retest strategy | Version exact triggers, next eligible action, cancellation, invalidation, stops, targets, expiry, costs and no-trade reasons. Keep event observations separate from the strategy specification. Verify gaps and ambiguous bars in the simulator. |
| 4 | Compare strategies fairly | Same declared dataset/evaluation protocol and cost/exposure assumptions; comparable ledgers and benchmarks; disclose all attempted parameter choices. |
| 5 | Save/reopen immutable research records | Store dataset identity, code/rule versions, chosen hypotheses and results; reopen/reproduce and compare runs; preserve notes and provenance. |
| 6 | Establish research validation | Define targets/horizons and ambiguity, chronological splits/purging, dependence-aware uncertainty, robustness and experiment accounting. Evaluate beyond the sample used to choose rules. |
| 7 | Expand evidence-backed analytical capability | Add remaining patterns/indicators and real multi-timeframe context one bounded family at a time, with positive/negative/timing tests and explanations. Broaden calendar/data coverage where it blocks the chosen work. |
| 8 | Add prospective paper tracking | Record a setup before outcomes exist, then track pending/triggered/expired/exited states with execution assumptions and review. |
| 9 | Introduce optional AI/ML and integrations | Use validated structured evidence; compare simple models and calibrate probabilities; supply deterministic narration fallback. Add licensed feeds and deployment controls under explicit scope. |

### A useful next-release definition

A researcher uploads a stock, immediately understands data readiness, selects an occurrence on a correctly bounded chart, opens its historical cohort, preserves that study, tests one exact breakout-retest strategy and can explain the result and its limitations in plain language. This is a more actionable next product target than “finish all 351 tasks.”

Longer-term completion means the entire research chain is inspectable, reproducible and independently evaluated. It does not mean every pattern is profitable, an AI must make a recommendation or live trading must be enabled.

## 11. Inspection coverage and limits

### Check matrix

| ID | Method | Check | Observed result |
| --- | --- | --- | --- |
| T01 | Browser | Default dashboard and navigation | Opens; synthetic status visible; sidebar initially collapsed in this session |
| T02 | Browser | Baseline backtest | Runs; five synthetic completed trades; ledger/metrics/export controls appear |
| T03 | Application probe | Unrelated overlay after backtest | Result disappears;F02 reproduced |
| T04 | Browser | Pattern/candlestick panels | Supported-family/context explanations and evidence controls present |
| T05 | Browser | Original NSE upload, unchanged | Accepted;21 observations normalized and sorted |
| T06 | Browser | Completed-session confirmation | Analysis blocked until checked |
| T07 | Browser/component | Short-history interpretation | RSI available, EMA50 unavailable; insufficiency and short-history messages present |
| T08 | Browser | Data-quality/freshness discovery | Bounded calendar and eight-session lag disclosed under Data & exports |
| T09 | Component | Standard CSV/XLSX parity |600-row numerical frames identical |
| T10 | Component | Duplicate dates | Rejected with specific message |
| T11 | Component | Invalid OHLC | Rejected with offending date |
| T12 | Component | Negative volume | Rejected |
| T13 | Component | Missing close/nonfinite values | Rejected |
| T14 | Component | Ambiguous standard CSV dates | Rejected with YYYY-MM-DD guidance |
| T15 | Browser/application | Synthetic comparison |150 common dates,149 matching intervals; coefficient rounded 0.682 |
| T16 | Application probe | One-date comparison | Explicit minimum-two-common-dates error; no crash |
| T17 | Component/source | Selected chart bounds with active patterns | Older annotation coordinates retained;F01 reproduced |
| T18 | Browser | Event-study defaults |21 included,6 overlap exclusions,19 complete at20 observations |
| T19 | Application probe | Empty event horizon selection | Clear warning; no crash |
| T20 | Application probe | Neutral Doji in directional mode | Zero included with explanation |
| T21 | Application probe | Switch neutral Doji to upward-price mode | Valid21-occurrence study; no exception |
| T22 | Browser | Individual event inspection | Formation/knowledge/reference and percentage excursions visible |
| T23 | Browser/download parse | Study JSON |84 outcomes,536 controls,24 summary rows; incomplete returns null |
| T24 | Browser/download parse | Comparison JSON |Readable object with comparison, labels and source passports |
| T25 | Browser | RSI search and keyboard submission |17 related entries; correct worked/reference content displayed |
| T26 | Browser | Build journal |351-task and original-plan views present; assignments-paused note visible |
| T27 | Application probe | Same-session navigation context | Label and250,000 capital preserved through Research → Compare → Research |
| T28 | Application probe | Synthetic UDiFF walkthrough | Loads and offers report-derived instrument selection; real-report gate remains separate |
| T29 | Component | Fee/slippage sensitivity | Expected direction of net-result change on synthetic fixture |
| T30 | Full regression | Existing240 cases |All passed in 99.08 seconds |
| T31 | Local/connector | Source provenance |All 70 audited files match published commit |
| T32 | Computational probe |5,000 synthetic observations |Analysis9.852s; study7.780s; no exception; not a load test |
| T33 | Browser | Phone-width attempt |Actual viewport remained1280×720; mobile result unavailable; override reset |

### Limits that must accompany this report

There was no live trading, financial recommendation, production deployment, account-access change or new data-source integration. No uploaded market dataset was redistributed. No formal accessibility certification, penetration test, multi-user stress test, fresh-machine installation, actual mobile-device test, complete50,000-row UI benchmark or empirical investment-validation study was performed. Passing paths reflect the tested examples and source snapshot, not an exhaustive guarantee.

Browser observations were allowed to settle before conclusions where Streamlit initially returned an earlier rendering. An early probe selected a number input by positional index; it was corrected to the account-capital label before the navigation finding was retained. The initial last-ten-demo-date chart probe did not trigger an out-of-range annotation; a second deliberately pattern-containing narrow window reproducedF01. These are test-design corrections, not additional application defects.

## 12. Evidence, reproducibility and continuation context

**Audited source commit:** `6a64fed3f28fa397ed889417eb84fa73d911eb9f` in the private [Signal Ledger repository](https://github.com/aryankjain11/signal-ledger). **Audited source inventory:**70 files. **Sorted source-manifest SHA256:** `3530e58f620796f6219cf3fc2f458f99eafb9dae876f5de07f3dec598dae8f8a` (manifest serialization generated by the inspection probe). **Runtime:** Python 3.13.7; Streamlit 1.66.1; pandas 2.3.2; NumPy 2.3.3; Plotly 6.9.0; pytest 9.2.0. These identify the inspected environment, not recommendations to upgrade packages.

Local runtime evidence is under `outputs/audit-2026-11-15/`: source manifest, probe script/results, computational timing and screenshots. Runtime artifacts are excluded from the publication allow-list. Screenshots used for the shareable report show synthetic observations or reference pages; the real uploaded CSV is not bundled. The readable HTML companion embeds selected synthetic screenshots; this Markdown report is the durable, easily searchable source.

Primary project records: [original brief](ORIGINAL_BRIEF.md), [refined build plan](BUILD_PLAN.md), [current original-plan status](PROJECT_STATUS.md), [master checklist](MASTER_CHECKLIST.md), [concept handbook](EDUCATION_AND_CONCEPTS.md), [event-study specification](EVENT_STUDIES.md), [analytical/comparison specification](ANALYSIS_AND_COMPARISON.md), [work log](WORK_LOG.md), and [GitHub verification record](GITHUB_SYNC.md).

Source paths relevant to the principal findings: `quant_engine/charts.py: price_chart`; `quant_engine/comparison_ui.py: side-by-side shown.frame slicing`; `app.py: conditional backtest rendering and fixed250-observation caption`; `quant_engine/event_study_ui.py: shared controls, study_period initialization and result explanations`; `learning/pages.py: reference and retained lesson presentation`.

The accompanying [platform continuation brief](PLATFORM_CONTEXT.md) is a compact handoff for any future human or AI collaborator. Read it with this inspection and the current source; do not assume planned capabilities exist merely because they have a reference definition or checklist entry.
