# Research reliability and workflow increment

Implemented 2026-11-15. This is a bounded usability/reliability milestone following
the [platform inspection](PLATFORM_INSPECTION_2026-11-15.md). It improves the
existing daily-data research workflow; it adds no strategy, predictive model or
investment-performance validation. New exercises remain paused.

## The usable workflow

1. Open Research dashboard with the synthetic example or one completed daily file.
   Original NSE security-history CSVs still work without editing.
2. Read **Data readiness** before interpreting the result. It names the symbol,
   observation count, cutoff range, price basis and unavailable calculations.
   Expand the recovery table for minimum-history counts or undefined-value reasons.
3. Inspect the chart and observation log. Select one row and choose **Study this
   observation type** to open its cohort in After the pattern. Diagnostic lifecycle
   states remain visible but cannot initiate an unsupported outcome study.
4. Keep or change the study's date/context/spacing filters. The incoming selection
   chooses the event type; it does not silently reset every study assumption.
   Neutral observations select upward price change rather than directional returns.
5. Use **Test the fixed breakout baseline** to open Backtest lab. It tests the
   existing long-breakout rule, not every event in the study. A dedicated
   breakout-retest execution strategy remains the next major feature.
6. Run the baseline. Change an overlay or visit a reference page: the completed
   result survives. Change a calculation input: the old result stays visible with
   an out-of-date warning until another run replaces it. Download the JSON/ledger
   to retain a copy beyond this browser session.

The Research steps controls provide visible links to all five workspaces. The
sidebar research inputs are rendered on all workspaces to preserve their state,
including an uploaded file, while reading a reference/checklist. Those pages still
need no upload. The comparison page identifies its own two datasets separately;
the retained single-stock sidebar inputs do not drive its statistics. Quick
reference buttons open the selected RSI, ATR, relative-volume, pivot-delay or
historical-outcome article directly in the concept library, clearing incompatible
search filters. This is contextual reference content, not new learner assignments.

## Chart date boundaries and evidence

The main price chart and side-by-side price charts use the last 250 observations
of the supplied analysis, or all available observations when shorter. Every trace
is restricted to those dates. Event geometry is drawn only when its knowledge
time is available in the supplied analysis; pivots also require their detection
time to be available. Replay still truncates data before analysis.

Line segments crossing a display boundary are clipped by linear interpolation.
For example, an invented line from day 1 at ₹100 to day 5 at ₹120 intersects day 3
at ₹110. That intersection is a drawing vertex, not a newly detected pivot. The
line layer has no pivot markers; separate markers show only actual original
anchors within the view. Disjoint visible segments remain separated. Full
formation coordinates, dates and detector evidence are left unchanged in exports.

All three date axes receive the same explicit bounds, with half a day of visual
padding at each end so edge candle bodies remain visible. Padding creates no
observations. The caption reports actual displayed/total counts and dates and
explains that zones describe the current as-of snapshot. It no longer claims
250 observations when a short file contains only 21. Zoom/pan remain available.

This fixes old annotations expanding the displayed date period. It does not add
chart editing, a full pattern catalogue, causal trendline/channel fitting,
independent validation or automatic selection of an economically useful period.

## One immutable baseline result per session

`saved_backtest.py` calls the existing numerical simulator without modifying its
entry, sizing, stop, target, gap, cost or exit rules. It freezes a JSON record and
trade CSV in a frozen `SavedBacktest` value stored outside transient widget state.
The record uses schema `saved-backtest/1` and strategy version `long-breakout/1`,
with UTC capture time, the calculation identity, original analysis evidence,
settings, metrics, trades and equity observations. A rerun replaces this one slot.

The identity covers the strategy version, full Settings, source SHA256, symbol,
price basis, dataset/research-view identity, execution restriction and the
canonical visible OHLCV plus EMA50/ATR14/relative-volume values used by the baseline.
Changing replay, source, calculations, costs, capital, risk or execution policy
therefore invalidates its match with current inputs. Display overlays and the
separate descriptive breakout/retest ResearchRules do not change this strategy's
identity. A future simulator-rule change must also update the strategy version.

The displayed saved header/settings and both downloads come from the frozen
record. They are never reconstructed using today's sidebar values. Hypothetically,
after a 10-bps-per-side run, setting charges to 25 bps leaves the old 10-bps record
and outputs available under the warning. Running again creates a 25-bps record.
Switching back to exactly matching inputs removes the stale warning because the
retained calculation again matches; it does not imply a new calculation occurred.

Execution restrictions still disable new runs and are checked inside the save
function. A previous unrestricted run can remain as explicitly stale historical
context after moving to a restricted research view. Retention cannot authorize a
new simulation on prohibited inputs. Insufficient history can produce a valid
zero-trade run; the UI states that absence explicitly rather than calling it a
failed trade or reporting an available win rate.

Session memory is not durable storage. A new session, server restart or connection
reset can lose the slot. No database, run browser, archive importer, multi-run
comparison or full experiment registry is implemented. Dataset bytes are not
automatically embedded in the saved result. Keep the original input and its
declarations with downloaded evidence if reproduction matters.

Sidebar data and baseline assumptions persist through reference navigation.
Non-sidebar replay, rule and action widgets do not yet have a complete cross-page
workspace-state contract; they may reset when their controls are absent. Check the
cutoff and rules on return. Current-input matching prevents a retained backtest
from silently adopting such changes. A full saved/reopened workspace is future work.

## Readiness means defined calculations

Readiness inspects actual values at the replay cutoff and explains the engine's
warm-up conventions. It distinguishes history shortage from undefined arithmetic
such as a zero previous-volume denominator or zero stochastic price range.

| Calculation | Minimum observed bars in this engine |
| --- | ---: |
| RSI14 | 15 closes / 14 changes |
| ATR14 | 14 |
| EMA20 / SMA20 / Bollinger20 | 20 |
| EMA50 / SMA50 | 50 |
| SMA200 | 200 |
| MACD line | 26 |
| MACD signal / histogram | 34 |
| Relative volume versus prior 20 | 21 |
| ROC10 | 11 |
| Fast stochastic %K14 / %D3 | 14 / 16 |

The table also includes confirmed price structure, prior-week context and the
baseline's context inputs. Structure needs the required confirmed highs/lows,
not an invented fixed row guarantee. Weekly context needs 20 prior calendar-week
aggregates and excludes the latest calendar week; existing calendar/source caveats
remain. Baseline context availability does not guarantee its breakout trigger or
an executable order.

A hypothetical valid 21-row input can have RSI, ATR and relative volume while
EMA50 needs 29 more observations. Readiness also surfaces the existing freshness
assessment, calendar coverage, flagged-date counts, unverified adjustment basis
and execution restrictions. No data rows are filled or removed by this display.
Synthetic data have no supported exchange-calendar declaration and say Not
assessed; a green calculation status never authenticates the source or predicts
a profitable trade. More calendar days alone do not imply more observed bars.

## Verification and audit follow-up

- Full local regression after source changes: **268 passed in 53.80 seconds**
  on Python 3.13.7; 28 new reliability cases plus the original 240.
- New tests cover crossing/reversed/vertical/outside geometry, a pattern-containing
  narrow period, source-evidence preservation, future-state filtering, real
  warm-up boundaries, undefined values, source/replay/basis/policy/settings identity,
  immutable exports, overlay retention, stale costs, reference navigation and
  study/baseline routes. Existing action/execution tests remain required.
- Browser checks covered the 600-row synthetic fixture, stale saved assumptions,
  actual original NSE 21-row upload, reference round trip retaining that upload,
  task pills, direct RSI article, keyboard observation selection, selected-cohort
  prefill and the baseline-tab route. Real input data stayed local; proof images
  use synthetic data only. No new mobile/accessibility certification is claimed.
- The old F02 supplemental audit probe and the first new UI test mistakenly used
  the first checkbox, enabling an action ledger. Corrected label-based reproduction
  against published pre-change `a482bc7` confirmed the baseline output disappearing
  after the actual Bollinger toggle, with no app exception. The finding was valid;
  the originally described interaction evidence was inaccurate. The new test uses
  the labelled control and checks assumptions as well as the retained result.
- Restricted local test attempts hung in Python's Windows asyncio socket-pair
  initialization before application execution. A run with local communication
  permitted completed the suite above. Identified stalled test processes were
  closed; these attempts are not recorded as application failures or passes.

F01/F02 and the bounded F03/F04 readiness/count scope are repaired. F05–F07 receive
task links, point-of-use references and explicit baseline-versus-detector/cost
scope; the broader glossary-everywhere and accessibility gates remain open. The
study-date widget avoids supplying a default alongside existing session state;
repeated study navigation tests pass. Other audit findings remain in the dated
inspection. Publication and any actual remote CI observations are recorded in
[GITHUB_SYNC.md](GITHUB_SYNC.md), separately from local acceptance.

Implementation references: `quant_engine/charts.py`, `saved_backtest.py`,
`backtest_ui.py`, `readiness.py`, `workflow_ui.py`, `event_study_ui.py`, `app.py`,
`learning/pages.py` and `tests/test_reliability.py`.

Further reading checked 2026-11-15: [Streamlit session state](https://docs.streamlit.io/develop/concepts/architecture/session-state)
for rerun/session mechanics; [pandas windowing](https://pandas.pydata.org/docs/user_guide/window.html)
for rolling-window concepts. The minimum counts and snapshot rules above are this
project's tested conventions, not a claim that those libraries set trading rules.
