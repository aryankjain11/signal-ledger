# Feature priorities after the data-foundation increments

Usability update ·2026-11-16: the requested workflow audit adds session-retained
files/dates/settings, explicit recovery, exact-input confirmation and clearer
controls/reference/outcome presentation. See `USABILITY_REVIEW_2026-11-16.md`.
It changes no numerical engine and does not replace the next feature below:
**fair strategy comparison**, then independent validation and durable research.

Strategy update ·2026-11-15: **Breakout-retest v1 is implemented and accepted**
as a separate long next-open strategy with frozen structural stop, cost-aware
sizing, gap/cancellation/expiry rules, setup audit, saved-price charts and records.
Full local regression:323 passed in84.15s. See `BREAKOUT_RETEST_STRATEGY.md`.
**Next feature: fair strategy comparison**, with identical relevant data/costs,
declared execution/coverage conventions and frozen evaluation definitions. It must
not claim an advantage from unlike samples or repeated filter selection. Independent
chronological validation and durable research storage remain subsequent gates.
The earlier recommendations below are retained as design history.

Reliability update ·2026-11-15: selected-period chart bounds, immutable baseline
session retention/staleness, visible readiness/actual counts and task/reference
links are implemented and accepted. Full local regression:268 passed in53.80s.
See `RESEARCH_RELIABILITY.md` for exact scope and limits; the dated inspection is
historical. That increment recommended the dedicated breakout-retest strategy;
the strategy update above now supersedes that next-step recommendation. Durable saved history,
broader accessibility and other inspection findings remain open.

Status: continuing feature priorities, with bounded implementation updates. Updated 2026-11-15.

2026-11-04 implementation update: the initial breakout/retest detector, triangle/
rectangle and contextual candle families, momentum/divergence panels and two-stock
comparison are now implemented. `ANALYSIS_AND_COMPARISON.md` defines the actual
scope. The strategy comparison follow-up remains planned;
the original prioritization narrative is preserved as the design rationale.

2026-11-05 implementation update: **After the pattern** now supplies a bounded
single-stock descriptive event study: known-time next-open/close references,
per-horizon returns/excursions, context-matched non-event baselines, comparable
coverage, overlap spacing, censoring, individual charts and portable audit records.
`EVENT_STUDIES.md` defines actual rules. It does not complete the broader database,
target/stop labeling, dependence-aware inference or held-out validation scope below.
Next highest-value feature: a versioned breakout-retest strategy with exact order,
stop, target, expiry and cost assumptions, followed by fair strategy comparison.

The owner asked to prioritize useful product features and conceptual learning,
rather than more file adapters. Existing daily/NSE uploads and the current research
engine are sufficient to begin an analytical feature increment. Known adjustment,
calendar and execution limits remain disclosed; unfinished data tasks stay on the
checklist without blocking every unrelated feature. Exercises remain paused.

## Planned analytical/product features

| Area | Planned scope | Current baseline |
| --- | --- | --- |
| Market structure | Trend strength/ranges, breakouts, breakdowns, retests, false breakouts, causal trendlines/channels | Fixed confirmed swings, basic HH/HL/LH/LL and pivot-cluster zones |
| Chart patterns | Triangles, flags, wedges, head-and-shoulders, cup-and-handle and broader lifecycle/context | Double-top/bottom geometric prototype |
| Candles | Hammer/shooting star, Morning/Evening Star and other families with trend/level context | Doji and engulfing geometry |
| Indicator interpretation | ADX, Supertrend, Donchian/squeeze states, stochastic measures and price/indicator divergence | Starter averages, RSI/MACD/ATR/Bollinger/OBV/RVOL |
| Multiple timeframes | Daily/weekly/monthly alignment, conflicts and completed-period availability | Daily plus conservative prior-week context |
| Strategy lab | Breakout-retest, pullbacks and structure-based reversals; alternative stops/targets and comparison | One explicit long breakout experiment |
| Historical research | Versioned event cohorts, target/stop/horizon outcomes, MFE/MAE, uncertainty and comparisons | Exploratory baseline backtest; no pattern-performance database |
| Research workflow | Saved analyses, comparisons and prospective paper tracking | Local replay and downloadable reports/evidence |
| Later AI/integration | Evidence-bound narration, screenshot analysis, calibrated models and data APIs | Deterministic explanations; no model probabilities or API feed |

These are existing roadmap themes, not new completion claims. Full mapping is in
PROJECT_STATUS.md and detailed tasks in MASTER_CHECKLIST.md.

## Recommended next increment: breakout/retest lifecycle

Connect market structure to one conditional strategy through observable states:
range/level → breakout → retest holding or failure → invalidation/expiry. Begin
with the long swing-research path; downward breaks can be observations without
introducing an unsupported overnight short-execution model.

User-facing result:

- Plot the pre-existing reference level, breakout candle and subsequent retest.
- Show Developing / Breakout / Retest / Failed / Invalidated / Expired state
  with exact formation and knowability times and configurable versioned rules.
- Explain the actual price/volume/volatility conditions that passed or failed.
- Preserve historical replay: a level or event cannot depend on future bars.
- Add one explicit breakout-retest plan with trigger, invalidation, expiry and
  declared stop/target assumptions; retain no-trade outcomes.
- Compare that rule with the existing breakout baseline under the same relevant
  costs and chronological execution conventions. No performance advantage is assumed.

Relevant existing scope: S03 breakout confirmation/failure/retest and evidence,
S08 breakout-retest/specifications, S09 structural risk rules, S10 evaluation.
Implement in small usable slices; an event detector alone does not complete the
strategy/backtesting/research layers.

Why prioritize it: it adds a visible and inspectable capability, reuses existing
data/indicators/chart/simulator work, and connects structure, confirmation delay,
false breakouts, order timing, risk and costs in one workflow. More indicator names
alone do not establish an independent contribution or a predictive edge.

## Recommended follow-up: an event-study research view

For one frozen event/rule definition, record occurrences and outcome windows.
Display event counts, target/stop/expiry/censored outcomes, MFE/MAE and returns
with stated costs/assumptions. Use a comparable baseline, chronological validation,
overlap handling and small-sample warnings. Historical frequency is not a calibrated
forecast. This advances S10/S11 and builds prerequisites for later S12 models.

Next candidates after the first end-to-end workflow: daily/weekly agreement and
conflict analysis; RSI/MACD divergence; one context-aware reversal/candle family.
Pattern and indicator additions should have a testable role rather than simply
increasing the size of a catalogue.

## Deferred unless needed

Native corporate-action-download parsing, further upload formats, automatic feeds,
wider calendar coverage and operational storage expansions stay planned. Correct
actual defects and respect known input/adjustment limits when a selected feature
requires them. This prioritization is not permission for live orders, unlicensed
data redistribution or displaying unsupported probabilities.
