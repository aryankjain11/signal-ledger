"""Shared master checklist. Status means implementation evidence, not learning mastery."""

STATUS_LABELS = {"done": "Done", "partial": "Partial", "planned": "Planned", "optional": "Optional / later"}

STAGES = [
    ("S00", "Learning foundation and version control", "1,17,20,22 + learning request",
     "Distinguish concepts, calculations, strategies and evidence. Learn files, tests, commits and documentation.",
     "Shared catalogue renders in app and handbook; navigation/search/examples pass tests; repository content is verified."),
    ("S01", "Audit the current daily-data prototype", "3,4,7,14,16,21",
     "Read an OHLCV candle, a causal indicator and a sequential trade ledger.",
     "Reproduce numerical fixtures and documented assumptions; supported upload/replay/report flows pass."),
    ("S02", "Reliable Indian equity data", "4,16,20",
     "Understand session dates, adjustments, data licensing, missingness and survivorship.",
     "Versioned source and adjustment metadata; calendar/corporate-action fixtures; no invented observations; provider failures handled."),
    ("S03", "Price structure, zones and breakouts", "5.1,5.2,5.3",
     "Explain HH/HL/LH/LL, pivot delay, support/resistance, breakouts and failed setups.",
     "Explicit configurable rules, positive/negative examples, formation/detection timestamps, no future-append changes."),
    ("S04", "Chart-pattern catalogue", "5.4,13,21",
     "Translate visual descriptions into geometry, tolerances and state transitions; geometry is not profitability.",
     "Each named detector has mathematical rules, positive/negative fixtures, coordinates, state lifecycle, annotations and education."),
    ("S05", "Candlestick catalogue and context", "6,13,21",
     "Understand bodies, shadows, gaps, preceding trend and the difference between shape and actionable evidence.",
     "Each named detector has OHLC geometry tests, context/gap rules, known-time markers, conflicts and a lesson; no reliability claims without research."),
    ("S06", "Configurable indicators and interpretation", "7",
     "Compare trend, momentum, volatility and volume; understand seeds, warm-up and correlated evidence.",
     "Each indicator matches independent fixtures, defines parameters/seeds/warm-up, stays causal and has interpretation plus limitations."),
    ("S07", "Multi-timeframe analysis", "4.2,8",
     "Aggregate OHLCV correctly and distinguish completed higher-timeframe context from a developing bar.",
     "Session-aware aggregation, complete-bar availability and causal cross-timeframe joins are tested; unavailable context stays unavailable."),
    ("S08", "Conditional strategy catalogue", "11",
     "A strategy needs an exact trigger, legal instrument, order assumption, invalidation, exits and expiry.",
     "Every strategy has a versioned rule specification, deterministic signals, next-action timing, no-trade reasons, replay and cost-aware tests."),
    ("S09", "Risk, position sizing and evidence scores", "11.2,11.3,11.4,12",
     "Separate monetary risk, volatility, setup quality and calibrated probability.",
     "Costs, price increments, gaps and capital constraints are tested; score components trace to evidence; probabilities require validation."),
    ("S10", "Backtesting and validation protocol", "16,21",
     "Learn execution chronology, mark-to-market returns, drawdown, baselines and overfitting.",
     "A frozen chronological protocol, realistic execution and comparable benchmarks produce reproducible ledgers and metrics with uncertainty."),
    ("S11", "Historical pattern research database", "9,14D,14F,17",
     "Define an occurrence, comparable population, outcome horizon and independent sample.",
     "Versioned events/features/outcomes persist, censoring/overlap is handled, and research summaries disclose cohort, dates and sample size."),
    ("S12", "Probability models and machine learning", "10,12.3",
     "Learn labels, features, temporal leakage, base rates, calibration and economic utility.",
     "Predefined target/stop/horizon, purged chronological evaluation, baseline comparison, calibration diagnostics and held-out after-cost results."),
    ("S13", "Screenshot observations and annotations", "2,13",
     "Learn why visible shape or pixel position is not exact OHLCV, time or a tradable fill.",
     "Image-only observations are explicitly qualitative, uncertainty/axis limits are disclosed and structured data wins numerical conflicts."),
    ("S14", "Evidence-bound AI interpretation", "3,15,20",
     "Use a language model to communicate verified facts without letting it invent calculations or probabilities.",
     "Provider-neutral narration has evidence references, factual/number checks, deterministic fallback, cost limits and prompt-injection tests."),
    ("S15", "Research dashboard, reports and history", "13.3,14,15,21",
     "Read an analysis as evidence, conflict, conditional action and invalidation; navigate help at the point of use.",
     "Charts/report/history share immutable run IDs; accessibility, export consistency, permissions and reference-data provenance are checked."),
    ("S16", "Prospective paper trading", "16.4,19 phase5",
     "Distinguish a signal recorded in advance from a retrospectively selected winning chart.",
     "Append-only proposed/triggered/expired/invalidated/closed events track paper fills, outcomes, drift and comparison to backtests."),
    ("S17", "Provider adapters and intraday expansion", "4.2,4.3,7.4,8,19 phase5",
     "Learn API limits, credentials, sessions/timezones, same-time-of-day volume and partial bars.",
     "Chosen licensed adapter has integration fixtures, retries, rate-limit behavior, session/calendar handling and no credential leakage."),
    ("S18", "Engineering, security and operation", "17,18,20,21,22",
     "Understand modular interfaces, reproducibility, migrations, tests, deployment and operational failure modes.",
     "Fresh install, CI, migrations/backups, input validation, observability, secrets policy and rollback work in the intended environment."),
    ("S19", "Optional research extensions", "Extensions beyond original brief",
     "Ask what additional evidence an extension contributes and pre-register a falsifiable hypothesis.",
     "Only pursue after core gates; each extension gets data rights, an experiment protocol, benchmark, cost estimate and a separate evaluation."),
    ("S20", "Learner practice and release review", "Learning request + 20,21,22",
     "Explain and reproduce the work independently; distinguish software completion from profitable trading.",
     "Worked exercises, misconception checks, release evidence and the learner's own explanation are recorded; never mark learner mastery automatically."),
]

TASKS = []


def _add(stage, lines):
    """Prefix + = done, ~ = partial, ? = optional; all other tasks are planned."""
    for number, line in enumerate(lines.strip().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        status = {"+": "done", "~": "partial", "?": "optional"}.get(line[0], "planned")
        title = line[1:].strip() if line[0] in "+~?" else line
        TASKS.append({"id": f"{stage}-{number:03}", "stage": stage, "title": title, "status": status})


_add("S00", """
+ Preserve original brief and refined first-build plan
+ Establish continuing AGENTS.md learning and logging agreement
+ Create master checklist with statuses, dependencies and acceptance gates
+ Add searchable Education and Concepts page independent of uploads
+ Export shared concept handbook and master checklist
+ Add original worked examples, learning labs and misconception checks
+ Add detailed build report and chronological work log
+ Add first lesson: from OHLCV to a falsifiable strategy
+ Create private GitHub repository
+ Upload reviewed source, synthetic data, tests and documents; verify remote tree
+ Add automated test workflow; distinguish local pass from remote CI pass
Record learner questions and exercises without claiming mastery
""")
_add("S01", """
+ Local Streamlit application and documented launch instructions
+ CSV and XLSX ingestion for one daily symbol
+ Strict OHLCV/date/duplicate/missing/nonfinite validation
+ Source hash and adjustment declaration
+ SMA20/50/200 and EMA20/50 numerical calculations
+ Wilder RSI14 and ATR14 numerical calculations
+ MACD12/26/9, Bollinger20, OBV and prior-session relative volume
+ Confirmed swings with formation and detection dates
+ Basic HH/HL and LH/LL market structure
+ As-of pivot-cluster support/resistance zones
+ Doji and bullish/bearish engulfing geometric observations
+ Double-top/bottom geometric event lifecycle
+ Completed prior-week SMA20 context
+ As-of historical replay and consistent chart annotations
+ One conditional long breakout plan and cost-aware whole-share sizing
+ Sequential breakout backtest with fees, slippage, gap and ambiguity rules
+ Download report, indicators, evidence and trade/equity record
+ Baseline numerical and application test suite
""")
_add("S02", """
~ Choose and document licensed Indian historical-data source and permitted uses
~ Provider-neutral daily data contract and symbol/company-name resolver
~ NSE/BSE identifiers, symbol changes, mergers and delistings
Exchange trading calendar, holidays and exceptional sessions
+ Asia/Kolkata timestamps and explicit session-date semantics
Detect genuinely missing sessions against the configured calendar
Consistent split/bonus adjustment across OHLC and volume
Dividend/total-return conventions and point-in-time adjustment policy
Rights/demerger/merger action handling and ambiguous-action review queue
~ Preserve original raw files plus normalized versioned datasets
Cross-source data checks, stale-feed detection and source timestamps
~ Duplicate correction policy with a visible audit record
Outlier, zero-volume, price-circuit and suspension flags
Adjusted-close, VWAP, number-of-trades and spread optional schema
Delivery volume and delivery percentage where licensed/available
Market-index and sector-index context
Point-in-time index constituents to reduce survivorship bias
Provider outage/rate-limit/retry/error behavior
~ Data completeness/freshness dashboard and adjustment-quality gates
+ No interpolation/fabrication; clearly report unavailable fields
""")
_add("S03", """
Configurable swing significance, tie handling and volatility-aware filtering
Trend strength, consolidation, sideways and possible-reversal classifications
Swing-based structure breaks with explicit confirmation time
Horizontal zones with rejection strength, interactions and age
Dynamic moving-average support/resistance
Previous session/week highs and lows
Psychological levels with explicit price-increment convention
Volume-near-level significance without inventing order flow
Support/resistance role reversals
Bullish breakout and bearish breakdown states
Volume/distance/closing-position breakout confirmation
Failed breakout and false breakdown event tracking
Retests and breakout-retest conditions
Trendlines/channels with stable causal anchors
Conflicting and insufficient-evidence explanations
""")
_add("S04", """
~ Double bottom: contextual significance and research validation
~ Double top: contextual significance and research validation
Triple bottom
Triple top
Head and shoulders
Inverse head and shoulders
Rounding bottom
Rounding top
Broadening formations
Bullish flag
Bearish flag
Bullish pennant
Bearish pennant
Ascending triangle
Descending triangle
Symmetrical triangle
Rising wedge
Falling wedge
Rectangle consolidation
Price channels
Cup and handle
Inverse cup and handle
Breakout retest formation
Bullish divergence
Bearish divergence
Higher-high/higher-low and lower-high/lower-low sequence patterns
Developing/confirmed/invalidated/inconclusive/expired pattern lifecycle standard
Pattern boundary/neckline/anchor coordinates and clickable evidence
Configurable tolerances, geometric-fit diagnostics and versioned definitions
""")
_add("S05", """
~ Doji with preceding-trend and support/resistance context
Dragonfly doji
Gravestone doji
Long-legged doji
Hammer
Hanging man
Inverted hammer
Shooting star
Bullish marubozu
Bearish marubozu
Spinning top
~ Bullish engulfing with context and historical evaluation
~ Bearish engulfing with context and historical evaluation
Piercing pattern
Dark cloud cover
Bullish harami
Bearish harami
Tweezer bottom
Tweezer top
Bullish kicking
Bearish kicking
Morning star
Evening star
Morning doji star
Evening doji star
Three white soldiers
Three black crows
Three inside up
Three inside down
Three outside up
Three outside down
Configurable body/wick/gap/trend definitions for each candle family
Volume confirmation, supporting/conflicting indicators and strength evidence
Reference-library comparison (evaluate TA-Lib installation/definitions)
Do not convert every recognized candle into a trading signal
""")
_add("S06", """
Configurable SMA/EMA/WMA periods including 9/20/50/100/200
Configurable MACD periods and histogram interpretation
ADX and directional movement
Parabolic SAR
Supertrend
Configurable Wilder RSI and flat-series conventions
Stochastic oscillator
Stochastic RSI
Rate of change
Williams %R
Commodity Channel Index
Configurable ATR and percentage-ATR
Configurable Bollinger bands and bandwidth
Return standard deviation and annualization assumptions
Historical volatility
Donchian channels
Keltner channels
Volatility expansion, contraction and squeeze states
Configurable OBV and slope interpretation
Session-anchored VWAP
Accumulation/distribution line
Chaikin money flow
Money flow index
Relative volume and rolling volume baselines
Same-time-of-day intraday relative volume
Price-volume and price-momentum divergence rules
Momentum acceleration and deterioration
Buying/selling-pressure proxies with explicit limitations
Avoid double-counting correlated indicators in aggregate scores
Explain reinforcing versus contradictory evidence by indicator family
""")
_add("S07", """
Daily/weekly/monthly aggregation and explicit partial-period policy
1-minute, 5-minute, 15-minute and 30-minute data support
1-hour and session-aware 4-hour bars where appropriate
Never upsample coarse observations into fabricated finer candles
Top-down weekly/daily/hourly/entry-timeframe workflow
Availability-time joins to prevent higher-timeframe leakage
Alignment and contradiction summaries across timeframes
Cross-timeframe support/resistance confluence
Insufficient-history labels per timeframe and indicator
Boundary, holiday, session-anchor and early-close aggregation tests
""")
_add("S08", """
Versioned strategy specification and parameter registry
Long breakout strategy research validation beyond prototype
Short/breakdown strategies only for legally supported instruments
Breakout-retest strategy
Reversal strategies tied to confirmed structures
Pullback-entry strategy
Momentum and trend-following strategies
Market, limit, breakout and pullback order semantics
Entry ranges, expiry and cancellation conditions
Market/sector and multi-timeframe confirmation
Multiple profit targets and partial exit rules
Explicit no-trade decisions and avoid-trade conditions
Intraday/swing/positional holding-style distinction
Structured plan with trigger, invalidation, horizon and evidence
""")
_add("S09", """
Swing/zone/ATR/pattern-invalidation stop methods
Measured-move, prior-level and ATR target methods
Fibonacci extensions as explicitly unvalidated hypotheses
Gap-aware portfolio stress tests and maximum-loss caveats
Tick-size and instrument lot-size constraints
Exchange/broker/order-specific asymmetric costs and taxes
Cash/settlement/buying-power and concentration constraints
Liquidity/spread/participation and fill uncertainty
Portfolio open risk, correlated exposure and sector caps
Separate geometric pattern quality, trend evidence and trading probability
Transparent risk classification with defined criteria
Unfavorable net reward/risk and nearby obstacle vetoes
Event/earnings/corporate-action risk flags with source timestamps
Never display arbitrary confidence percentages as probabilities
""")
_add("S10", """
Freeze chronological development, validation and untouched test periods
Version/hash every experiment's data, parameters and code
Benchmark cash, exposure-matched buy-and-hold and simple rules
Detailed fees, taxes, spread, slippage and market-impact model
Gap-through orders and stop/target same-bar ambiguity tests
Limit-order non-fills, partial fills and trading restrictions
Multiple targets, trailing stops and partial exits
End-of-data, event expiry and censored/open-position conventions
Net total return and annualized return with elapsed-time conventions
Historical win rate and average winner/loser
Profit factor, expectancy and sample-size uncertainty
Marked equity and maximum drawdown/drawdown duration
Sharpe and Sortino with return interval/risk-free assumptions
Calmar ratio and average holding period
Regime/timeframe/stock/sector breakdowns
Walk-forward research and overlapping-label treatment
Parameter robustness, sensitivity and regime stability tests
Multiple-testing/selection-bias and experiment-count disclosure
Block-bootstrap/Monte Carlo stress tests with dependent observations
Prospective-versus-historical result comparison
Evaluate Backtesting.py and VectorBT against execution requirements
""")
_add("S11", """
SQLite schema and migrations with PostgreSQL-compatible interfaces
Persist symbols, versioned OHLCV and data provenance
Immutable analysis runs and parameter/engine versions
Occurrence records with market/timeframe/definition/known-time/features
Target-before-stop labels with fixed horizon and ambiguity policy
Successful/failed/expired/censored occurrence counts
MFE/MAE and average favorable/adverse movement
Time-to-target and holding-time distributions
Conditional pattern cohorts and feature combinations
Market-regime and timeframe performance slices
Non-overlapping samples, uncertainty and small-sample warnings
Research-lab filters by symbol, date, regime, subtype and context
No historical-performance display without an auditable cohort
""")
_add("S12", """
Point-in-time feature store for returns, indicators and market context
Predefine target, stop and horizon before creating labels
Up/down/horizon return and target-before-stop research objectives
Logistic-regression and unconditional-frequency baselines
Random forest comparison
XGBoost and LightGBM evaluation if justified
Chronological train/validation/test split
Purging and embargo for overlapping event labels
Feature scaling, missingness and selection fitted on training only
Precision, recall, F1, ROC-AUC and PR-AUC
Brier score, log loss and reliability/calibration diagrams
Probability calibration and confidence/uncertainty intervals
Subgroup/regime and out-of-distribution checks
Expected after-cost utility versus classification accuracy
Model registry, reproducibility, drift and retraining gates
Do not add deep learning without evidence simpler models are inadequate
""")
_add("S13", """
Screenshot upload and chart-type recognition
Visible stock/timeframe/axis-label extraction with uncertainty
Cropping, resolution, distortion and missing-axis quality checks
Qualitative support/resistance/trendline observations
Visible candle/pattern/breakout candidates with approximate anchors
Green support, red resistance, blue boundaries and yellow candle annotations
Swing circles, directional arrows and consolidation highlights
Entry/stop/target overlays only when defensible and clearly conditional
Clickable annotations with known-time and evidence details
Strict image-only versus structured-data mode distinction
Structured-data reconciliation; never invent exact screenshot OHLCV
""")
_add("S14", """
Provider-independent LLM interface and environment-based credentials
Schema-validated numerical evidence bundle for narration
Evidence-linked trend/pattern/volume/conflict explanations
Exact-number and unsupported-claim checks on generated text
No fabricated levels, probabilities, sources or recommendations
Prompt-injection defense for uploaded content
Streaming, error handling, timeouts and cost/token budgets
Deterministic report fallback without paid API access
Questions answered from a specific immutable analysis run
Report evaluation set for factual faithfulness and uncertainty
""")
_add("S15", """
Company/ticker/exchange/timeframe/period controls
Configurable indicators and overlay visibility
Technical report covering trend, zones, patterns, momentum and volume
Explicit bullish/bearish/conflicting evidence and invalidation
Structured strategy table with all planned parameters
Pattern Research Lab and backtest configuration UI
Saved analysis history and realized-outcome comparison
Clickable chart annotations synchronized with report evidence
Downloadable readable HTML/PDF report alongside JSON/CSV
Contextual glossary links/tooltips for every financial term
Keyboard accessibility, color-safe encoding and responsive layouts
Currency/precision/units and local-time explanations
""")
_add("S16", """
Record each proposed paper setup before its outcome exists
Entry pending/triggered/not-filled/expired states
Setup invalidation and stop/target/time exit states
Append-only paper ledger and timestamped provenance
Scheduled outcome tracking and data freshness checks
Prospective returns, calibration and execution comparisons
Paper alerts/watchlists with opt-in notification rules
Post-trade review and learner trade journal
No live broker orders in this research phase
""")
_add("S17", """
Evaluate Zerodha Kite Connect data adapter and current permissions
Evaluate Upstox historical-data adapter
Evaluate DhanHQ historical-data adapter
Evaluate other licensed data providers against coverage and adjustment needs
Secure credential configuration and expiration handling
Incremental data updates, local cache and provider rate limits
Intraday timezone and exchange-session boundaries
Same-time-of-day volume and incomplete-current-bar exclusion
Spread, auction, circuit and suspension behavior
Integration fixtures and graceful unavailable-provider behavior
""")
_add("S18", """
Clear typed interfaces between acquisition, analysis, strategies and narration
Configuration validation and dependency/version policy
+ Continuous integration on clean Python installs
Numerical regression fixtures and leakage/property tests
Upload parsing limits and spreadsheet/image resource safeguards
Secrets scanning and sanitized diagnostic logs
User authentication/authorization before any multi-user deployment
Data/analysis storage retention, export and deletion policy
Database migrations, backups and restore drill
Structured run IDs, logs, errors and performance monitoring
Reproducible packaging and separate development/production configuration
Deployment, health checks and rollback procedure
Cache invalidation tied to data and engine versions
Dataset/model documentation and experiment reports
License selection before public distribution; preserve source attribution
Release checklist and user-facing limitations
""")
_add("S19", """
? Relative strength versus sector/index (distinct from RSI)
? Cross-sectional momentum and breadth research
? Fundamental/event overlays from licensed point-in-time sources
? Portfolio construction and volatility targeting
? Regime classifiers and change-point detection
? Transaction-cost and capacity estimation by liquidity bucket
? Anchored VWAP and volume-profile research with suitable data
? Benchmark-independent ablation studies for every added feature
? Exportable strategy rule specifications and independent replay
? Community lesson contributions with numerical/source review
? Derivatives/options analytics as a separately scoped education/research project
? Live execution only after a separate explicit scope, controls and authorization
""")
_add("S20", """
Explain OHLCV, bodies/wicks and daily versus weekly bars in your own words
Hand-calculate SMA, one EMA update and true range
Hand-calculate RSI and explain why it is not a success probability
Explain MACD line, signal line and histogram with a numerical example
Identify Evening Star context and contrast shape with confirmation
Replay a pivot and explain its confirmation delay
Calculate position quantity, cash exposure and cost-aware risk
Explain gaps, ambiguity and why planned risk is not maximum loss
Read a trade ledger and recompute net P&L and drawdown
Design a falsifiable strategy and name its benchmark
Find an example of leakage, survivorship bias and multiple testing
Reproduce a run from its dataset/settings/code record
Review every original acceptance criterion with evidence before final-product claim
Write a learner retrospective and decide the next small experiment
""")

STAGE_BY_ID = {s[0]: {"id": s[0], "title": s[1], "brief": s[2], "learn": s[3], "gate": s[4]} for s in STAGES}


def checklist_markdown():
    counts = {state: sum(t["status"] == state for t in TASKS) for state in STATUS_LABELS}
    lines = ["# Master implementation and learning checklist", "Updated: 2026-11-03",
             "Source of truth: `learning/roadmap.py`. Regenerate with `python scripts/export_learning_docs.py`.",
             f"{len(TASKS)} work items: " + ", ".join(f"{counts[s]} {STATUS_LABELS[s].lower()}" for s in counts) + ".",
             "Done means the named software gate is evidenced; it does not mean profitable trading or learner mastery. Partial items intentionally remain unchecked. Optional extensions are outside the core completion gate.",
             "Work order: S00/S01 → S02 → S03/S06 → S04/S05 → S07 → S08/S09 → S10 → S11 → S12. S13/S14 follow reliable evidence; S15/S18 continue across stages; S16 follows frozen rules. S17 intraday is a separate expansion. S19 requires a new hypothesis. S20 exercises accompany each stage.",
             "Every new detector/indicator/strategy also needs a concept explanation, hypothetical example, misconception warning, source, numerical/negative tests, time-availability checks, UI evidence and log entry.",
             "The full original requirements remain in `docs/ORIGINAL_BRIEF.md`; original section references below make coverage traceable."]
    for stage_id, meta in STAGE_BY_ID.items():
        lines += [f"\n## {stage_id} · {meta['title']}", f"Original brief: {meta['brief']}",
                  f"**Learn:** {meta['learn']}", f"**Acceptance gate:** {meta['gate']}"]
        lines += [f"- [{'x' if t['status'] == 'done' else ' '}] **{t['id']}** · {STATUS_LABELS[t['status']]} · {t['title']}"
                  for t in TASKS if t["stage"] == stage_id]
    lines += ["\n## Original acceptance criteria audit (brief §21)",
              "1–4 upload/validation/chart/principal starter indicators: implemented for daily files.",
              "5–7 structure/zones/candle starter set: implemented with limited definitions; context/extensions remain above.",
              "8 basic double patterns: prototype; triangles and head-and-shoulders remain pending.",
              "9 detection coordinates/status: implemented for supported events; universal schema pending.",
              "10 multiple timeframes: partial (daily plus conservative prior-week context).",
              "11–14 coherent report/conditional plan/risk math/annotations: implemented for the single baseline; broader catalogue pending.",
              "15 insufficient data: implemented starter behavior; calendar/provider completeness pending.",
              "16 no future information: starter numerical/event/execution tests pass; every future module must pass independently.",
              "17 local launch: documented and tested on the development environment; clean remote CI is separate.",
              "18 analytical/financial tests: present; coverage expands with each module."]
    return "\n\n".join(lines) + "\n"
