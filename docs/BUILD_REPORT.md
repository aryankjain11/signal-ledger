# Signal Ledger · build and learning report

Updated: 2026-11-03. This is a living project report. The chronological record is
`WORK_LOG.md`; the comprehensive status list is `MASTER_CHECKLIST.md`. Neither is
a claim of profitable trading or of the learner having mastered the material.

## Purpose and scope

Owner update on 2026-11-03: learning assignments are paused until the owner
revisits their intended scope. Product implementation, testing, logs and source
synchronization continue. Existing educational references remain available;
new work does not require exercises or learner responses. `PROJECT_STATUS.md`
maps all 43 original phase items; `MASTER_CHECKLIST.md` tracks detailed subfeatures.

The owner's primary objective is to learn financial analysis, quantitative research
and software construction by building the system step by step. The product is a
research workbench for Indian-stock daily swing setups, with later extensions
explicitly gated by data quality, testability and evidence. An explanation page
must keep up with the feature it explains.

The original brief specifies a broad terminal: acquisition, structure/patterns,
candles/indicators, multiple timeframes, historical research, models, strategies,
risk, annotated screenshots, dashboard/history, narration and paper evaluation.
The master checklist covers those individually, plus education, reliability,
accessibility, operation and optional experiments. Optional work is not required
before the original product can be called complete, and it is not permission for
live orders or paid services.

## What exists before the learning milestone

The deterministic prototype accepts one stock's CSV/XLSX daily bars, validates
OHLCV and dates, computes a starter set of indicators and builds a Plotly chart.
It identifies delayed confirmed pivots, basic structure, approximate zones,
doji/engulfing observations and double-top/bottom geometry states. It compares
daily observations with completed prior-week SMA20 context. Replay slices inputs
before the as-of analysis.

One long-only breakout rule has conditional reference levels, cost-aware sizing
and a sequential simulator. It uses prior bars for signal inputs, the next open
for entry, fixed2ATR/2R thresholds and a ten-session hold. Its trade ledger models
blended per-side costs, adverse slippage, cash/risk/volume caps, opening gaps,
stop-first ambiguity and end-of-data liquidation. Numerical and report outputs
share one analysis result. The sample is synthetic and explicitly labelled.

Previously verified baseline:35 tests. New milestone results are recorded in
`WORK_LOG.md` only after they have actually run.

## Learning-led additions in this milestone

1. **Continuing work agreement.** `AGENTS.md` requires each future milestone to
   connect concept, specification, implementation, evidence, exercise and log.
2. **Shared implementation checklist.** `learning/roadmap.py` lists discrete work
   items with stable IDs, Done/Partial/Planned/Optional states, source-brief coverage,
   stage learning objectives and common acceptance gates. Existing starter behavior
   remains distinct from completion of its broader production/research requirement.
3. **Shared concept library.** `learning/concepts.py` is the content source for
   both the website and exported handbook. Worked entries include OHLCV, sessions,
   adjustments, trend/pivots/zones, moving averages, RSI/MACD/ATR, bands/volume,
   candle shapes, Evening Star, double formations, costs/sizing, drawdown, leakage,
   overfitting and calibration. A compact catalogue defines the remaining requested
   indicators/patterns now and will receive deeper implementation lessons later.
4. **Education and Concepts page.** It provides a learning route, searchable
   categories, an explicit application-coverage filter, formulas/rules, original
   hypothetical examples, mistakes, source links and builder references.
5. **Learning lab.** An RSI arithmetic step, a position-size example using the
   engine's actual sizing function, a labelled synthetic Evening Star illustration
   and a misconception question connect the vocabulary to visible behavior.
6. **Build checklist and journal page.** It exposes stage scope, gates, statuses,
   the chronological log and this report without requiring a market-data upload.
7. **Lesson1.** `lessons/01_from_prices_to_evidence.md` gives a connected walkthrough,
   exercises, worked answers and pointers from the concepts into the code.
8. **GitHub.** The user requested a repository and upload. The private repository
   is `https://github.com/aryankjain11/signal-ledger`. Remote upload/CI outcomes,
   including authentication limitations, belong in the final log entry.

## Architecture and why it is arranged this way

| Area | Responsibility | Why it is separate |
| --- | --- | --- |
| `quant_engine/data.py` | Parse, validate, daily/prior-week aggregation | Prevent UI convenience from fabricating data |
| `quant_engine/indicators.py` | Numeric causal features and warm-up | Independent calculations can be checked |
| `quant_engine/patterns.py` | Geometric observations, pivots and events | Shape detection and success probability are different |
| `quant_engine/strategy.py` | Fixed hypothesis, sizing and sequential fills | A signal and an execution model are different |
| `quant_engine/analysis.py` | Assemble evidence and readable report | Chart/report must agree on values |
| `learning/concepts.py` | Shared educational definitions/examples | Website and handbook cannot silently drift |
| `learning/roadmap.py` | Shared scope/status/gates | A feature label cannot silently become a completion claim |
| `learning/pages.py` | Learning UI and small teaching labs | Educational examples cannot become market signals |
| `scripts/export_learning_docs.py` | Generate handbook/checklist Markdown | Reviewable downloadable artifacts stay synchronized |
| `docs/WORK_LOG.md` | Human development record | Learn why the design changed, not just the final code |
| `tests/` | Numerical and meaningful application checks | Software claims require reproducible evidence |

The website remains Streamlit. This milestone does not migrate the frontend or
add a database/model/provider merely to make the architecture look complete.

## Curriculum and build sequence

**L0/S00, current:** establish shared vocabulary, learning UI, documentation and
versioned source. Run the first exercises; questions guide subsequent lessons.

**S02-A implemented (synthetic acceptance):** offline NSE CM UDiFF-style CSV/ZIP
preview, exact EQ security selection, provider-neutral passports, source versus
replay hashes and Lesson 2. See `S02_DATA_IMPORT.md` for individual gates and limits.
Real-file acceptance, a verified full current NSE schema and a licensed provider
are not yet complete. No automatic feed or corporate-action adjustment is implied.

**Next S02:** accept a permitted real report, define the versioned session/calendar and
adjustment contracts, import a small verified Indian-stock dataset and show its
provenance. Learn splits/dividends/volume adjustment and distinguish a missing
session from a holiday. Data access, subscription costs or credentials are resolved
before a provider-dependent implementation.

**Then S03/S06:** strengthen causal structure and configurable indicator conventions.
For every feature, first write the hand example and failure cases. Use tests to
connect the finance definition to a reproducible function.

**Then S04/S05:** implement one small pattern family at a time. Start with explicit
context and a detector specification. Evening Star is a good learning candidate
after the candle lesson; it is currently explained but not detected.

**Then S07–S11:** causal timeframe alignment, precise strategies, risk, frozen
evaluation and persisted historical research. Plot attractive curves only alongside
their assumptions, sample size, costs and comparison protocol.

**Later S12–S17:** probability models, screenshots, evidence-bound narration and
prospective paper tracking. Intraday data and broker data adapters are independent
scopes with their own time, session and execution challenges. Software quality,
documentation and accessibility continue through every phase.

## Definition of done for each small feature

- The learner can find a plain definition and a small labelled example.
- The actual parameters, data requirements, edge cases and knowledge time are stated.
- The code produces a usable result, not an empty placeholder or a demonstration
  presented as a live feature.
- Relevant independent numerical, negative-case, leakage or UI checks pass.
- The report/chart/help match the same underlying implementation.
- The checklist and log identify what was verified and what remains limited.
- A reviewed source snapshot is uploaded and verified; remote CI is reported
  separately from local checks.
- The next exercise/question is recorded. Learner mastery is never auto-checked.

## Financial concepts that must remain distinct

An observation is not an execution; a score is not a probability; a backtest win
rate is not a current setup forecast; volatility is not direction; cash exposure
is not planned stop risk; a stop order is not a maximum-loss guarantee; a traditional
pattern interpretation is not empirical validation; an adjusted source hash is
not a certificate of data quality. The learning page repeats these distinctions
where they are useful, rather than hiding all uncertainty in a footer.

## Verification and limitations

New split/bonus increment: reviewed action-ledger CSV, before/after share ratios,
ex-date and known-on cutoff policy, optional adjusted OHLCV research view, preserved
original source and separate research ID/hashes/factor exports. Source declaration
must be unadjusted; ambiguous/unsupported events stop for review. Engine/UI guards
disable execution for adjusted and known action-crossing ranges. No automatic
action feed, dividend/total-return calculation, composite event handling or
share-accounting backtest is claimed. See `CORPORATE_ACTIONS.md` for the contract.
The master checklist now has 344 items; broad corporate-action gates remain Partial.
Latest local regression: **168 passed in 30.66 seconds**, including 27 action cases
and mode-switch/cache-policy isolation. Expanded counts: 35 Done, 16 Partial,
281 Planned, 12 Optional. Original phase counts remain 8 Done, 18 Partial and
17 Planned; the bounded research feature does not complete the whole data stage.

Earlier data-quality increment: versioned NSE CM 2026 calendar snapshot with trading
holidays, January closure amendment, Budget and Muhurat Sunday overrides; missing
observation/non-session/future-date flags; explicit 18:00 IST conservative freshness
policy; source/replay isolation and passport/evidence downloads. Calendar checks
do not infer security listing/suspension history or fill bars. Other years and
exchanges remain unverified. `DATA_QUALITY.md` contains sources and limitations.
At that increment the shared checklist had 343 items; broader S02 gates remained Partial.
Local regression for this increment: **141 passed in 49.18 seconds**. The original
43-item phase mapping has 8 Done, 18 Partial and 17 Planned items; none of the five
original phases is claimed complete. Expanded task counts are 34 Done, 14 Partial,
283 Planned and 12 Optional, which are not effort-weighted completion percentages.
Remote evidence: source commit `9a41497dd7024d0a1d3b39534573f80df6f45e77`,
54 of 54 source files verified; GitHub run **41657477162**, job **125991544026**,
passed **141 tests in 10.45 seconds** on Ubuntu 26.04 / Python 3.13.17. Browser
checks confirmed the original-plan table and calendar summary on the owner's file.

Earlier direct-NSE-export result: **117 local checks passed in 48.11 seconds**.
Source commit `dbb5a3db7e48cbf58f7bb3b2519e7ca063f6de8d` was uploaded privately;
all **49** allow-listed source files matched their remote blob SHAs. GitHub run
**41652886132**, job **125975413746**, passed **117 tests in 12.78 seconds** on
Ubuntu 26.04 / Python 3.13.17. Browser upload of the owner's original file rendered
21 sessions with correct label, close and interpretation record. The real dataset
and its screenshot remain local. The new numerical fixtures contain invented data.

**Direct security-history upload increment:** `quant_engine/nse_quotes.py`
recognizes the supplied NSE quote-export schema, parses explicit dates and Indian
number grouping, selects CLOSE/share VOLUME, guards EQ identity and records its
interpretation in the passport. Research → Upload daily data requires no manual
file cleanup. Existing generic CSV/XLSX and UDiFF paths remain separate.
The owner's 21-row download was parsed locally unchanged; test fixtures use
invented data and the downloaded file is not redistributed. See `NSE_CSV_UPLOAD.md`
and the latest work-log entry for test and browser evidence. The catalogue now has
120 concepts and the checklist 342 items (S02-021 adds this explicit upload gate).

Earlier S02-A acceptance: **90 local tests passed in 52.97 seconds**. Source commit
`165264391dbdef6e0f1dcd1b3d88eec7c70e06c2` contains all 46 reviewed files, each
verified against its remote blob SHA. GitHub Actions run **41639106785** passed
the same 90 tests in **11.79 seconds** on Ubuntu 26.04 / Python 3.13.17.
This synthetic/schema-subset gate does not establish current full NSE schema
compatibility, real-source authenticity or profitability. See `S02_DATA_IMPORT.md`.

The new modules are `quant_engine/nse_files.py` (bounded offline report adapter),
`datasets.py` (instrument/provenance contract) and `data_ui.py` (import/passport UI).
`tests/test_nse_files.py` adds 41 checks to the previous 49. Lesson 2 is available
inside the app and as Markdown. Shared handbook/checklist exports remain tested.

Tests cover catalogue integrity and documentation consistency as well as app search,
page navigation, lab arithmetic and invalid inputs. The existing35 analytical/app
checks remain a regression requirement. A synthetic fixture tests software; it does
not test economic value. Compact glossary entries are introductory, not full
standalone courses or claims that all future definitions have been quantitatively
validated.

Earlier learning-foundation verification: repository privacy was verified. All 40 source-snapshot files were uploaded
and their remote blob SHAs matched the reviewed contents, at source commit
`189b15a6043dad2638f7c04d08920c52ada0d03a`. GitHub Actions run 41624242800 passed
all 49 tests on a clean Ubuntu 26.04 / Python 3.13.17 runner (3.13 seconds of tests).
The fresh local run before upload also passed 49 tests (13.05 seconds).
See `GITHUB_SYNC.md` for links and the resolved approval-service outage.

The computer's Git client has no saved
GitHub credentials; the connected GitHub tools can upload to the repository.
No credential is copied into this project. CI execution depends on the repository's
Actions availability and the actual workflow run; a workflow file alone is not a pass.

## Next implementation work

Learning assignments are paused. Current position is a working daily research
prototype, with bounded data-quality checks and parts of original phases 1–3.
Next data gates are broader historical calendar coverage, UDiFF real-report
acceptance and corporate-action policies/fixtures. Then continue structure,
indicators and pattern/strategy families before statistical/model layers.
`PROJECT_STATUS.md` maps every original phase item; no phase is claimed complete.
