# Refined product and implementation plan

## Product thesis

Build an evidence-first technical research workbench. Its first job is to make
uploaded price data auditable, describe observable price structure, and test one
explicit hypothesis. Pattern recognition is a feature; demonstrated predictive
value is a separate research result. The competitive advantage must eventually be
reproducibility and prospective evaluation, not a larger indicator catalogue.

## First user and scope

Start with an individual researching Indian-stock daily, long-only swing setups using
one symbol per file. INR is assumed without conversion. CSV and XLSX are authoritative inputs. The user confirms all
bars are complete and supplies adjustment metadata. Daily observations are
session dates, not intraday timestamps. No provider or exchange calendar is
assumed. A labelled synthetic fixture demonstrates functionality, never market
performance.

First release: strict validation; SMA/EMA, Wilder RSI/ATR, MACD, Bollinger bands,
prior-bar relative volume; confirmed swings and structure; approximate zones;
doji/engulfing observations; double-top/bottom geometry; completed weekly context;
one explicit 20-session breakout rule, conditional position sizing and sequential
backtest; consistent charts and downloadable numerical evidence and report.

## Decisions before implementation

- Python, pandas/NumPy, Plotly and Streamlit keep computation independent of UI.
- Implement a short, documented set of indicators with numerical fixtures. Avoid
  TA-Lib's native installation dependency for this slice.
- Use a small sequential simulator for ONE fixed rule, making fill timing, gaps,
  costs and ambiguous bars explicit. Evaluate Backtesting.py before adding more
  order types; vectorized research is not the execution source of truth.
- Dataclasses describe analysis, events, settings and trades. No database until
  immutable run persistence is actually implemented; no empty storage/ML modules.
- No LLM is needed to compute or explain the first results. Deterministic reports
  can later become the evidence input to an optional language layer.

## Pipeline and interfaces

1. `load_bars(bytes, filename) -> DataFrame`: parse supported files, canonicalize
   six column names. `validate_daily -> ValidatedData` rejects ambiguous dates,
   duplicates, missing/nonfinite values, invalid OHLCV and intraday observations;
   sorts with a warning and never fills prices. Preserve raw-byte SHA-256 in runs.
2. `indicators(DataFrame) -> DataFrame`: backward-looking features, warm-up NaNs.
3. `swings -> list[Pivot]`: formation index AND confirmation index. Only expose
   a pivot after the right-hand window closes. Structure, zones and chart-pattern
   events use only confirmed pivots.
4. `analyze -> Analysis`: numerical snapshot, reproducible event coordinates,
   rule-derived explanations, limitations and weekly context. Each event has
   formation and detection times. Geometry is not a success probability.
5. `breakout_setup -> dict`: uses a completed close versus prior 20 highs, EMA50,
   relative volume >= 1.2 and ATR14. A candidate is valid only at the NEXT observed
   open; 2 ATR stop, 2R target and 10-session maximum hold. Costs enter sizing.
6. `backtest -> BacktestResult`: next-open fills, one position, no leverage,
   risk/cash/liquidity caps, adverse slippage, fees per side, stop-first ambiguity,
   gap-through stops, end-of-data close and marked-to-market equity.
7. UI and report consume the SAME Analysis object. JSON includes settings, source
   hash, time range, adjustment declaration and engine version.

## Build order and verification gates

1. Data contracts and validation: malformed files, datetime ambiguity, OHLC
   relationships, missing/duplicate dates, price adjustment warnings.
2. Numerical analysis: hand-calculated RSI/ATR, warm-up and flat-series behavior;
   every feature must remain unchanged when future data is appended.
3. Structure: confirmation-delay, event-prefix invariance, pattern coordinates,
   no candidate advertised as a confirmed breakout.
4. Simulation: exact cost/sizing fixtures, next-open timing, same-bar stop/target,
   gap loss beyond intended risk, no pyramiding and daily equity drawdown.
5. Dashboard: synthetic sample and upload path, chart, report, export, settings,
   data errors; automated Streamlit smoke checks and local server check.

## Later releases and their gates

1. Real-data research: versioned adjusted datasets, provider/calendar adapters,
   benchmarks, immutable SQLite run history, experiment registry, frozen
   chronological development/validation/test periods. Audit survivorship,
   delistings and corporate actions before cross-sectional claims.
2. Add double-pattern strategies and paper tracking only after event tests and
   research on enough independent occurrences; report uncertainty and sample size.
   Add triangles/head-and-shoulders only with explicit geometric definitions.
3. Probability models: fixed target/stop/horizon labels; purged time splits for
   overlapping labels; logistic baseline; Brier/log loss and calibration against
   unconditional frequency; costs and held-out economic performance. Record every
   experiment. No success percentage before these gates.
4. Intraday: exchange calendars/timezones/session anchors, incomplete-bar handling,
   same-time-of-day volume, spread and execution models. This is a separate scope.
5. Screenshot observations: qualitative and visibly separate from numeric research;
   never reconstruct precise OHLCV from an image. Optional evidence-bound LLM.

## Acceptance for this starting build

Working local dashboard, valid uploads, visible validation failures, annotated
data-based chart, numerical report, cost-aware baseline backtest, reproducible
exports, meaningful passing tests and documented limitations. It is a research
prototype, not completion of all 18 acceptance items in the original proposal.

## Research and implementation references

- pandas resampling: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
- Streamlit charts: https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart
- Streamlit AppTest: https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest
- Bailey et al., The Probability of Backtest Overfitting:
  https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf

Trying many configurations increases selection bias. A visually attractive chart
or profitable run is not evidence of a persistent edge. A general-purpose
terminal is a crowded category; a useful early differentiator is the ability to
replay exactly what was knowable on each date.
