# Signal Ledger

A local technical-analysis and trading-research workbench for **Indian stocks** (NSE/BSE),
built for daily-candle swing research. Type a ticker, and Signal Ledger reads the trend,
structure, momentum, volume flow and chart patterns, shows where support and resistance
sit, studies what happened after similar patterns in the stock's own history, and
backtests explicit strategies with costs. It never invents a success probability.

## Run it

**Windows:** double-click `Start App.cmd`. The first run creates `.venv` and installs packages.

**Any OS:**

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt     # Windows: .venv\Scripts\python.exe
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

Open http://127.0.0.1:8501. No API key or account is needed; ticker data comes from
Yahoo Finance (via `yfinance`) and needs an internet connection. Without one, use
**Upload daily data** (an NSE stock-history CSV works unchanged) or **Demo data**.

To put it online so others can use it from a browser, see [DEPLOY.md](DEPLOY.md).

## What you can do

| Page | Use it to |
| --- | --- |
| **Analyze** | Fetch a ticker or load a file. The **Market read** gives one vote each to price structure, trend, momentum, volume flow, higher timeframes (completed weeks + months) and recent patterns, plus key support/resistance levels with % and ATR distances, and a **Timeframes** strip (monthly · weekly · daily) that says whether the daily move is aligned with or against the larger trend. The chart has switchable overlays (EMA, SMA200, Supertrend, Donchian, Keltner, VWAP, Bollinger) and lower panels (RSI, MACD, ADX/DI, Stochastic, MFI, OBV). Other tabs: pattern/candle/divergence detections, a conditional trade plan with sizing, two backtestable long strategies, and data quality and exports. **Replay** recomputes everything as of an earlier date. |
| **Scanner** | Run the full Market read over a watchlist (NIFTY 50 preset, or your own list of up to 100) and rank the results. Filter by verdict, timeframe alignment or recent patterns; select a row to open that stock in Analyze; export CSV. |
| **Pattern research** | *This stock:* for any detected pattern type (breakouts/retests, double tops/bottoms, head & shoulders, triangles, candles, divergences), forward moves, best/worst excursions and comparison with ordinary days in the same stock. *Watchlist (pooled):* the same study run on every stock in a list (NIFTY 50 preset), pooled into hundreds of events per pattern, with distinct-date counts, concentration, a date-clustered 90% range for the edge over ordinary days, and an explicit "how many would look good by chance" check. |
| **Strategy backtest** | Trade one bullish pattern across a watchlist as a portfolio (risk-based sizing, max open positions, ATR stop, R-multiple target, holding limit, costs). The pattern is chosen from the **training** years only; results are shown side by side for training and held-out **test** years, and judged against **random entries with identical rules** (40 runs), so market drift is not mistaken for an edge. |
| **Paper trades** | Record a setup on the day it appears (from Analyze, a Scanner row, or a strategy's latest signals) and let the app check later whether it hit its target, its stop or its holding limit, using only sessions after the signal. Plans are frozen once recorded (void with a reason, never edit); recording a past date is refused. Stats in R, cumulative curve, per-source breakdown, named ledgers. Stored in SQLite locally, or any database via a `DATABASE_URL` secret. |
| **Compare stocks** | Two tickers (or files) side by side: relative performance, drawdowns and return correlation. |
| **Learn** | 131 searchable definitions with worked examples, each labelled with what the app actually implements. |

Settings in the sidebar: capital, risk per trade and costs (used by the trade plan and
backtests only), a corporate-action ledger for split/bonus adjustment of uploaded files,
and breakout/retest rule parameters.

## Principles the code enforces

- **No look-ahead.** Every pattern records when it *formed* and when it became *knowable*.
  Swing points need right-side confirmation; boundaries and necklines are frozen at
  detection; replay slices the data before analysis. Tests check that truncated data
  reproduces earlier results.
- **No invented numbers.** Missing rows are never filled. A still-forming session is dropped
  from fetched data. The Market read counts evidence and is labelled as a heuristic,
  not a probability. "Success probability: unavailable" stays until a validated model exists.
- **Realistic simulation.** Next-open entries, costs and slippage on both sides, gap-through-stop
  fills, stop-first when a bar touches both levels, cash/risk/liquidity position caps.
- **It can say no.** "NO TRADE — INSUFFICIENT EVIDENCE" is a normal outcome.

Research and decision support only: not investment advice, and it never places orders.

## Project layout

```
app.py                     Streamlit shell: navigation, data source, Analyze page
quant_engine/
  providers.py             ticker → validated daily OHLCV (Yahoo), completed-bar filter
  data.py, nse_*.py        file ingestion and validation (generic, NSE history, UDiFF)
  indicators.py            trailing indicator catalogue (cross-checked against `ta`)
  patterns.py, research.py swings, structure, zones, candles, breakouts, chart patterns, H&S
  market_read.py           one-vote-per-family evidence summary + key levels
  timeframes.py            completed monthly/weekly bars, per-timeframe trend, alignment verdict
  scanner*.py              watchlist scan (NIFTY 50 preset) built on the same engine
  pooled_study.py, pooled_ui.py  watchlist-wide pattern outcomes (per-stock engine, then pooled)
  portfolio.py, portfolio_ui.py  multi-stock portfolio backtest, train/test split, random-entry control
  paper.py, paper_store.py, paper_ui.py  paper trading: frozen plans, forward-only evaluation, storage
  strategy.py, retest_*.py position sizing and the two strategy simulators
  event_study*.py          Pattern research engine and page
  comparison*.py           two-stock comparison
  *_ui.py, charts.py       presentation
learning/                  concept library, roadmap and progress sources
tests/                     pytest suite (run: python -m pytest -q)
docs/                      design notes, work log, original brief, status records
```

Run the tests with `python -m pytest -q` (installs: `requirements-dev.txt`). App tests
default to the bundled demo data so they run offline. Ticker fetching is tested
against stand-in provider responses.

## Project records

- [Original brief](docs/ORIGINAL_BRIEF.md): the full product vision.
- [Work log](docs/WORK_LOG.md): dated changes, reasons and verification.
- [Original-plan status](docs/PROJECT_STATUS.md) and [master checklist](docs/MASTER_CHECKLIST.md).
- Rule specifications: [event studies](docs/EVENT_STUDIES.md), [breakout-retest strategy](docs/BREAKOUT_RETEST_STRATEGY.md),
  [research reliability](docs/RESEARCH_RELIABILITY.md), [data quality](docs/DATA_QUALITY.md), [corporate actions](docs/CORPORATE_ACTIONS.md).
- Earlier handoff and inspection reports (16 Nov 2026 and before) are kept in `docs/` as history.
- The developer checklist page is still available at `http://127.0.0.1:8501/?page=build`.
