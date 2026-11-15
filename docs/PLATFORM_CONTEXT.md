# Signal Ledger · platform context and continuation brief

Last reviewed: **2026-11-15, Asia/Calcutta**. This is a handoff, not a declaration that the full project is complete. Read [the detailed inspection](PLATFORM_INSPECTION_2026-11-15.md), then verify current source and records before changing implementation.

## Product identity and purpose

Signal Ledger is intended to become an interpretable quantitative technical-analysis and strategy-research platform. Its central promise is to connect data, observable structure, historical evidence, exact conditional strategies, risk and clear explanations. The original brief calls it an AI-powered engine, but the current software is deterministic and does not have a connected LLM or trained model.

The initial user is an individual researching Indian-stock swing setups from completed daily INR observations. Useful research and conceptual understanding matter together. The owner explicitly paused new exercises/assignments; reference definitions and existing lessons remain available. Feature development has priority over extra format adapters and automated action downloads unless those are necessary for a chosen feature or an actual reliability defect.

## Current operating state

- Local Python/Streamlit application, loopback address `http://127.0.0.1:8501/`.
- Workspace folder: `C:/Users/aryan/OneDrive/Documents/ChatGPT/Projects to Build/quant-research-engine`.
- Private source repository: [aryankjain11/signal-ledger](https://github.com/aryankjain11/signal-ledger).
- Audited pre-report commit: `6a64fed3f28fa397ed889417eb84fa73d911eb9f`; all 70 source files matched that snapshot during the inspection. A later documentation commit adds this brief/report.
- Current implementation status: useful exploratory research prototype, not a finished trading terminal or empirically validated prediction service.
- Five workspaces: Research dashboard; After the pattern; Compare two stocks; Education and Concepts; Build checklist & log.
- No public hosting, automatic ticker retrieval, live market feed, saved research database or live order integration is implemented.

## What exists

1. Standard daily CSV/XLSX and unchanged native NSE security-history normalization. EQ daily UDiFF CSV/ZIP import is a separate preview, not the same acceptance gate.
2. Strict OHLCV/date validation, source/visible hashes, passports, replay cutoff and bounded offline NSE CM 2026 quality/freshness assessment.
3. Manual reviewed split/bonus ledger, optional normalized research view and execution restrictions where share accounting is unavailable. No dividend-inclusive total returns.
4. Starter fixed indicators; confirmed swings/HH-HL-LH-LL; approximate clustered levels; limited chart/candle families; breakout/retest lifecycle; momentum and delayed confirmed-pivot divergences.
5. Interactive charts, deterministic report/evidence exports and two long strategy simulators: the fixed breakout baseline plus versioned breakout-retest execution. Both declare sizing/cost/gap/exit assumptions; the retest strategy adds frozen structural risk, one next-open attempt and a complete setup/cancellation audit. Its controls are independent from descriptive chart rules.
6. Versioned descriptive event studies: knowledge-time references, forward movements, MFE/signed MAE, per-horizon censoring, overlap spacing, retrospective same-stock context baselines, sample/coverage counts, occurrence charts and portable records.
7. Two-stock common-date indexed performance/drawdown/relative ratio, matched native-interval Pearson/Spearman/rolling correlation, side-by-side analysis and evidence downloads.
8. Shared131-concept reference library and357-item roadmap with durable build records and a passing automated regression workflow.
9. Bounded chart geometry, actual displayed counts, visible data readiness/recovery, task/concept links and one immutable baseline session snapshot with stale-input warnings and original-run downloads. This is not durable save/reopen history. Exact rules are in `RESEARCH_RELIABILITY.md`.
10. Independent immutable retest-strategy session record, saved-price setup inspection, explicit pending/cutoff state, forced-liquidation labels and JSON/CSV decisions/transitions/trade exports. Exact rules and evidence are in `BREAKOUT_RETEST_STRATEGY.md`. Strategy selection and retest controls survive tested strategy/upload/reference routes; this is not full durable workspace storage.

## What does not exist

The remaining pattern/indicator catalogue; general intraday/monthly analysis; completed multi-timeframe strategy confirmation; pullback/reversal and short execution strategies; fair strategy-comparison framework; persisted pattern/outcome/history database; target-before-stop event-study labels; dependent-data statistical inference; experiment registry; held-out/walk-forward validation; calibrated probabilities; trained ML models; evidence-bound LLM narration; screenshot ingestion/interpretation; automatic licensed feeds; prospective paper ledger; production accounts/isolation/monitoring. A strategy's simulated stop/target exits do not complete the broader event-label/database layer. Do not imply missing capabilities exist from a glossary entry, mathematical name, roadmap item or local chart.

## Research conventions to preserve

- Completed daily observations are session-date claims; do not invent missing prices or upsample into fictitious intraday bars.
- Formation and first-knowable detection times differ. Preserve delayed pivot confirmation and event-prefix causality.
- Event states are immutable observations. A later failure must not remove an earlier breakout from historical research.
- A geometric observation is distinct from a strategy signal, a simulated trade and a calibrated probability.
- Event-study default reference is next observed open after detection, ending horizon h at close[t+h]. Incomplete horizons stay null, not failed trades or artificial end-of-file exits.
- Bearish direction alignment negates price movement; it does not simulate executable short selling.
- Baseline pools are retrospective same-stock context comparisons with shared controls. They are not causal alpha or a market-model abnormal return.
- Match both native interval endpoints for cross-stock returns; no forward-filled pairs.
- Backtests remain exploratory same-dataset simulations until a separate validation protocol passes. Never invent success probabilities or performance evidence.
- Do not override action-audited execution restrictions with an observational study.

## Inspection findings and immediate priorities

**F01, repaired:** chart geometry is clipped to visible observations, actual anchors remain distinct from interpolated drawing vertices, all date axes are bounded, and original event evidence is unchanged. Regression includes an older pattern crossing a narrow three-observation window.

**F02, repaired:** one immutable result survives display/navigation reruns. Original assumptions/exports stay attached to it; changed calculation inputs mark it stale. A rerun replaces the session record. No durable history database exists. The initial audit's positional checkbox probe was mislabeled; a later correctly labelled reproduction against the pre-change published app confirmed the defect before acceptance of the fix.

**F03/F04, bounded scope complete:** readiness and actual plotted counts appear near the main result. The original NSE example still has21 bars and partial readiness despite valid ingestion; EMA50 recovery is29 observations. Full source authenticity/provider verification remains outside this gate.

**F05–F07, partially addressed:** task pills, direct reference articles, observation-to-cohort/baseline links and explicit monetary/detector-versus-strategy scope are implemented. Universal term help and broader polish remain. **F08–F09:** further gross/directional/sample-coverage presentation improvements remain planned.

The event date selector now supplies a default only when there is no session value; repeated navigation checks pass. Optional learning prompts and some historical wording still need presentation review; dense charts/tables need accessibility and actual small-screen evaluation. No valid phone-width test was obtained because the browser continued to report1280×720 after the attempted override. Do not claim mobile QA passed.

The inspection's narrow state probe was not proof of every route. Follow-up browser checks exposed sidebar resets after visiting Education. Research sidebar widgets are now rendered on every workspace and retained, including the uploaded file and baseline assumptions. Replay and non-sidebar rule/action controls are not a complete durable workspace-state implementation; database/reopen acceptance remains planned.

## Recommended implementation sequence

1. Completed bounded reliability gate: F01/F02, readiness/counts and selected task/reference links; preserve their regression tests.
2. Completed first versioned long breakout-retest strategy: frozen prior range/ATR, close-confirmed later retest, one next-open attempt, structural stop, target, expiry, gap/cost/capacity cancellations and saved audit/inspection. Preserve its chronology tests and boundary disclosures.
3. Add fair comparison of that strategy and the existing baseline under a declared evaluation protocol.
4. Save/reopen immutable datasets, runs and experiment definitions.
5. Define labels and chronological/overlap/uncertainty/benchmark validation before predictive claims.
6. Expand pattern/indicator/timeframe families one bounded feature at a time; add prospective paper tracking.
7. Add optional AI/ML, licensed integrations and operational expansion only after their evidence and scope gates.

This is the inspection's recommendation. Unimplemented items remain planned until tested and documented.

## Evidence and status counts

Fresh inspection regression: **240 tests passed in 99.08 seconds** on Python 3.13.7. Historical event-study source CI: run 42098482104,240 passed in 15.74 seconds. Those are different runs. Supplemental probes recorded11 scenarios/groups, including uploads, invalid inputs, chart bounds, state, comparisons, neutral studies and report preview. A 5,000-bar artificial computational probe took 9.852s analysis and 7.780s study, excluding UI/rendering; it is not a scalability guarantee.

Follow-up local regression after reliability source changes: **268 passed in53.80s**, adding28 cases. Browser checks included unchanged21-row NSE data,600-row synthetic data, retained upload/assumptions, stale saved costs, RSI shortcut, keyboard observation selection, prefiltered cohort and baseline-tab route. Publication and actual remote CI observations are recorded separately in `GITHUB_SYNC.md`.

Latest strategy acceptance: **323 passed in84.15s**, adding55 retest cases to268 existing tests; final target-marker presentation check1 passed in4.35s. Browser verified synthetic trades/cancellations, unchanged21-row NSE no-trade behavior, concept/selection retention, stale rules and a real600-bar/5-setup/4-trade JSON download. Original baseline engine remains unchanged. These are software checks, not evidence of economic advantage.

Original43-bullet mapping:8 Done,20 Partial,15 Planned. Expanded357-task mapping:50 Done,48 Partial,247 Planned,12 Optional. No complete original phase is claimed; counts are not effort-weighted completion percentages. Strategies/descriptive research are usable while fair comparison and database/model/validation layers remain missing.

## Working agreement and file map

Read `AGENTS.md` first. Numerical code is in `quant_engine/`; UI coordination is `app.py`; shared reference/status sources are `learning/concepts.py`, `learning/roadmap.py` and `learning/progress.py`. Generated handbook/checklists come from `scripts/export_learning_docs.py`. Reuse the existing source repository and append meaningful batches to `docs/WORK_LOG.md`; keep `docs/BUILD_REPORT.md` current. Keep prior dated evidence distinct from new checks.

Publish reviewed source, tests, synthetic fixtures and documentation only. Exclude environments, credentials, private uploads, licensed datasets and runtime outputs. Repository visibility must stay private. GitHub upload is complete only after branch/files are verified. Preserve local user changes; do not force-update a changed remote head. Live orders, new paid services and changing the publication audience are outside current scope.

The inspection added reports/records only. The later reliability increment repairsF01/F02 and adds four bounded software gates. It implements no new strategy and does not certify accessibility, security or investment performance.
