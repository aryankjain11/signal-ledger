# Proposed next milestone · fair comparison of the two long strategies

Prepared16 November2026 for continuation. **Specification proposal, not implemented
functionality.** The owner has not requested implementation during this handoff.
The next assistant should adopt/refine a bounded protocol, state its acceptance
gate, then implement it when continuing the build. Preserve existing engines.

## Problem and user benefit

The site can simulate a fixed breakout baseline and a separate breakout-retest
strategy. Users can switch between them, but there is no saved, declared common
comparison tying data, execution assumptions, coverage and both results together.
Comparing two screenshots or highest returns after changing filters would be weak
research. The existing **Compare two stocks** page solves a different problem.

The next feature should answer: **On this declared dataset and evaluation window,
under these recorded assumptions, how do the two frozen hypotheses differ in
trades, exposure, risk, results and skipped/cancelled opportunities?** It must also
answer when there is too little data or too few trades to learn anything useful.

It must not answer which strategy is generally best, claim significance, tune
parameters automatically or imply that retests improve performance without evidence.

## Non-negotiable existing contracts

- Baseline version`long-breakout/1` in `strategy.py` remains unchanged.
- Retest version`long-breakout-retest/1` in `retest_strategy.py` remains unchanged.
  In particular, do not insert its later-retest/structural-stop logic into baseline.
- Descriptive `ResearchRules` are distinct from both executable hypotheses.
- Future information cannot alter a historical signal, entry or natural transition.
  Preserve formation/knowledge dates, causal warm-up and next-open decisions.
- Cost/risk/cash/prior-volume, ambiguity, gap, action restrictions and artificial
  cutoff conventions must be visible and obeyed. Do not silently normalize away
  differences in the strategies' eligible timing.
- A comparison must hold immutable copies/identities of **both** outputs and their
  actual inputs. Never combine one stale saved run with a newer run without saying
  so; preferably compute a new coherent pair for the declared protocol.

## Suggested first release boundary

One uploaded/synthetic stock, one declared time window, two frozen strategy
versions and one common account/execution configuration. No multi-stock portfolio,
parameter optimizer, hypothesis search, ML, LLM dependency or database prerequisite.
Use the app's existing file/passport/replay readiness workflow.

Make an explicit protocol object before implementation. Recommended recorded fields:

| Field group | Required content |
| --- | --- |
| Identity | Comparison schema/protocol version, source hash, canonical analyzed-data/visible hashes, symbol, basis and action policy |
| Time | Uploaded history bounds, replay cutoff, evaluation start/end and actual observation counts |
| Rules | Exact baseline version/used settings and full retest version/rules; no unused settings masquerading as calculation inputs |
| Execution | Initial capital, risk fraction, charges/slippage, participation, share/cash/capacity conventions and cutoff policy |
| Coverage | Indicator readiness, warm-up region, natural candidates/signals, trade count, no-trade/cancellation/pending counts available from each engine |
| Outputs | Both equity curves, trade ledgers, metrics and relevant retest audit/current state, with common-window alignment rules |
| Provenance | Created timestamp, source passports, protocol identity, engine/rule versions, explicit research/validation status |

### Resolve warm-up and evaluation timing deliberately

A naive slice at evaluation start can reset EMA/ATR and change signals; feeding
earlier bars directly to a cash simulator can let pre-window positions leak into
the result. Pick and document a policy rather than hiding this choice.

A bounded initial implementation could **limit the evaluation start to the first
uploaded bar**, use the same full replay slice for both engines, report each
strategy's causal warm-up coverage and show the actual start of tradable context.
This avoids pretending that arbitrary independent evaluation starts already work.
If implementing a later evaluation start, pre-start bars may initialize causal
features but must not create carried positions/trades or equity gains before the
declared initial cash start. This requires separate tests and an explicit interface;
do not modify the frozen versions silently to achieve it.

Keep the global replay cutoff authoritative. Never use the later source tail for
an earlier evaluation window. Do not count an incomplete pending retest as a loss.

### Common assumptions versus genuine differences

Hold shared data, start cash, cost/slippage, risk and participation assumptions
constant. Report strategy differences openly: baseline stop uses signal ATR and
entry-relative distance; retest uses a frozen earlier level/ATR and structural stop.
The retest may have fewer/later trades and more cancellations/cash time. Do not
force the trade populations to match, nor imply equal exposure from equal risk%
or equal starting capital. Entry conditions and eligible-opportunity counts differ.

An early comparison is a same-dataset descriptive experiment. A later held-out
protocol must freeze rules and record previous experimentation before claiming
external evidence. The user should learn why fair comparison needs more than return.

## Suggested product flow

1. Existing Backtest lab exposes a clearly named **Compare strategies** route or
   mode. Keep two-stock comparison separate and preserve existing workspace state.
2. Show the actual dataset/replay/basis/action-policy/readiness and common account
   assumptions. Show each frozen strategy/version and retest parameters.
3. Explain the window/warm-up/cutoff policy in ordinary language. Enable Run only
   when the data/execution policy permits it; no bypass for adjusted research.
4. Run both under the declared protocol. Display a two-column metrics table and
   aligned equity/drawdown charts, with cash exposure/opportunity coverage where
   precisely defined and available.
5. Make no-trade/few-trade/censored/pending/forced-cutoff cases visible. Do not
   select a winner, show confidence scores or use red/green profit alone as advice.
6. Let users inspect each trade/audit and download the complete comparison record,
   both trade ledgers and aligned curve data. Keep saved-original inputs when stale.
7. Explain concepts through concise reference/tooltips and an original labelled
   hypothetical example, without exercises. Update the shared concept catalogue
   only where this feature adds an actual concept/rule.

## Metrics and benchmarks

For the first release, use well-defined common metrics already computed correctly:
net ending wealth/return, observed marked-equity maximum drawdown, number of trades,
win fraction only when trades exist, cost totals where available, and explicit
natural-versus-forced-cutoff counts. Derive any new metric independently in tests.
If showing exposure, define the numerator, denominator and whether cash/entry/exit
bars count. Do not call gross P&L after slippage a pre-slippage return.

Buy-and-hold can be a **separately labelled reference**, but the existing gross
close-to-close number is unlike a costed next-open cash strategy. Either preserve
that distinction visibly or specify/test a matching investable benchmark. Do not
pretend the gross reference is a fair net benchmark by merely relabelling it.

Do not casually annualize sparse irregular daily observations or add Sharpe/Sortino
without a justified return frequency, calendar/coverage convention and cost basis.
Dependent returns and repeated parameter selection make naive significance tests
misleading. Statistical inference/calibration is a separate later acceptance gate.

## Implementation guidance, without prescribing empty folders

Prefer a pure comparison/protocol module and an immutable record builder, with
a thin UI using the existing saved-result/state helpers. The exact filenames are
implementation choices. Reuse calculators rather than reimplementing fills in UI.
Preserve original equity timestamps and export units; state any rebasing/intersection
policy. A hidden cache key must include actual data/protocol/version inputs.

Current record builders are `saved_backtest.py` and `retest_records.py`. Read how
they select relevant identity fields. The comparison request ID should be stable
under display-only changes and change for every actual calculation change. Store
both original outputs with the protocol; strict JSON must reject/normalize undefined
numbers rather than emit invalid NaN/Infinity tokens.

Do not require a database just to implement one immutable session comparison. Do
not call that record durable history. Reopening persisted records is a subsequent
storage/version/migration acceptance gate.

## Acceptance checklist for the next assistant

- [ ] Written versioned protocol names actual execution/evaluation/warm-up/cutoff
  rules and discloses sample/exposure differences before user interpretation.
- [ ] Pure output matches each existing simulator exactly under the same relevant
  input/configuration; no frozen engine changes or invented signal equivalence.
- [ ] Independent arithmetic fixtures verify net wealth, drawdown, selected cost/
  exposure metrics and units; engine outputs are not their own only oracle.
- [ ] Future-append/prefix checks preserve natural decisions through the original
  cutoff, with artificial end liquidation handled explicitly rather than compared
  as a natural future-invariant event.
- [ ] No trades, one trade, all-cancelled, insufficient warm-up, zero shares,
  pending setup, gap cancellation, same-bar barriers and forced end exits render
  meaningful unavailable/coverage states instead of misleading zeros or winners.
- [ ] Source/replay/cost/retest-rule/policy changes affect identity/staleness; display
  changes do not. Both saved outputs/exports remain attached to original inputs.
- [ ] Adjustment/action execution restrictions remain effective at engine, builder
  and UI boundaries. Generic/NSE accepted inputs still work unchanged.
- [ ] The first chosen evaluation-start policy has direct tests; if arbitrary
  starts are unsupported, the UI cannot imply support or silently carry positions.
- [ ] Browser verifies route discovery, setting clarity, retained context, actual
  computation, empty/small-sample results, charts/tables and real downloadable record.
- [ ] Relevant regression and complete suite pass; measured results are logged.
- [ ] New concept/reference, roadmap gate, generated docs, build report and work
  log reflect actual scope; original-phase statuses remain honest.
- [ ] Reviewed source/tests/synthetic/docs are privately published and branch/files
  verified. Observe remote CI separately; no claim of predictive performance.

## What follows

Durable immutable dataset/run/experiment storage, frozen chronological evaluation,
dependence/selection-aware uncertainty and prospective paper tracking. Expand the
strategy/indicator/pattern catalogue one testable question at a time. An optional
LLM may narrate structured evidence later; it cannot substitute for these gates.
