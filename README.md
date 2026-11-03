# Signal Ledger

A local quantitative technical-research workbench for **Indian stocks and swing
trading**. This starting build turns a daily OHLCV file into traceable structure,
an annotated chart, a deterministic report and one explicit strategy experiment.
It does not claim a demonstrated trading edge.

## Learn while building

Use the sidebar **Workspace** menu to switch between the research dashboard,
**Education and Concepts**, and **Build checklist & log**. Learning pages work
without an upload. Start with Lesson 1, then try the RSI, position-sizing and
synthetic Evening Star labs. The concept library labels what is actually computed
or detected separately from features that are only explained.

- [Master checklist](docs/MASTER_CHECKLIST.md): 341 tracked items across 21 stages,
  covering the original brief and optional extensions with acceptance gates.
- [Education and Concepts](docs/EDUCATION_AND_CONCEPTS.md): 119 definitions and
  notes; worked examples for foundations and current features, concise entries for
  future additions.
- [Lesson 1](docs/lessons/01_from_prices_to_evidence.md): connected explanations,
  exercises, answers and pointers into the code.
- [Lesson 2](docs/lessons/02_daily_data_and_passports.md): daily reports, security
  identity, session dates, adjustments, hashes and a hands-on import walkthrough.
- [Work log](docs/WORK_LOG.md): chronological changes, reasons, verification and blockers.
- [Build report](docs/BUILD_REPORT.md): architecture, curriculum and current limits.

Each future increment follows learn → specify → build → verify → explain → record.
The continuing agreement is in [AGENTS.md](AGENTS.md). Understanding is not
automatically checked off for the learner.

The private repository is [aryankjain11/signal-ledger](https://github.com/aryankjain11/signal-ledger).
The source, tests, synthetic sample and learning documents have been uploaded and
verified for the learning foundation. See
[GitHub sync status](docs/GITHUB_SYNC.md) for the verified commit and Actions run.
The local computer's Git client does not currently have a saved GitHub login;
the connected GitHub tools handle this upload, and no credentials are stored here.

## Open the app

This workspace has a prepared `.venv`. Double-click **Start App.cmd**, or run:

```powershell
cd 'C:\Users\aryan\OneDrive\Documents\ChatGPT\Projects to Build\quant-research-engine'
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Visit http://127.0.0.1:8501. The server binds only to your computer. Stop it with
Ctrl+C in its terminal. No API key, broker account or paid AI service is needed.
The walkthrough uses clearly labelled synthetic observations, not market data.

## Fresh setup

Use Python 3.13 (tested with 3.13.7):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If Python's bundled pip setup is unavailable, use an existing pip to provision the
environment without changing system packages:

```powershell
python -m venv --without-pip .venv
python -m pip --python .venv\Scripts\python.exe install -r requirements-dev.txt
```

## Try your own data

1. Select **Upload daily data** and choose a CSV or XLSX file containing one stock.
2. Enter its label. Labels do not fetch data. Supply INR prices; no currency
   conversion is performed. No automated NSE/BSE data feed is integrated yet.
3. Declare whether all OHLC prices use a consistent corporate-action adjustment
   basis. The app cannot verify this declaration or repair corporate actions.
4. Confirm every row is a completed daily candle. Intraday timestamps are rejected.
5. Enter capital, risk budget, and estimated per-side charges/slippage. The default
   numbers are illustrative inputs, not an Indian tax or brokerage schedule.
6. Inspect the chart, evidence and limitations. Move the replay slider to see only
   what was observable by a selected date. Run the exploratory backtest separately.
7. Download the report, feature table, analysis evidence and backtest record.

Required columns (case insensitive):

```csv
date,open,high,low,close,volume
2024-01-01,100,102,99,101,100000
2024-01-02,101,103,100,102,110000
2024-01-03,102,104,101,103,105000
```

CSV dates must be YYYY-MM-DD. Native Excel date cells are accepted. Missing values,
duplicate dates, mixed symbols, infinite/negative values and impossible OHLC
relationships fail validation. Rows may be sorted with a visible warning. No
prices are forward-filled or fabricated. Only the first XLSX worksheet is read.
Maximum size: 20 MB and 50,000 sessions. Use at least 60 sessions for the baseline
and 20 completed prior calendar weeks for weekly SMA context.

## Implemented

- Offline NSE CM UDiFF-style CSV/ZIP import preview for one selected EQ security
  across daily reports; source/date/identity/duplicate guards and bounded ZIP reading.
- Synthetic 80-report walkthrough with two fake securities; no real market data.
- Provider-neutral data passport, original-file hashes, source versus replay-slice
  fingerprints, JSON passport and analyzed-CSV downloads. Provenance records claims;
  it does not independently authenticate origin or verify adjustment/usage rights.
- Lesson 2 in Education → Start here. See [S02-A scope](docs/S02_DATA_IMPORT.md)
  for acceptance and remaining real-file, calendar and corporate-action work.

- SMA20/50/200, EMA20/50, Wilder RSI14 and ATR14, MACD12/26/9, Bollinger20
  (population standard deviation), OBV and prior-20-session relative volume.
- Confirmed three-session-left/right pivots with distinct formation and detection
  dates; HH/HL and LH/LL structure; nearby pivot clusters as approximate zones.
- Doji and bullish/bearish engulfing geometry. Double tops/bottoms have explicit
  tolerances, coordinates and developing/confirmed/invalidated/expired events.
  Confirmation here means a geometric neckline close, not proven profitability.
- Completed prior-calendar-week aggregation and weekly SMA20 context. The latest
  calendar week is always excluded, even on Friday, to avoid assuming a calendar.
- One long-only 20-session breakout rule; next-open entry, a fixed-at-entry 2 ATR
  stop, 2R target and ten-session maximum hold; explicit no-trade outcome.
- Whole-share sizing capped by cash, planned stop risk and 1% of previous-session
  volume; per-side blended fees and adverse slippage; gap-through-stop handling;
  stop-first rule for ambiguous bars; liquidation-cost marked equity and drawdown.
- Chart annotations and report derived from one analysis object. Evidence JSON
  includes raw-source SHA-256, as-of date, adjustment declaration, settings, engine
  version, feature values, events and limitations. Backtest JSON adds equity and
  trades. Downloads are records; there is no persistent run database yet.

## Analytical conventions and limitations

EMA uses a first-observation recursive seed with `adjust=False` and a period-length
warm-up. RSI uses an arithmetic seed over the first 14 price changes; zero gains
and losses produce RSI50. ATR uses the first 14 true ranges, including the initial
high-low range, then Wilder recursion. Other libraries may use different seeds.

Swings are plotted at formation for visual context; their hover text and evidence
show when they became knowable. Latest support/resistance zones and market
structure are as-of summaries, not backdated trading signals. The pattern event
log preserves observation times and immutable state changes. The fixed baseline
strategy does not trade those chart patterns.

The latest-close plan is an indicative reference, not a known fill. Actual
simulation levels are recalculated from the next open including entry slippage.
Stop risk includes assumed normal stop slippage and fees, but opening gaps can
produce losses beyond the risk budget. Historical volume participation is a rough
cap, not a fill or liquidity guarantee. No partial fills, settlement, circuits,
auctions, order-book spreads, asymmetric taxes, corporate-action cash flows or
market impact are modeled. Input OHLC adjustment consistency matters.

Backtests are exploratory on the uploaded dataset. They are not walk-forward,
held-out validation or evidence of future success. The win rate is descriptive
of those completed trades, not the chance the current setup succeeds. Profit
factor is unavailable when there are no losing trades. Buy-and-hold comparison
is gross close-to-close return, not cost/exposure-matched. No calibrated
probabilities, model training, triangles, head-and-shoulders, screenshot analysis,
live feeds, paper trading, database history or order execution are implemented.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Tests cover data failure modes and CSV/XLSX parity, hand-calculated Wilder seeds,
warm-ups, future-append invariance, pivot confirmation, pattern event timing,
cost-aware sizing, execution timing, gaps, ambiguous candles, numerical exports,
chart alignment, and dashboard flows. Fixtures test software correctness; they
cannot establish real-world alpha. The synthetic fixture can be regenerated with
`python scripts/make_demo.py`.

Tests also cover concept search, honest feature labels, generated-document
consistency, learning-page navigation, worked RSI arithmetic, quiz feedback and
invalid long-position examples. Update shared content in `learning/`, then run
`python scripts/export_learning_docs.py` to refresh the two generated handbooks.
The CI workflow runs checks on pushes and pull requests; a configured workflow
must not be confused with an observed successful run.

## Structure and next milestone

`quant_engine/` contains UI-independent data, numerical analysis, patterns,
strategy execution, evidence export and chart functions. `app.py` is the thin
Streamlit interface; `tests/` holds numerical and application checks.

Read [the refined plan](docs/BUILD_PLAN.md) for product decisions, contracts and
release gates. Your [original project brief](docs/ORIGINAL_BRIEF.md) is preserved
as a reference; its complete feature list is not a claim about this prototype.
The next valuable increment is to add licensed, consistently
adjusted Indian equity history, an exchange calendar and immutable experiment
records; then freeze a chronological evaluation protocol and test against simple
benchmarks. Only add probability estimation after that foundation.

Research and decision support only. Outcomes are uncertain and profits are not
guaranteed.
