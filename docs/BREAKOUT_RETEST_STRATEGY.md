# Breakout-retest execution strategy · version 1

Specification frozen and implemented on2026-11-15. Version: `long-breakout-retest/1`.
Full local acceptance: **323 passed in84.15s**; final chart-marker presentation
check **1 passed in4.35s**. Detailed evidence is in WORK_LOG.md. Publication and
actual remote CI are recorded separately in GITHUB_SYNC.md after observation.
This is a long-only daily research hypothesis, not a recommendation or a validated
edge. It is independent of the chart's descriptive ResearchRules and the existing
fixed breakout baseline. New exercises remain paused.

## Decision chronology

At completed bar b, calculate L = maximum high of the previous N observations and
A = ATR14 at b−1. Require finite positive A, close[b] > L + buffer×A,
close[b−1] <= that threshold, relative volume[b] >= minimum, and close[b] > EMA50[b].
The range excludes b; relative volume excludes b from its volume denominator.
Freeze L and A. Defaults: N20, buffer0.1, volume1.2. A fresh geometric/volume break
that fails EMA50 or capacity still receives an audit row; weak-volume/non-crossing
bars are not candidates. Warm-up is reported separately.

Only one pending setup or long position is allowed. New qualifying breaks while
busy are skipped and audited. Terminal transitions cannot restart on the same
bar. No pyramiding, leverage, shorts or same-bar re-entry.

For each later bar r, apply these rules in order:

1. If close[r] < L − invalidation×A, cancel (default0.5). This is a close-based
   setup rule, not a claim that a resting order filled at that threshold.
2. If r−b >= retest_window (default10), expire before checking a retest. Eligible
   retest ages are1 through9 by default. All ages count observed bars, not days.
3. A retest intersects [L−tolerance×A, L+tolerance×A] and closes at/above L.
   Default tolerance0.25. It must close above EMA50[r]. A retest failing that
   trend filter cancels the setup. No same-breakout-bar retest is possible.
4. Freeze stop S = min(low[r], L) − stop_buffer×A (default0.25). A nonpositive
   stop cancels. Schedule one entry attempt at the next observed open, even if
   that next bar is the expiry age; the retest itself met the deadline.

At that next open, before reading the day's high/low/close for entry:

- Cancel if open <= S, or open < L, or open > close[r] + max_gap×A (default1).
  Equality at the maximum gap is allowed. An invalid/chased entry never rolls
  forward to another day. Stop/gap cancellation takes precedence over sizing.
- Entry fill E = open×(1+slippage). The frozen structural stop does not move with
  the opening gap. D = E−S; target T = E + reward_multiple×D (default2).
- Require positive net reward at the target after the declared exit slippage and
  both fees. Otherwise cancel. Size whole shares using current cash equity,
  cost-aware stop loss, available cash and retest-bar volume participation caps.
  The shared sizing helper includes entry/exit fees and adverse stop slippage.
  Zero shares is an explicit cancellation; no fictitious fractional fill.

## Position management and accounting

Stops/targets are fixed at entry. Exit precedence matches the existing baseline:
open <= S → opening gap stop; open >= T → opening gap target; low <= S → stop;
high >= T → target; holding limit → close; otherwise keep the position. If both
barriers touch in a daily bar, assume stop first and label the ambiguity. This
applies on the entry bar too. An opening target exit assumes an executable market
exit at the observed open; it is a simulation convention, not a guaranteed fill.

Every exit receives adverse slippage and per-side fees. Default holding limit is
10 observations including entry. Remaining positions liquidate at dataset/replay
end after normal exits; forced liquidations are labelled and counted separately.
They are boundary assumptions, not naturally completed target/stop observations.
Pending setups stay Awaiting retest / Awaiting next open at cutoff, not failed or
expired simply because the file ends. Current-plan snapshots describe the cutoff
before an artificial end liquidation. Extending a file may therefore change an
old forced end exit; natural events/fills before that boundary remain causal.

Daily equity equals cash plus estimated net liquidation value of any held shares.
Entry cash includes fees; no interest, leverage, dividends, settlement constraints,
auctions, price bands, partial fills, price impact, statutory fee schedule or
exchange holiday repair is modeled. Gaps can exceed planned risk; volume caps do
not prove real liquidity. Existing corporate-action execution restrictions apply
inside the engine and record builder as well as the UI. No orders are sent.

## Auditable output and website scope

Backtest lab offers this strategy alongside the unchanged fixed baseline. Its own
controls, explicit rules, setup decisions, transition tape, trade/equity ledger,
current conditional state and inspectable setup chart are required. Show the
frozen level/ATR, breakout, retest, scheduled next-open action, stop/target, risk,
costs and reason for each terminal/no-trade outcome.

Save one immutable session result with versioned rules, input/provenance identity,
original bars, settings, metrics and audit rows. Display changes retain it; actual
input/rule changes mark it stale. Downloads must describe the saved inputs rather
than today's controls. Original bars in the local download enable faithful stale
setup charts. No runtime records or owner market-data files enter source uploads.

Fair strategy comparison and independent chronological validation are a separate
next milestone. Do not infer superiority from unequal trade samples or claim an
investment edge from tests or a synthetic example. Do not convert bearish
observations into unsupported overnight short execution.

## Acceptance gates

Independent arithmetic fixtures must verify chronology, frozen levels/ATR/stop,
target, cash/risk/prior-volume caps, cost-sensitive P&L/equity, opening cancellations,
same-bar ambiguity, gaps exceeding risk, exact expiry/holding boundaries, warm-up,
zero/no-trade states, capacity, cutoff pending/forced-liquidation semantics and
prefix invariance excluding artificial boundary exits. Existing baseline tests
must still pass. UI checks must cover strategy switching, changed rules/staleness,
saved exports, audit/inspection, replay and execution restrictions. Documentation,
shared concepts/checklist and verified private publication complete the gate.

Conceptual references checked2026-11-15: [Fidelity support and resistance](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/support-and-resistance)
for level-role ideas, and [CFA Institute backtesting and simulation](https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/backtesting-and-simulation)
for historical evaluation and its limitations. All exact thresholds and execution
assumptions here are original, testable project choices; those sources do not
validate this strategy or prescribe its numbers.
