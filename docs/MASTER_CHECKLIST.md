# Master implementation and learning checklist

Updated: 2026-11-15

Source of truth: `learning/roadmap.py`. Regenerate with `python scripts/export_learning_docs.py`.

357 work items: 50 done, 48 partial, 247 planned, 12 optional / later.

Done means the named software gate is evidenced; it does not mean profitable trading or learner mastery. Partial items intentionally remain unchecked. Optional extensions are outside the core completion gate.

Work order: S00/S01 → S02 → S03/S06 → S04/S05 → S07 → S08/S09 → S10 → S11 → S12. S13/S14 follow reliable evidence; S15/S18 continue across stages; S16 follows frozen rules. S17 intraday is a separate expansion. S19 requires a new hypothesis. S20 exercises accompany each stage.

Every new detector/indicator/strategy also needs a concept explanation, hypothetical example, misconception warning, source, numerical/negative tests, time-availability checks, UI evidence and log entry.

The full original requirements remain in `docs/ORIGINAL_BRIEF.md`; original section references below make coverage traceable.


## S00 · Learning foundation and version control

Original brief: 1,17,20,22 + learning request

**Learn:** Distinguish concepts, calculations, strategies and evidence. Learn files, tests, commits and documentation.

**Acceptance gate:** Shared catalogue renders in app and handbook; navigation/search/examples pass tests; repository content is verified.

- [x] **S00-001** · Done · Preserve original brief and refined first-build plan

- [x] **S00-002** · Done · Establish continuing AGENTS.md learning and logging agreement

- [x] **S00-003** · Done · Create master checklist with statuses, dependencies and acceptance gates

- [x] **S00-004** · Done · Add searchable Education and Concepts page independent of uploads

- [x] **S00-005** · Done · Export shared concept handbook and master checklist

- [x] **S00-006** · Done · Add original worked examples, learning labs and misconception checks

- [x] **S00-007** · Done · Add detailed build report and chronological work log

- [x] **S00-008** · Done · Add first lesson: from OHLCV to a falsifiable strategy

- [x] **S00-009** · Done · Create private GitHub repository

- [x] **S00-010** · Done · Upload reviewed source, synthetic data, tests and documents; verify remote tree

- [x] **S00-011** · Done · Add automated test workflow; distinguish local pass from remote CI pass

- [ ] **S00-012** · Planned · Record learner questions and exercises without claiming mastery


## S01 · Audit the current daily-data prototype

Original brief: 3,4,7,14,16,21

**Learn:** Read an OHLCV candle, a causal indicator and a sequential trade ledger.

**Acceptance gate:** Reproduce numerical fixtures and documented assumptions; supported upload/replay/report flows pass.

- [x] **S01-001** · Done · Local Streamlit application and documented launch instructions

- [x] **S01-002** · Done · CSV and XLSX ingestion for one daily symbol

- [x] **S01-003** · Done · Strict OHLCV/date/duplicate/missing/nonfinite validation

- [x] **S01-004** · Done · Source hash and adjustment declaration

- [x] **S01-005** · Done · SMA20/50/200 and EMA20/50 numerical calculations

- [x] **S01-006** · Done · Wilder RSI14 and ATR14 numerical calculations

- [x] **S01-007** · Done · MACD12/26/9, Bollinger20, OBV and prior-session relative volume

- [x] **S01-008** · Done · Confirmed swings with formation and detection dates

- [x] **S01-009** · Done · Basic HH/HL and LH/LL market structure

- [x] **S01-010** · Done · As-of pivot-cluster support/resistance zones

- [x] **S01-011** · Done · Doji and bullish/bearish engulfing geometric observations

- [x] **S01-012** · Done · Double-top/bottom geometric event lifecycle

- [x] **S01-013** · Done · Completed prior-week SMA20 context

- [x] **S01-014** · Done · As-of historical replay and consistent chart annotations

- [x] **S01-015** · Done · One conditional long breakout plan and cost-aware whole-share sizing

- [x] **S01-016** · Done · Sequential breakout backtest with fees, slippage, gap and ambiguity rules

- [x] **S01-017** · Done · Download report, indicators, evidence and trade/equity record

- [x] **S01-018** · Done · Baseline numerical and application test suite


## S02 · Reliable Indian equity data

Original brief: 4,16,20

**Learn:** Understand session dates, adjustments, data licensing, missingness and survivorship.

**Acceptance gate:** Versioned source and adjustment metadata; calendar/corporate-action fixtures; no invented observations; provider failures handled.

- [ ] **S02-001** · Partial · Choose and document licensed Indian historical-data source and permitted uses

- [ ] **S02-002** · Partial · Provider-neutral daily data contract and symbol/company-name resolver

- [ ] **S02-003** · Partial · NSE/BSE identifiers, symbol changes, mergers and delistings

- [ ] **S02-004** · Partial · Exchange trading calendar, holidays and exceptional sessions

- [x] **S02-005** · Done · Asia/Kolkata timestamps and explicit session-date semantics

- [ ] **S02-006** · Partial · Detect genuinely missing sessions against the configured calendar

- [ ] **S02-007** · Partial · Consistent split/bonus adjustment across OHLC and volume

- [ ] **S02-008** · Partial · Dividend/total-return conventions and point-in-time adjustment policy

- [ ] **S02-009** · Planned · Rights/demerger/merger action handling and ambiguous-action review queue

- [ ] **S02-010** · Partial · Preserve original raw files plus normalized versioned datasets

- [ ] **S02-011** · Partial · Cross-source data checks, stale-feed detection and source timestamps

- [ ] **S02-012** · Partial · Duplicate correction policy with a visible audit record

- [ ] **S02-013** · Planned · Outlier, zero-volume, price-circuit and suspension flags

- [ ] **S02-014** · Planned · Adjusted-close, VWAP, number-of-trades and spread optional schema

- [ ] **S02-015** · Planned · Delivery volume and delivery percentage where licensed/available

- [ ] **S02-016** · Planned · Market-index and sector-index context

- [ ] **S02-017** · Planned · Point-in-time index constituents to reduce survivorship bias

- [ ] **S02-018** · Planned · Provider outage/rate-limit/retry/error behavior

- [ ] **S02-019** · Partial · Data completeness/freshness dashboard and adjustment-quality gates

- [x] **S02-020** · Done · No interpolation/fabrication; clearly report unavailable fields

- [x] **S02-021** · Done · Direct NSE security-history CSV upload without manual cleanup

- [x] **S02-022** · Done · NSE CM 2026 calendar snapshot and visible-slice completeness/freshness audit

- [x] **S02-023** · Done · Reviewed split/bonus ledger, replay-safe adjusted research and factor exports


## S03 · Price structure, zones and breakouts

Original brief: 5.1,5.2,5.3

**Learn:** Explain HH/HL/LH/LL, pivot delay, support/resistance, breakouts and failed setups.

**Acceptance gate:** Explicit configurable rules, positive/negative examples, formation/detection timestamps, no future-append changes.

- [ ] **S03-001** · Planned · Configurable swing significance, tie handling and volatility-aware filtering

- [ ] **S03-002** · Planned · Trend strength, consolidation, sideways and possible-reversal classifications

- [ ] **S03-003** · Planned · Swing-based structure breaks with explicit confirmation time

- [ ] **S03-004** · Planned · Horizontal zones with rejection strength, interactions and age

- [ ] **S03-005** · Planned · Dynamic moving-average support/resistance

- [ ] **S03-006** · Planned · Previous session/week highs and lows

- [ ] **S03-007** · Planned · Psychological levels with explicit price-increment convention

- [ ] **S03-008** · Planned · Volume-near-level significance without inventing order flow

- [ ] **S03-009** · Planned · Support/resistance role reversals

- [ ] **S03-010** · Partial · Bullish breakout and bearish breakdown states

- [ ] **S03-011** · Partial · Volume/distance/closing-position breakout confirmation

- [ ] **S03-012** · Partial · Failed breakout and false breakdown event tracking

- [ ] **S03-013** · Partial · Retests and breakout-retest conditions

- [ ] **S03-014** · Planned · Trendlines/channels with stable causal anchors

- [ ] **S03-015** · Planned · Conflicting and insufficient-evidence explanations

- [x] **S03-016** · Done · Frozen prior-range breakout/retest/failure/continuation events and replay evidence


## S04 · Chart-pattern catalogue

Original brief: 5.4,13,21

**Learn:** Translate visual descriptions into geometry, tolerances and state transitions; geometry is not profitability.

**Acceptance gate:** Each named detector has mathematical rules, positive/negative fixtures, coordinates, state lifecycle, annotations and education.

- [ ] **S04-001** · Partial · Double bottom: contextual significance and research validation

- [ ] **S04-002** · Partial · Double top: contextual significance and research validation

- [ ] **S04-003** · Planned · Triple bottom

- [ ] **S04-004** · Planned · Triple top

- [ ] **S04-005** · Planned · Head and shoulders

- [ ] **S04-006** · Planned · Inverse head and shoulders

- [ ] **S04-007** · Planned · Rounding bottom

- [ ] **S04-008** · Planned · Rounding top

- [ ] **S04-009** · Planned · Broadening formations

- [ ] **S04-010** · Planned · Bullish flag

- [ ] **S04-011** · Planned · Bearish flag

- [ ] **S04-012** · Planned · Bullish pennant

- [ ] **S04-013** · Planned · Bearish pennant

- [ ] **S04-014** · Partial · Ascending triangle

- [ ] **S04-015** · Partial · Descending triangle

- [ ] **S04-016** · Partial · Symmetrical triangle

- [ ] **S04-017** · Planned · Rising wedge

- [ ] **S04-018** · Planned · Falling wedge

- [ ] **S04-019** · Partial · Rectangle consolidation

- [ ] **S04-020** · Planned · Price channels

- [ ] **S04-021** · Planned · Cup and handle

- [ ] **S04-022** · Planned · Inverse cup and handle

- [ ] **S04-023** · Partial · Breakout retest formation

- [ ] **S04-024** · Partial · Bullish divergence

- [ ] **S04-025** · Partial · Bearish divergence

- [ ] **S04-026** · Planned · Higher-high/higher-low and lower-high/lower-low sequence patterns

- [ ] **S04-027** · Planned · Developing/confirmed/invalidated/inconclusive/expired pattern lifecycle standard

- [ ] **S04-028** · Planned · Pattern boundary/neckline/anchor coordinates and clickable evidence

- [ ] **S04-029** · Planned · Configurable tolerances, geometric-fit diagnostics and versioned definitions

- [x] **S04-030** · Done · Six-anchor triangle/rectangle geometry with frozen boundaries and causal state events


## S05 · Candlestick catalogue and context

Original brief: 6,13,21

**Learn:** Understand bodies, shadows, gaps, preceding trend and the difference between shape and actionable evidence.

**Acceptance gate:** Each named detector has OHLC geometry tests, context/gap rules, known-time markers, conflicts and a lesson; no reliability claims without research.

- [ ] **S05-001** · Partial · Doji with preceding-trend and support/resistance context

- [ ] **S05-002** · Planned · Dragonfly doji

- [ ] **S05-003** · Planned · Gravestone doji

- [ ] **S05-004** · Planned · Long-legged doji

- [ ] **S05-005** · Partial · Hammer

- [ ] **S05-006** · Partial · Hanging man

- [ ] **S05-007** · Partial · Inverted hammer

- [ ] **S05-008** · Partial · Shooting star

- [ ] **S05-009** · Planned · Bullish marubozu

- [ ] **S05-010** · Planned · Bearish marubozu

- [ ] **S05-011** · Planned · Spinning top

- [ ] **S05-012** · Partial · Bullish engulfing with context and historical evaluation

- [ ] **S05-013** · Partial · Bearish engulfing with context and historical evaluation

- [ ] **S05-014** · Planned · Piercing pattern

- [ ] **S05-015** · Planned · Dark cloud cover

- [ ] **S05-016** · Planned · Bullish harami

- [ ] **S05-017** · Planned · Bearish harami

- [ ] **S05-018** · Planned · Tweezer bottom

- [ ] **S05-019** · Planned · Tweezer top

- [ ] **S05-020** · Planned · Bullish kicking

- [ ] **S05-021** · Planned · Bearish kicking

- [ ] **S05-022** · Partial · Morning star

- [ ] **S05-023** · Partial · Evening star

- [ ] **S05-024** · Planned · Morning doji star

- [ ] **S05-025** · Planned · Evening doji star

- [ ] **S05-026** · Planned · Three white soldiers

- [ ] **S05-027** · Planned · Three black crows

- [ ] **S05-028** · Planned · Three inside up

- [ ] **S05-029** · Planned · Three inside down

- [ ] **S05-030** · Planned · Three outside up

- [ ] **S05-031** · Planned · Three outside down

- [ ] **S05-032** · Planned · Configurable body/wick/gap/trend definitions for each candle family

- [ ] **S05-033** · Planned · Volume confirmation, supporting/conflicting indicators and strength evidence

- [ ] **S05-034** · Planned · Reference-library comparison (evaluate TA-Lib installation/definitions)

- [ ] **S05-035** · Planned · Do not convert every recognized candle into a trading signal

- [x] **S05-036** · Done · Context-aware shadow and Morning/Evening Star detector variants with known-time tests


## S06 · Configurable indicators and interpretation

Original brief: 7

**Learn:** Compare trend, momentum, volatility and volume; understand seeds, warm-up and correlated evidence.

**Acceptance gate:** Each indicator matches independent fixtures, defines parameters/seeds/warm-up, stays causal and has interpretation plus limitations.

- [ ] **S06-001** · Planned · Configurable SMA/EMA/WMA periods including 9/20/50/100/200

- [ ] **S06-002** · Planned · Configurable MACD periods and histogram interpretation

- [ ] **S06-003** · Planned · ADX and directional movement

- [ ] **S06-004** · Planned · Parabolic SAR

- [ ] **S06-005** · Planned · Supertrend

- [ ] **S06-006** · Planned · Configurable Wilder RSI and flat-series conventions

- [ ] **S06-007** · Partial · Stochastic oscillator

- [ ] **S06-008** · Planned · Stochastic RSI

- [ ] **S06-009** · Partial · Rate of change

- [ ] **S06-010** · Planned · Williams %R

- [ ] **S06-011** · Planned · Commodity Channel Index

- [ ] **S06-012** · Planned · Configurable ATR and percentage-ATR

- [ ] **S06-013** · Planned · Configurable Bollinger bands and bandwidth

- [ ] **S06-014** · Planned · Return standard deviation and annualization assumptions

- [ ] **S06-015** · Planned · Historical volatility

- [ ] **S06-016** · Planned · Donchian channels

- [ ] **S06-017** · Planned · Keltner channels

- [ ] **S06-018** · Planned · Volatility expansion, contraction and squeeze states

- [ ] **S06-019** · Planned · Configurable OBV and slope interpretation

- [ ] **S06-020** · Planned · Session-anchored VWAP

- [ ] **S06-021** · Planned · Accumulation/distribution line

- [ ] **S06-022** · Planned · Chaikin money flow

- [ ] **S06-023** · Planned · Money flow index

- [ ] **S06-024** · Planned · Relative volume and rolling volume baselines

- [ ] **S06-025** · Planned · Same-time-of-day intraday relative volume

- [ ] **S06-026** · Partial · Price-volume and price-momentum divergence rules

- [ ] **S06-027** · Partial · Momentum acceleration and deterioration

- [ ] **S06-028** · Planned · Buying/selling-pressure proxies with explicit limitations

- [ ] **S06-029** · Planned · Avoid double-counting correlated indicators in aggregate scores

- [ ] **S06-030** · Planned · Explain reinforcing versus contradictory evidence by indicator family

- [x] **S06-031** · Done · ROC10, fast stochastic, momentum explanations and confirmed-pivot RSI/MACD divergences


## S07 · Multi-timeframe analysis

Original brief: 4.2,8

**Learn:** Aggregate OHLCV correctly and distinguish completed higher-timeframe context from a developing bar.

**Acceptance gate:** Session-aware aggregation, complete-bar availability and causal cross-timeframe joins are tested; unavailable context stays unavailable.

- [ ] **S07-001** · Planned · Daily/weekly/monthly aggregation and explicit partial-period policy

- [ ] **S07-002** · Planned · 1-minute, 5-minute, 15-minute and 30-minute data support

- [ ] **S07-003** · Planned · 1-hour and session-aware 4-hour bars where appropriate

- [ ] **S07-004** · Planned · Never upsample coarse observations into fabricated finer candles

- [ ] **S07-005** · Planned · Top-down weekly/daily/hourly/entry-timeframe workflow

- [ ] **S07-006** · Planned · Availability-time joins to prevent higher-timeframe leakage

- [ ] **S07-007** · Planned · Alignment and contradiction summaries across timeframes

- [ ] **S07-008** · Planned · Cross-timeframe support/resistance confluence

- [ ] **S07-009** · Planned · Insufficient-history labels per timeframe and indicator

- [ ] **S07-010** · Planned · Boundary, holiday, session-anchor and early-close aggregation tests


## S08 · Conditional strategy catalogue

Original brief: 11

**Learn:** A strategy needs an exact trigger, legal instrument, order assumption, invalidation, exits and expiry.

**Acceptance gate:** Every strategy has a versioned rule specification, deterministic signals, next-action timing, no-trade reasons, replay and cost-aware tests.

- [ ] **S08-001** · Partial · Versioned strategy specification and parameter registry

- [ ] **S08-002** · Planned · Long breakout strategy research validation beyond prototype

- [ ] **S08-003** · Planned · Short/breakdown strategies only for legally supported instruments

- [x] **S08-004** · Done · Breakout-retest strategy

- [ ] **S08-005** · Planned · Reversal strategies tied to confirmed structures

- [ ] **S08-006** · Planned · Pullback-entry strategy

- [ ] **S08-007** · Planned · Momentum and trend-following strategies

- [ ] **S08-008** · Planned · Market, limit, breakout and pullback order semantics

- [ ] **S08-009** · Partial · Entry ranges, expiry and cancellation conditions

- [ ] **S08-010** · Planned · Market/sector and multi-timeframe confirmation

- [ ] **S08-011** · Planned · Multiple profit targets and partial exit rules

- [ ] **S08-012** · Planned · Explicit no-trade decisions and avoid-trade conditions

- [ ] **S08-013** · Planned · Intraday/swing/positional holding-style distinction

- [ ] **S08-014** · Planned · Structured plan with trigger, invalidation, horizon and evidence

- [x] **S08-015** · Done · Audit each long retest candidate, next-open cancellation, capacity skip and chronological fill/exit

- [x] **S08-016** · Done · Preserve versioned breakout-retest session records, original-price inspection and stale-input exports


## S09 · Risk, position sizing and evidence scores

Original brief: 11.2,11.3,11.4,12

**Learn:** Separate monetary risk, volatility, setup quality and calibrated probability.

**Acceptance gate:** Costs, price increments, gaps and capital constraints are tested; score components trace to evidence; probabilities require validation.

- [ ] **S09-001** · Partial · Swing/zone/ATR/pattern-invalidation stop methods

- [ ] **S09-002** · Planned · Measured-move, prior-level and ATR target methods

- [ ] **S09-003** · Planned · Fibonacci extensions as explicitly unvalidated hypotheses

- [ ] **S09-004** · Planned · Gap-aware portfolio stress tests and maximum-loss caveats

- [ ] **S09-005** · Planned · Tick-size and instrument lot-size constraints

- [ ] **S09-006** · Planned · Exchange/broker/order-specific asymmetric costs and taxes

- [ ] **S09-007** · Planned · Cash/settlement/buying-power and concentration constraints

- [ ] **S09-008** · Planned · Liquidity/spread/participation and fill uncertainty

- [ ] **S09-009** · Planned · Portfolio open risk, correlated exposure and sector caps

- [ ] **S09-010** · Planned · Separate geometric pattern quality, trend evidence and trading probability

- [ ] **S09-011** · Planned · Transparent risk classification with defined criteria

- [ ] **S09-012** · Planned · Unfavorable net reward/risk and nearby obstacle vetoes

- [ ] **S09-013** · Planned · Event/earnings/corporate-action risk flags with source timestamps

- [ ] **S09-014** · Planned · Never display arbitrary confidence percentages as probabilities


## S10 · Backtesting and validation protocol

Original brief: 16,21

**Learn:** Learn execution chronology, mark-to-market returns, drawdown, baselines and overfitting.

**Acceptance gate:** A frozen chronological protocol, realistic execution and comparable benchmarks produce reproducible ledgers and metrics with uncertainty.

- [ ] **S10-001** · Planned · Freeze chronological development, validation and untouched test periods

- [ ] **S10-002** · Planned · Version/hash every experiment's data, parameters and code

- [ ] **S10-003** · Planned · Benchmark cash, exposure-matched buy-and-hold and simple rules

- [ ] **S10-004** · Planned · Detailed fees, taxes, spread, slippage and market-impact model

- [ ] **S10-005** · Planned · Gap-through orders and stop/target same-bar ambiguity tests

- [ ] **S10-006** · Planned · Limit-order non-fills, partial fills and trading restrictions

- [ ] **S10-007** · Planned · Multiple targets, trailing stops and partial exits

- [ ] **S10-008** · Planned · End-of-data, event expiry and censored/open-position conventions

- [ ] **S10-009** · Planned · Net total return and annualized return with elapsed-time conventions

- [ ] **S10-010** · Planned · Historical win rate and average winner/loser

- [ ] **S10-011** · Planned · Profit factor, expectancy and sample-size uncertainty

- [ ] **S10-012** · Planned · Marked equity and maximum drawdown/drawdown duration

- [ ] **S10-013** · Planned · Sharpe and Sortino with return interval/risk-free assumptions

- [ ] **S10-014** · Planned · Calmar ratio and average holding period

- [ ] **S10-015** · Planned · Regime/timeframe/stock/sector breakdowns

- [ ] **S10-016** · Planned · Walk-forward research and overlapping-label treatment

- [ ] **S10-017** · Planned · Parameter robustness, sensitivity and regime stability tests

- [ ] **S10-018** · Planned · Multiple-testing/selection-bias and experiment-count disclosure

- [ ] **S10-019** · Planned · Block-bootstrap/Monte Carlo stress tests with dependent observations

- [ ] **S10-020** · Planned · Prospective-versus-historical result comparison

- [ ] **S10-021** · Planned · Evaluate Backtesting.py and VectorBT against execution requirements


## S11 · Historical pattern research database

Original brief: 9,14D,14F,17

**Learn:** Define an occurrence, comparable population, outcome horizon and independent sample.

**Acceptance gate:** Versioned events/features/outcomes persist, censoring/overlap is handled, and research summaries disclose cohort, dates and sample size.

- [ ] **S11-001** · Planned · SQLite schema and migrations with PostgreSQL-compatible interfaces

- [ ] **S11-002** · Planned · Persist symbols, versioned OHLCV and data provenance

- [ ] **S11-003** · Planned · Immutable analysis runs and parameter/engine versions

- [ ] **S11-004** · Partial · Occurrence records with market/timeframe/definition/known-time/features

- [ ] **S11-005** · Planned · Target-before-stop labels with fixed horizon and ambiguity policy

- [ ] **S11-006** · Partial · Successful/failed/expired/censored occurrence counts

- [ ] **S11-007** · Partial · MFE/MAE and average favorable/adverse movement

- [ ] **S11-008** · Planned · Time-to-target and holding-time distributions

- [ ] **S11-009** · Partial · Conditional pattern cohorts and feature combinations

- [ ] **S11-010** · Partial · Market-regime and timeframe performance slices

- [ ] **S11-011** · Partial · Non-overlapping samples, uncertainty and small-sample warnings

- [ ] **S11-012** · Partial · Research-lab filters by symbol, date, regime, subtype and context

- [x] **S11-013** · Done · No historical-performance display without an auditable cohort

- [x] **S11-014** · Done · Versioned forward-outcome study with known-time references, complete/censored horizons and portable records

- [x] **S11-015** · Done · Same-stock context-matched non-event baselines with explicit comparable coverage


## S12 · Probability models and machine learning

Original brief: 10,12.3

**Learn:** Learn labels, features, temporal leakage, base rates, calibration and economic utility.

**Acceptance gate:** Predefined target/stop/horizon, purged chronological evaluation, baseline comparison, calibration diagnostics and held-out after-cost results.

- [ ] **S12-001** · Planned · Point-in-time feature store for returns, indicators and market context

- [ ] **S12-002** · Planned · Predefine target, stop and horizon before creating labels

- [ ] **S12-003** · Planned · Up/down/horizon return and target-before-stop research objectives

- [ ] **S12-004** · Planned · Logistic-regression and unconditional-frequency baselines

- [ ] **S12-005** · Planned · Random forest comparison

- [ ] **S12-006** · Planned · XGBoost and LightGBM evaluation if justified

- [ ] **S12-007** · Planned · Chronological train/validation/test split

- [ ] **S12-008** · Planned · Purging and embargo for overlapping event labels

- [ ] **S12-009** · Planned · Feature scaling, missingness and selection fitted on training only

- [ ] **S12-010** · Planned · Precision, recall, F1, ROC-AUC and PR-AUC

- [ ] **S12-011** · Planned · Brier score, log loss and reliability/calibration diagrams

- [ ] **S12-012** · Planned · Probability calibration and confidence/uncertainty intervals

- [ ] **S12-013** · Planned · Subgroup/regime and out-of-distribution checks

- [ ] **S12-014** · Planned · Expected after-cost utility versus classification accuracy

- [ ] **S12-015** · Planned · Model registry, reproducibility, drift and retraining gates

- [ ] **S12-016** · Planned · Do not add deep learning without evidence simpler models are inadequate


## S13 · Screenshot observations and annotations

Original brief: 2,13

**Learn:** Learn why visible shape or pixel position is not exact OHLCV, time or a tradable fill.

**Acceptance gate:** Image-only observations are explicitly qualitative, uncertainty/axis limits are disclosed and structured data wins numerical conflicts.

- [ ] **S13-001** · Planned · Screenshot upload and chart-type recognition

- [ ] **S13-002** · Planned · Visible stock/timeframe/axis-label extraction with uncertainty

- [ ] **S13-003** · Planned · Cropping, resolution, distortion and missing-axis quality checks

- [ ] **S13-004** · Planned · Qualitative support/resistance/trendline observations

- [ ] **S13-005** · Planned · Visible candle/pattern/breakout candidates with approximate anchors

- [ ] **S13-006** · Planned · Green support, red resistance, blue boundaries and yellow candle annotations

- [ ] **S13-007** · Planned · Swing circles, directional arrows and consolidation highlights

- [ ] **S13-008** · Planned · Entry/stop/target overlays only when defensible and clearly conditional

- [ ] **S13-009** · Planned · Clickable annotations with known-time and evidence details

- [ ] **S13-010** · Planned · Strict image-only versus structured-data mode distinction

- [ ] **S13-011** · Planned · Structured-data reconciliation; never invent exact screenshot OHLCV


## S14 · Evidence-bound AI interpretation

Original brief: 3,15,20

**Learn:** Use a language model to communicate verified facts without letting it invent calculations or probabilities.

**Acceptance gate:** Provider-neutral narration has evidence references, factual/number checks, deterministic fallback, cost limits and prompt-injection tests.

- [ ] **S14-001** · Planned · Provider-independent LLM interface and environment-based credentials

- [ ] **S14-002** · Planned · Schema-validated numerical evidence bundle for narration

- [ ] **S14-003** · Planned · Evidence-linked trend/pattern/volume/conflict explanations

- [ ] **S14-004** · Planned · Exact-number and unsupported-claim checks on generated text

- [ ] **S14-005** · Planned · No fabricated levels, probabilities, sources or recommendations

- [ ] **S14-006** · Planned · Prompt-injection defense for uploaded content

- [ ] **S14-007** · Planned · Streaming, error handling, timeouts and cost/token budgets

- [ ] **S14-008** · Planned · Deterministic report fallback without paid API access

- [ ] **S14-009** · Planned · Questions answered from a specific immutable analysis run

- [ ] **S14-010** · Planned · Report evaluation set for factual faithfulness and uncertainty


## S15 · Research dashboard, reports and history

Original brief: 13.3,14,15,21

**Learn:** Read an analysis as evidence, conflict, conditional action and invalidation; navigate help at the point of use.

**Acceptance gate:** Charts/report/history share immutable run IDs; accessibility, export consistency, permissions and reference-data provenance are checked.

- [ ] **S15-001** · Planned · Company/ticker/exchange/timeframe/period controls

- [ ] **S15-002** · Planned · Configurable indicators and overlay visibility

- [ ] **S15-003** · Planned · Technical report covering trend, zones, patterns, momentum and volume

- [ ] **S15-004** · Planned · Explicit bullish/bearish/conflicting evidence and invalidation

- [ ] **S15-005** · Planned · Structured strategy table with all planned parameters

- [ ] **S15-006** · Partial · Pattern Research Lab and backtest configuration UI

- [ ] **S15-007** · Planned · Saved analysis history and realized-outcome comparison

- [ ] **S15-008** · Planned · Clickable chart annotations synchronized with report evidence

- [ ] **S15-009** · Planned · Downloadable readable HTML/PDF report alongside JSON/CSV

- [ ] **S15-010** · Planned · Contextual glossary links/tooltips for every financial term

- [ ] **S15-011** · Planned · Keyboard accessibility, color-safe encoding and responsive layouts

- [ ] **S15-012** · Planned · Currency/precision/units and local-time explanations

- [x] **S15-013** · Done · Two-stock CSV/NSE comparison, matched-interval correlations and side-by-side analysis

- [x] **S15-014** · Done · Bound displayed chart geometry to the observed period while preserving complete evidence

- [x] **S15-015** · Done · Retain one immutable baseline session result, mark changed calculation inputs stale and preserve its exports

- [x] **S15-016** · Done · Show replay-aware data readiness, recovery counts and actual displayed observation counts

- [x] **S15-017** · Done · Connect task navigation, selected observations, outcome studies, baseline lab and direct concept references


## S16 · Prospective paper trading

Original brief: 16.4,19 phase5

**Learn:** Distinguish a signal recorded in advance from a retrospectively selected winning chart.

**Acceptance gate:** Append-only proposed/triggered/expired/invalidated/closed events track paper fills, outcomes, drift and comparison to backtests.

- [ ] **S16-001** · Planned · Record each proposed paper setup before its outcome exists

- [ ] **S16-002** · Planned · Entry pending/triggered/not-filled/expired states

- [ ] **S16-003** · Planned · Setup invalidation and stop/target/time exit states

- [ ] **S16-004** · Planned · Append-only paper ledger and timestamped provenance

- [ ] **S16-005** · Planned · Scheduled outcome tracking and data freshness checks

- [ ] **S16-006** · Planned · Prospective returns, calibration and execution comparisons

- [ ] **S16-007** · Planned · Paper alerts/watchlists with opt-in notification rules

- [ ] **S16-008** · Planned · Post-trade review and learner trade journal

- [ ] **S16-009** · Planned · No live broker orders in this research phase


## S17 · Provider adapters and intraday expansion

Original brief: 4.2,4.3,7.4,8,19 phase5

**Learn:** Learn API limits, credentials, sessions/timezones, same-time-of-day volume and partial bars.

**Acceptance gate:** Chosen licensed adapter has integration fixtures, retries, rate-limit behavior, session/calendar handling and no credential leakage.

- [ ] **S17-001** · Planned · Evaluate Zerodha Kite Connect data adapter and current permissions

- [ ] **S17-002** · Planned · Evaluate Upstox historical-data adapter

- [ ] **S17-003** · Planned · Evaluate DhanHQ historical-data adapter

- [ ] **S17-004** · Planned · Evaluate other licensed data providers against coverage and adjustment needs

- [ ] **S17-005** · Planned · Secure credential configuration and expiration handling

- [ ] **S17-006** · Planned · Incremental data updates, local cache and provider rate limits

- [ ] **S17-007** · Planned · Intraday timezone and exchange-session boundaries

- [ ] **S17-008** · Planned · Same-time-of-day volume and incomplete-current-bar exclusion

- [ ] **S17-009** · Planned · Spread, auction, circuit and suspension behavior

- [ ] **S17-010** · Planned · Integration fixtures and graceful unavailable-provider behavior


## S18 · Engineering, security and operation

Original brief: 17,18,20,21,22

**Learn:** Understand modular interfaces, reproducibility, migrations, tests, deployment and operational failure modes.

**Acceptance gate:** Fresh install, CI, migrations/backups, input validation, observability, secrets policy and rollback work in the intended environment.

- [ ] **S18-001** · Planned · Clear typed interfaces between acquisition, analysis, strategies and narration

- [ ] **S18-002** · Planned · Configuration validation and dependency/version policy

- [x] **S18-003** · Done · Continuous integration on clean Python installs

- [ ] **S18-004** · Planned · Numerical regression fixtures and leakage/property tests

- [ ] **S18-005** · Planned · Upload parsing limits and spreadsheet/image resource safeguards

- [ ] **S18-006** · Planned · Secrets scanning and sanitized diagnostic logs

- [ ] **S18-007** · Planned · User authentication/authorization before any multi-user deployment

- [ ] **S18-008** · Planned · Data/analysis storage retention, export and deletion policy

- [ ] **S18-009** · Planned · Database migrations, backups and restore drill

- [ ] **S18-010** · Planned · Structured run IDs, logs, errors and performance monitoring

- [ ] **S18-011** · Planned · Reproducible packaging and separate development/production configuration

- [ ] **S18-012** · Planned · Deployment, health checks and rollback procedure

- [ ] **S18-013** · Planned · Cache invalidation tied to data and engine versions

- [ ] **S18-014** · Planned · Dataset/model documentation and experiment reports

- [ ] **S18-015** · Planned · License selection before public distribution; preserve source attribution

- [ ] **S18-016** · Planned · Release checklist and user-facing limitations


## S19 · Optional research extensions

Original brief: Extensions beyond original brief

**Learn:** Ask what additional evidence an extension contributes and pre-register a falsifiable hypothesis.

**Acceptance gate:** Only pursue after core gates; each extension gets data rights, an experiment protocol, benchmark, cost estimate and a separate evaluation.

- [ ] **S19-001** · Optional / later · Relative strength versus sector/index (distinct from RSI)

- [ ] **S19-002** · Optional / later · Cross-sectional momentum and breadth research

- [ ] **S19-003** · Optional / later · Fundamental/event overlays from licensed point-in-time sources

- [ ] **S19-004** · Optional / later · Portfolio construction and volatility targeting

- [ ] **S19-005** · Optional / later · Regime classifiers and change-point detection

- [ ] **S19-006** · Optional / later · Transaction-cost and capacity estimation by liquidity bucket

- [ ] **S19-007** · Optional / later · Anchored VWAP and volume-profile research with suitable data

- [ ] **S19-008** · Optional / later · Benchmark-independent ablation studies for every added feature

- [ ] **S19-009** · Optional / later · Exportable strategy rule specifications and independent replay

- [ ] **S19-010** · Optional / later · Community lesson contributions with numerical/source review

- [ ] **S19-011** · Optional / later · Derivatives/options analytics as a separately scoped education/research project

- [ ] **S19-012** · Optional / later · Live execution only after a separate explicit scope, controls and authorization


## S20 · Learner practice and release review

Original brief: Learning request + 20,21,22

**Learn:** Explain and reproduce the work independently; distinguish software completion from profitable trading.

**Acceptance gate:** Worked exercises, misconception checks, release evidence and the learner's own explanation are recorded; never mark learner mastery automatically.

- [ ] **S20-001** · Planned · Explain OHLCV, bodies/wicks and daily versus weekly bars in your own words

- [ ] **S20-002** · Planned · Hand-calculate SMA, one EMA update and true range

- [ ] **S20-003** · Planned · Hand-calculate RSI and explain why it is not a success probability

- [ ] **S20-004** · Planned · Explain MACD line, signal line and histogram with a numerical example

- [ ] **S20-005** · Planned · Identify Evening Star context and contrast shape with confirmation

- [ ] **S20-006** · Planned · Replay a pivot and explain its confirmation delay

- [ ] **S20-007** · Planned · Calculate position quantity, cash exposure and cost-aware risk

- [ ] **S20-008** · Planned · Explain gaps, ambiguity and why planned risk is not maximum loss

- [ ] **S20-009** · Planned · Read a trade ledger and recompute net P&L and drawdown

- [ ] **S20-010** · Planned · Design a falsifiable strategy and name its benchmark

- [ ] **S20-011** · Planned · Find an example of leakage, survivorship bias and multiple testing

- [ ] **S20-012** · Planned · Reproduce a run from its dataset/settings/code record

- [ ] **S20-013** · Planned · Review every original acceptance criterion with evidence before final-product claim

- [ ] **S20-014** · Planned · Write a learner retrospective and decide the next small experiment


## Original acceptance criteria audit (brief §21)

1–4 upload/validation/chart/principal starter indicators: implemented for daily files.

5–7 structure/zones/candle starter set: implemented with limited definitions; context/extensions remain above.

8 basic double patterns plus initial triangle/rectangle geometry: prototype; head-and-shoulders and further contextual/statistical validation remain pending.

9 detection coordinates/status: implemented for supported events; universal schema pending.

10 multiple timeframes: partial (daily plus conservative prior-week context).

11–14 coherent report/conditional plan/risk math/annotations: implemented for the single baseline; broader catalogue pending.

15 insufficient data: implemented starter behavior; calendar/provider completeness pending.

16 no future information: starter numerical/event/execution tests pass; every future module must pass independently.

17 local launch: documented and tested on the development environment; clean remote CI is separate.

18 analytical/financial tests: present; coverage expands with each module.
