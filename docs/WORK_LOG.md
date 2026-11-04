# Work log

This is the continuing development journal. Entries record meaningful work batches,
why they were done, evidence and what the learner should try. This is not yet an
automatic database of every analysis performed in the application.

## 2026-11-03 · Retrospective: starting prototype

**Provenance:** reconstructed from the existing source, test results and this chat;
not a contemporaneous activity-by-activity log. Work began in the preceding session.

- Preserved the original 22-section brief; narrowed the first build to Indian-stock
  daily swing research. Selected Python/pandas/NumPy, Plotly and Streamlit.
- Built CSV/XLSX validation, Wilder RSI/ATR, moving averages, MACD, Bollinger bands,
  relative volume, confirmed pivots, approximate zones, candle observations and
  double-top/bottom state events. Formation and knowability dates are separate.
- Added completed prior-week context, as-of replay, deterministic reports and
  source-hashed evidence exports.
- Built one long-only breakout simulator: next-open entry, fixed 2 ATR stop, 2R
  target, ten-session hold, risk/cash/volume caps, costs, gaps and stop-first bars.
- Added a labelled synthetic walkthrough. No real-data profitability was established.
- Verification in the previous session: **35 tests passed**. Coverage includes
  data failures, numerical seeds, future-append invariance, event timing, cost-aware
  sizing, execution assumptions and application upload/replay/backtest flows.
- Corrected an early replay test that mistakenly expected RSI to remain in warm-up
  after enough observations. Simplified a chart legend after visual inspection.
- Environment note: restricted local networking prevented Streamlit's internal
  connection; tests and local server were run with local-access authorization.
- An unnecessary cleanup attempt for an incomplete parent-level `.venv` was rejected
  by automatic approval review. It was left untouched. No cleanup is needed to run
  this project.
- Remaining: no calibrated probabilities, exchange calendar, saved-run database,
  provider integration, complete pattern catalogue, screenshot analysis or live orders.

## 2026-11-03 · Milestone L0 opened: learning-led project foundation

**User instruction:** turn every feature in the brief plus useful extensions into
a checklist; build sequentially; document ongoing work; teach the financial concepts
and create an Education and Concepts page; create a GitHub repository and upload.

**Completed in this work batch:**

- Inspected the existing application, numerical conventions, tests and original
  feature lists before designing the learning layer.
- Confirmed the connected GitHub identity. The connector supports repository file
  changes but exposes no repository-creation action; used GitHub's creation page
  as the fallback. Selected private visibility and the name `signal-ledger`.
  Creation/upload verification is recorded in a later entry once it is observed.
- Added `AGENTS.md` to preserve the owner's learning, logging and evidence requirements
  across future work. Created this journal before the new implementation.
- Chose one shared concept catalogue for the website and downloadable handbook,
  and one shared roadmap catalogue for the website and Markdown checklist.
- Education design: plain definition, calculation/rule, original hypothetical
  example, interpretation, common mistake, implementation status and further reading.

**Learning point:** an indicator describes data; a strategy adds precise entry and
exit rules; a backtest simulates those rules; validation asks whether the result
survives genuinely new observations. These are four different deliverables.

**References checked:** Fidelity's RSI, MACD and ATR guides; Zerodha Varsity's
multi-candle chapter; official NSE corporate-action/report resources. Links are
stored alongside the relevant educational material.

**Next:** implement the checklist and learning pages, export the handbook, exercise
the UI, run tests, verify repository upload and log the measured result.

## 2026-11-03 · L0 implementation and first verification

- Authored a **341-item, 21-stage checklist**, covering every named chart pattern,
  candle formation and indicator from the brief, along with data, risk, research,
  models, image observations, narration, paper evaluation and operational work.
  Added optional extensions separately from the original completion gate.
- Authored **116 concept entries**, including fuller worked explanations for the
  foundation/current engine and Evening Star; other future items have introductory
  definitions to expand during their implementation milestone.
- Added Education and Concepts and Build checklist & log as sidebar workspaces.
  They do not require an upload. Added an RSI arithmetic lab, a risk lab that calls
  the real sizing function, a synthetic Evening Star illustration and quiz feedback.
- Added detailed Lesson1, the living build report, handbook/checklist generation
  and tests that ensure generated Markdown agrees with the source catalogues.
- Added a GitHub Actions test workflow using the versions documented by the
  official checkout/setup-python projects at the time of this change. Its execution
  has not yet been verified; a workflow file is not a successful CI run.
- Verified **aryankjain11/signal-ledger exists and is private**, on its initial
  README commit. The computer's Git client cannot authenticate without interaction;
  used the already-connected GitHub API tools for the planned source upload.
  No local Git credential or token was extracted or stored.
- First extended test run: **48 passed, 1 failed**. The failure was an overly strict
  search test: full-text search intentionally finds related entries that mention
  Evening Star. Corrected the test to assert the direct result comes first and
  related results remain in the requested category; did not remove useful search.
- Additional review: replaced a text-based implementation filter with an explicit
  list of actual engine behaviors, so education-only Evening Star cannot appear as
  a currently implemented detector.

**Next verification:** rerun49 tests, inspect page navigation in the browser,
review the upload allow-list and commit the tested snapshot. Final evidence follows.

## 2026-11-03 · L0 local acceptance gate passed

- Final full suite after the search-test correction: **49 passed in11.95 seconds**
  on the prepared Python3.13 environment. This includes the original35 checks and
  14 additional learning/catalogue/application cases (including parameterized cases).
- Browser verification: Education and Concepts loads without an upload; Start here
  shows the eight-step route; Concept library initially renders RSI; searching
  Evening Star returns the direct entry and related definitions. The displayed
  Evening Star status explicitly says education/illustration only, detector pending.
- Generated handbook/checklist exports match their shared Python catalogues under
  automated tests. Marked the corresponding S00 learning-foundation items Done.
- Prepared a source-upload manifest: explicit source/test/docs/configuration paths,
  synthetic CSV only, and a known-credential-pattern check. It excludes virtual
  environments, private uploads, local databases, runtime outputs and credentials.
- Added `scripts/source_manifest.py` to make this upload selection reviewable and
  repeatable. This is a limited precaution, not a claim that all secret scanning is
  solved. Full secrets/operations work remains in S18.
- No numerical trading rule changed in this milestone. No Evening Star detector,
  statistical win probability or real-data performance was claimed.

**Learner exercise:** start Lesson1 and bring back the candle, RSI or sizing
calculation you find least clear. **Next engineering milestone:** S02 verified
daily-data source, calendar and corporate-action policy. Remote verification follows
in the next log entry rather than being assumed from local file creation.

## 2026-11-03 · Remote upload blocked; source preserved

- Reviewed a38-file source snapshot (36 text files and2 synthetic/application
  screenshots), totaling about471KB. Binary objects were separated from text
  content for the GitHub Git-tree API. This snapshot excluded environments,
  private uploads and secrets.
- The automatic approval service failed with **“Selected model is at capacity”**.
  The error explicitly said it was a review failure, not an unsafe-action finding,
  and that the affected action was not executed. Retried the reviewed upload once;
  the same service-capacity condition recurred during content preparation.
- Did not bypass the approval check through browser uploads, credential access or
  another write mechanism. No source commit or branch update is claimed. The
  private repository currently has its initial README commit only.
- Asked the owner whether to retry after service recovery or use a source archive.
  This is guidance about an infrastructure blocker, not a new request for permission
  to create the already-authorized repository.
- Prepared `scripts/package_source.py` and `docs/GITHUB_SYNC.md` so the owner has a
  source-only archive option and an exact resumable status. Packaging and archive
  verification are recorded after they run below.
- Rechecked the updated learning/catalogue slice after marking verified local work:
  **14 passed in6.72 seconds**. The remote-upload checklist item remains unchecked;
  the workflow remains Partial because remote CI has not executed for this source.

## 2026-11-03 · Source archive verified

- Packaged40 reviewed source/teaching/test/configuration files plus an embedded
  `SOURCE_MANIFEST.json`. ZIP integrity checks passed and every archived file's
  SHA-256 matched its manifest record. Confirmed environment/private-upload paths
  were absent. The archive lives at `outputs/signal-ledger-source.zip`.
- Marked source synchronization Partial, rather than Done: preparation and private
  repository creation are complete, but a verified remote source commit is blocked.
- Regenerated the catalogue documents after the status change. The archive is
  regenerated after this entry so it carries the latest journal and blocker note.
- No scheduled retry or background automation was created. The owner's guidance
  question remains pending; no upload workaround will bypass approval review.

## 2026-11-03 · Owner requested upload retry

- The owner selected **retry here after the service recovers**. Reused the existing
  private repository rather than creating another one.
- Re-read the working agreement and sync status, and checked the remote README:
  it still contained the initial repository description, not the project source.
- A new, small immutable-content write through the same connected GitHub tool
  succeeded. This establishes that the approval service can process a retry now;
  it does not yet establish that the source is committed on `main`.
- Retry approach: submit reviewed files as individual content objects, assemble
  their tree, then make one atomic source commit and verify its files. Each write
  continues through automatic approval review; no alternative bypass is used.
- Re-running the full local regression suite before the branch update. Actual
  commit, verification and CI outcomes will be recorded once observed.

## 2026-11-03 · Source upload completed and verified

- The approval service processed the retry normally. Prepared all 40 reviewed
  files through the connected GitHub tools, assembled their Git tree, created
  source commit **`189b15a6043dad2638f7c04d08920c52ada0d03a`**, and updated `main`
  with an expected-head check (no forced overwrite).
- Repository: https://github.com/aryankjain11/signal-ledger. Reconfirmed **private**
  visibility. Source includes the engine, app, synthetic CSV, tests, workflow,
  original brief, roadmap, concept library, lessons, build report and journal.
  Environments, private uploads, credentials, databases and runtime outputs were excluded.
- Fetched every uploaded file at the source commit and compared its Git blob SHA
  with the reviewed upload object: **40 of 40 matched**. Repository creation or an
  API success message alone was not used as proof of a complete source upload.
- Fresh local regression before upload: **49 passed in 13.05 seconds**.
- GitHub Actions **run 41624242800**, job **125877447096**, completed successfully.
  The log reports **49 passed in 3.13 seconds**, on Ubuntu 26.04 / Python 3.13.17.
  Run: https://github.com/aryankjain11/signal-ledger/actions/runs/41624242800.
- Marked source synchronization and clean-runner CI Done in the checklist; updated
  the sync report, README and build report. Updated the Git/GitHub concept entry
  to connect the learner's actual repository and CI to the definitions.
- Documentation audit follows the verified source commit. Its shared catalogue
  exports are regenerated and checked before uploading the audit. These records
  reference an already observed commit/run rather than claiming to predict the
  outcome of the commit that contains the record itself.

**Learning point:** a commit is a versioned snapshot, content hashes check what
was uploaded, and a CI result checks the behavior of that snapshot in a separate
environment. These are related but distinct forms of evidence. A passing software
test suite still does not demonstrate trading profitability.

**Owner exercise:** open the source commit and Actions run; identify the tests
step, then return to Lesson 1's candle/RSI/sizing examples. **Next engineering
milestone remains S02:** verified daily data, exchange sessions and adjustment policy.

## 2026-11-03 · S02-A opened: daily-data contract and NSE file adapter

- The owner asked to begin the next planned increment. Read the project working
  agreement, journal, checklist and existing ingestion/analysis interfaces first.
- Small milestone: normalize user-supplied NSE CM UDiFF daily report CSVs into a
  single selected stock's daily OHLCV, and attach a provider-neutral data passport
  containing identity, source hashes, date semantics and adjustment/permission
  declarations. Keep the existing standard CSV/XLSX path working.
- Checked official NSE format/report pages. The current reports page points to
  CM-UDiFF Common Bhavcopy Final ZIP rather than the discontinued legacy format.
  The adapter will use the published UDiFF field names, not guessed legacy aliases.
- Checked NSE's data-usage policy: downloadable/visible data is not assumed to
  confer redistribution or automated-feed rights. This milestone builds a local
  importer for files the user is entitled to use; no subscription, automated scraping,
  rights acceptance, real-market dataset redistribution or broker connection is added.
- Acceptance: deterministic normalization; exact instrument/series selection;
  no silent duplicate merging; reject inconsistent identities/dates/prices;
  passport exported with numerical evidence; meaningful synthetic fixtures and
  application tests; explanation and exercises in Lesson 2.
- Calendar reconciliation and corporate-action adjustments remain later S02 work.
  Recording an unadjusted/unknown status is not the same as verifying or adjusting it.

**Learning example:** a hypothetical 2-for-1 split can halve the quoted share price
while doubling the share count. A raw price jump alone does not establish an
economic return or justify inventing an adjustment.

**Official references:**
https://www.nseindia.com/static/resources/forms-formats-members
https://www.nseindia.com/all-reports
https://www.nseindia.com/static/market-data/nse-data-policy

## 2026-11-03 · S02-A implementation and local acceptance

- Completed the offline daily-report CSV/ZIP adapter, EQ security selector,
  provider-neutral passport, raw/normalized hashes and downloadable analysis CSV.
  Existing standard CSV/XLSX ingestion now also attaches a passport.
- Separated the full source identity from the historical replay slice. Evidence
  JSON and the passport carry an analyzed-data hash matching the exported CSV;
  a replay does not overwrite the original source count/range/hash.
- Reject duplicate date/symbol/series records, inconsistent selected ISINs,
  malformed required fields, invalid selected OHLCV, recognized provisional or
  interim reports, and unsupported/unsafe ZIP members. Imports stay in memory.
- Added a deterministic 80-report/two-security teaching ZIP generated without
  real-market data. Missing security records are disclosed without fabricated bars
  or an invented exchange calendar. One/two-row imports show preview only.
- Added Lesson 2 in Education → Start here, with definitions, worked split and
  report examples, code walkthrough, exercises/answers and source limitations.
  Added bhavcopy, security identity and data-passport entries (119 concepts total).
  Updated the shared 341-item roadmap, README, build report and S02 scope record.
- Fixed a pandas method/column name collision (`frame.isin` versus `frame["isin"]`)
  during the initial smoke check; identity selection is now covered by regression.
- Source research limitation: the linked current NSE format workbook could not
  be fetched (connection reset/timeout). An official NCDEX UDiFF document confirmed
  shared field meanings only, not the full current NSE equity schema. No real-file
  acceptance or authenticated source claim is made.
- First importer suite: **38 passed in 19.79 seconds**. After adding uploaded-ZIP
  analysis/failure and Lesson 2 checks, full regression: **90 passed in 52.97 seconds**
  in the local Python 3.13 environment. This includes all 49 existing checks.
  Shared handbook/checklist exports were regenerated before the complete run.

**Owner exercise:** select DEMOBETA in the synthetic report walkthrough, inspect
its passport, then replay earlier. Explain which row counts and hashes change and
why a 2-for-1 split does not alone halve the holding value. No mastery is assumed.

**Remaining S02 gates:** permitted real-file/current-schema acceptance, versioned
exchange calendar and genuine missing-session reconciliation; then corporate-action
policies/fixtures, provider integration and durable dataset storage. GitHub upload
and remote verification of this milestone are recorded after they are observed.

## 2026-11-03 · S02-A published and remotely verified

- Private repository reconfirmed. Published source commit
  `165264391dbdef6e0f1dcd1b3d88eec7c70e06c2` on main, based on verified previous
  head `8abef847f1f5e8d8dbea464abe769bb53c036ffe`, using an expected-head update.
- Fetched all **46** allow-listed source files at that commit and matched their
  blob SHAs to the reviewed contents. A few connector reads returned internal
  errors; smaller sequential retries succeeded. No content mismatch remained.
- GitHub Actions run **41639106785**, job **125927744182**, completed successfully:
  **90 passed in 11.79 seconds**, Ubuntu 26.04 / Python 3.13.17.
  Run: https://github.com/aryankjain11/signal-ledger/actions/runs/41639106785.
- Restarted only this project's verified Streamlit server to refresh imported
  modules. Browser-checked Research → Synthetic NSE report walkthrough →
  Data & exports: 80 observations, exact instrument/ISIN, synthetic origin/basis,
  source versus analysis range, limitations and both download controls rendered.
  Screenshot: local `outputs/S02-import-verified.jpg` (runtime output, not uploaded).
- This documentation audit records the observed source commit and remote result;
  it does not predict the result of its own later audit commit. The source-only
  archive is rebuilt after this record with the same allow-list and verified hashes.

**Milestone outcome:** offline importer/passport and learning increment complete
for the supported synthetic acceptance gate. Full S02 remains Partial. Next is
permitted real-file/current-schema acceptance and exchange-calendar reconciliation,
then corporate-action policies. No market-performance claim or learner completion
has been added.

## 2026-11-03 · S02-021: original NSE stock-history CSV compatibility

- Owner supplied an unmodified NSE security-history CSV and asked to eliminate
  manual column/date/number cleanup. Inspected its header and parser behavior.
  This is a security-history download, not a daily multi-security UDiFF report.
- Implemented scoped format detection in `quant_engine/nse_quotes.py`, called by
  `load_bars`. Recognize header whitespace/case/BOM and long OHLCV aliases, convert
  explicit English DD-Mon-YYYY dates, validate Indian/international comma grouping,
  use CLOSE and traded share VOLUME, ignore extra market fields, and sort sessions.
- Added EQ-only and filename/supplied-symbol conflict guards. Download filename
  supplies a clearly disclosed label hint, not authenticated security identity.
  Missing numbers, malformed groups, dates, duplicate sessions and bad OHLC still
  fail instead of being filled or silently repaired. Standard CSV stays strict.
- Added detected-format feedback and interpretation details in Data & exports.
  Passport stores the normalization policy; adapter version is now 1.1.0 so new
  source interpretations are versioned. Adjustment declarations remain unverified.
- Checked the owner's unchanged file locally: **21 sessions**, ascending after
  normalization. No row was fabricated, dropped or aggregated. The actual file
  remains outside source control, fixtures and GitHub uploads.
- Added 27 independent checks using invented values in the observed schema:
  exact close/volume mapping, grouping formats, XLSX equivalence, invalid fields,
  ambiguity/identity guards and app upload/passport flow. Initial targeted result:
  **27 passed in 17.02 seconds**, with a pandas inference warning for an invalid-date
  rejection. Made ISO parsing explicit, eliminating the inference path.
- Full regression after that change: **117 passed in 48.11 seconds**, without
  warnings. Includes the previous 90 checks and generated-doc consistency checks.
- Added `docs/NSE_CSV_UPLOAD.md`, expanded Lesson 2 and the concept library (120
  entries), and added explicit S02-021 to the shared roadmap (342 items). Updated
  README/build report/S02 scope and regenerated the handbook/checklist.

**Learning example:** invented CLOSE 1,240.00 versus LTP 1,248.00 means this
daily analysis uses 1240. VOLUME 23,34,553 means 2334553 shares, not rupee turnover.
Formatting conversion preserves quoted values; it is not split/dividend adjustment.

**Owner exercise:** upload the original file through Upload daily data, inspect
the detected format and interpretation record, and explain the long-indicator
warm-up warning for a one-month history. Learner mastery is not marked complete.

**Remaining:** UDiFF real-report/current-schema acceptance, exchange calendar and
corporate-action reconciliation remain separate gates. Browser and GitHub results
for this change will be recorded once observed.

## 2026-11-03 · Direct NSE upload browser and GitHub gate passed

- Restarted only this project's verified local server. Uploaded the owner's
  original CSV through Research → Upload daily data with the file chooser, then
  confirmed completed sessions. No manual preprocessing was performed.
- Browser displayed the inferred stock label, **21 sessions**, source date range,
  closing price matching the supplied CLOSE field, computed indicators and the
  appropriate unavailable/short-history states. Data & exports showed EQ identity,
  input hash, normalization details and the original adjustment/rights limitations.
- Saved local proof `outputs/nse-quote-upload-verified.png`. Because it displays
  the owner's uploaded market data, it is excluded from the source upload.
- Published commit **`dbb5a3db7e48cbf58f7bb3b2519e7ca063f6de8d`** on main, based
  on `718fef3a53a20e5cad71d54d96215351a78512bc`, using an expected-head update.
  A tool-catalog refresh interrupted commit preparation once; refreshing the
  catalog and retrying normally succeeded. No authorization check was bypassed.
- Reconfirmed private visibility. All **49 source files** at the commit were
  fetched and their blob SHAs matched the reviewed upload objects. Source excludes
  the actual CSV, screenshots of it, environments and credentials.
- GitHub Actions run **41652886132**, job **125975413746**, succeeded:
  **117 passed in 12.78 seconds**, Ubuntu 26.04 / Python 3.13.17.
  https://github.com/aryankjain11/signal-ledger/actions/runs/41652886132
- Updated the sync/build reports and README after observing these results. This
  documentation audit references the verified source snapshot; it does not claim
  to predict its own later commit/test result. Source archive is regenerated and
  hash-checked after the final documentation update.

**Outcome:** the supplied security-history format now uploads unchanged. Keep
the original filename for its label hint and use a longer date range to warm up
long indicators. UDiFF acceptance, calendar and corporate actions remain separate
next steps. No trading-performance or learner-mastery claim is made.

## 2026-11-03 · Owner steering and calendar/data-quality increment

- Owner paused learning exercises until their intent is discussed later, and
  requested implementation plus a done/remaining checklist against the original
  plan. Recorded this preference in AGENTS.md; it supersedes exercise-related
  steps. Existing reference pages remain available, with no new assignments.
- Inspected original brief §19 and mapped all 43 implementation bullets across
  its five phases in shared `learning/progress.py`, exported `PROJECT_STATUS.md`
  and the Build checklist & log workspace. Partial scope is explicit; no complete
  original phase or percent-of-effort claim is made.
- Checked official NSE CM holiday and amendment circulars. Implemented offline
  snapshot `NSE-CM-2026/2026-11-03.1`, January 15 election closure and February 1
  Budget/November 8 Muhurat live Sunday overrides. Settlement/banking holidays
  are deliberately not substituted for trading holidays.
- Added visible-slice checks for absent expected observations, non-session/future
  dates, unsupported years, zero volume, short history and freshness. Source
  identity remains stable; replay disables today's freshness comparison and
  does not inspect hidden source rows. No bars are inserted, dropped or changed.
- Freshness uses a documented conservative 18:00 Asia/Kolkata application cutoff,
  not an assertion about exchange close or provider publication/finality.
  Listing/suspension histories remain unverified, so absent observations are
  candidates for review rather than proof of a broken feed.
- The summary appears under Data & exports and is included in the passport,
  analysis/backtest evidence and its own JSON download. Calendar/source hashes
  and assessed clock are recorded. Synthetic and other-exchange fixtures are
  explicitly excluded from the NSE calendar audit.
- Added `docs/DATA_QUALITY.md` with sources and limits. Broader calendars and
  corporate actions remain pending; the added bounded gate is S02-022 (343 total
  tasks). Updated the relevant reference entry without adding exercises.
- Targeted verification: **23 passed in 18.74 seconds**, covering exceptional
  sessions, unsupported dates, timezone/cutoff boundaries, gaps versus freshness,
  replay isolation, immutability and UI flags. Full regression: **141 passed in
  49.18 seconds** (117 previous checks, 23 calendar checks and one original-plan
  mapping/export check). No changes to strategy rules were made.

Sources: NSE CMTR71775 (2026 CM holidays), CMTR72260 (January closure amendment),
CMTR72349 (Budget live session), CMTR76941 (Muhurat schedule). Exact links are in
DATA_QUALITY.md and in the exported assessment. Only source references and the
calendar rules are bundled; no owner market-data download is redistributed.

## 2026-11-03 · Calendar/status live and remote verification

- Browser-checked Build checklist & log: 343 expanded tasks, 34 Done, 14 Partial,
  12 Optional; original five-phase overview and project-status download rendered.
  Original-plan mapping remains 8 Done, 18 Partial and 17 Planned out of 43 bullets.
- Uploaded the owner's unchanged NSE security-history file locally. Data & exports
  displayed 21 observations, no absent/unexpected observations within the checked
  range, and current through November 3 with zero-session lag. Short-history and
  adjustment/identity limits remained visible. No real dataset was uploaded remotely.
- Saved runtime proof to `outputs/project-status-verified.png` and
  `outputs/data-quality-verified.png`; runtime outputs remain excluded from source.
- Published source commit **`9a41497dd7024d0a1d3b39534573f80df6f45e77`**, based on
  `fc9582d2720e45ef7372ccd0b46e257592619384`, with an expected-head branch update.
  Reconfirmed private visibility and fetched/matched **54 of 54** source blob SHAs.
- GitHub Actions run **41657477162**, job **125991544026**, completed successfully:
  **141 passed in 10.45 seconds**, Ubuntu 26.04 / Python 3.13.17.
  https://github.com/aryankjain11/signal-ledger/actions/runs/41657477162
- Final documentation audit records the observed source snapshot and test run;
  it does not predict its own later commit. Regenerate and verify the source-only
  archive after updating these records, keeping market uploads/screenshots local.

Current position: daily research prototype with bounded data-quality coverage and
partial implementations across original phases 1–3. No original phase or final
acceptance is declared complete. Next implementation gates: UDiFF real-report
acceptance, broader calendars and corporate-action policies/fixtures, followed by
structure/indicator and pattern/strategy expansion. Exercises remain paused.

## 2026-11-03 · Reviewed split/bonus normalization opened

- Continued the next authorized data-foundation increment. Scope: reviewed
  split/bonus ledger, preservation of source prices, separate adjusted research
  view and auditable per-date factors. No learning assignments were added.
- Checked official NSE corporate-action records and investor material for
  split/bonus ratio semantics. Derived original implementation/examples; no
  market dataset or source document was redistributed. References are in
  `docs/CORPORATE_ACTIONS.md`.
- Added explicit CSV fields for action ID, symbol, ex-date, first knowable date,
  type, shares before/total shares after and reference. Reject ambiguous same-date
  composites, duplicates, bad ratios/dates, unsupported types and missing effective
  ex-date bars. No action is inferred from a price jump.
- Normalize pre-ex-date OHLC and volume consistently, composing multiple actions.
  Ex-date bars remain in new units. Replay considers only events declared knowable
  by the cutoff, applies only effective events, and uses the selected cutoff's
  share units rather than later events. Late-known corrections stay excluded from
  earlier replay. These declarations are not independently authenticated.
- Preserve original source identity and hashes; add a separate research-view ID,
  ledger/result hashes, raw-visible download, factor CSV and audit JSON. Source
  warnings are preserved separately while adjusted jump warnings are recomputed.
- Added optional controls and synthetic file examples. Original price CSVs need
  no editing. Unknown/already-adjusted sources cannot enter adjusted mode; the
  original price basis must be explicitly declared unadjusted.
- Adjusted research and raw views spanning known effective events disable trade
  plans/sizing and backtests. Added guards in the engine and UI; the current
  simulator does not yet account for share/lot changes and entitlements.
- Initial targeted run: **24 passed, 2 failed in 16.16 seconds**. Both failures
  were incorrect test assumptions: changing only one of two symbols still left
  a matching future event, and a two-bar UI replay correctly stopped at the
  existing three-observation analysis minimum. Corrected those cases; did not
  loosen the engine's data gate. Engine execution guards were strengthened during
  review. Final full-suite evidence follows after completion.
- Updated the relevant reference entry and original-phase status description,
  added bounded S02-023 (344 tracked tasks), kept broad adjustment/point-in-time
  gates Partial, and regenerated shared documents. An interrupted verification
  call left its output unavailable; inspected state and reran the full suite
  rather than treating an interrupted call as a successful check.

Remaining scope: automatic action ingestion/completeness, dividends/total returns,
simultaneous-event review, rights/mergers, listing/entitlement history, execution
accounting, broader calendars and real UDiFF report acceptance. No complete S02
stage or original project phase is claimed.

Full local acceptance after the interrupted call: **167 passed in 29.09 seconds**
(141 existing checks plus 26 new corporate-action cases). Numerical/replay/guard
checks and generated-doc consistency passed. Final UI wording distinguishes the
original-source declaration from the explicit adjusted analysis view. Browser
acceptance and GitHub verification are recorded after observation below.

Final cache-policy check: identical raw/adjusted numerical values can still have
different execution restrictions before an event becomes effective. Made that
policy an explicit computation-cache input, added a mode-switching regression,
and reran the full suite: **168 passed in 30.66 seconds** (27 action checks).
Browser verified two applied events, separate original/source declarations and
raw/factor/audit downloads; the exploratory backtest control was disabled in
adjusted mode. Proof saved locally to `outputs/corporate-actions-verified.png`.

## 2026-11-03 · Split/bonus research published and verified

- Source commit **`3c17469bb15ec48dd2d54e628e7f091688f88110`** published on main
  using an expected-head update from `225977f1b0bc6e34f846957f4908351222dc0025`.
  Repository remains private. All **58 of 58** allow-listed source files were
  fetched at the commit and their blob SHAs matched the reviewed upload objects.
- GitHub Actions run **41683491255**, job **126082987461**, completed successfully:
  **168 passed in 11.06 seconds**. Source run:
  https://github.com/aryankjain11/signal-ledger/actions/runs/41683491255
- Browser checked the optional price/action upload flow using original synthetic
  fixtures, declared raw basis and adjusted mode. The audit showed two applied
  events with ex/known dates and resulting share counts; source and analysis bases
  were separate, original/factor/audit exports were present, and the backtest
  control was disabled. Runtime screenshot/fixtures remain local under outputs.
- Updated sync/README/build evidence after observation. This final documentation
  audit references the verified source snapshot and does not predict its own
  later commit. Source archive is rebuilt and integrity/hash-checked after these
  records, excluding runtime outputs, credentials and user market-data uploads.

Current checklist: **344 tasks — 35 Done, 16 Partial, 281 Planned, 12 Optional**.
Original five-phase mapping remains **8 Done, 18 Partial, 17 Planned** of 43 items.
The new bounded split/bonus research gate is Done; broader corporate-action/data
reconciliation remains Partial. Automatic action sources, dividends/total returns,
composite events, share-accounting execution, wider calendars and real UDiFF
acceptance remain pending. Learning assignments remain paused.

## 2026-11-03 · Feature-value prioritization review

- Owner asked to stop extending file adapters and assess which analytical features
  add the most product value and conceptual learning. Reviewed S03–S12, original
  pattern requirements and current structure/pattern/strategy implementations.
- Recorded the new priority in AGENTS.md. Conceptual learning should happen through
  inspectable product behavior; homework/exercises remain paused. Additional NSE
  corporate-action-download parsing is deferred unless a selected feature needs it.
- Added `FEATURE_PRIORITIES.md`: planned feature inventory, current baselines,
  recommended breakout/retest/failed-breakout lifecycle, an explicit strategy
  follow-through and a subsequent event-study research view. This is a proposed
  development sequence, not a claim that these features have been built.
- No numerical or UI behavior changed and no task was marked Done. Existing
  original-phase counts remain 8 Done / 18 Partial / 17 Planned. Planning records
  are synchronized to the existing private repository; verification is reported
  after the commit is observed. No new software test result is claimed for these
  documentation-only changes.

## 2026-11-04 · Analytical features and two-stock comparison opened

- Owner authorized breakout/retest analysis plus chart patterns, candlestick
  context, momentum and side-by-side stock correlation/comparison. Interpreted
  “reset” as retest from the accepted plan. Bounded first families are explicit;
  no new exercises or event-feed adapters were added.
- Added `ResearchRules` and `research-events/1`: prior-range close/volume breaks,
  frozen level/previous ATR, later held retests, failures, continuation and expiry.
  Added four six-anchor chart formations with frozen fits and diagnostics, six
  context-aware shadow/star candle variants, ROC10/fast stochastic and delayed
  confirmed-pivot RSI/MACD divergences. Events are observations, not new trades.
- Connected the families to chart lines/markers, Patterns & momentum tabs,
  explanation tables, momentum plots, report/evidence and event exports. Kept the
  existing single breakout strategy and action-related execution restrictions.
- Added Compare two stocks: two native CSV/XLSX/NSE uploads or a deterministic
  synthetic pair, shared-period selection, normalized100 performance, common-date
  drawdowns, relative ratio, matched return scatter and Pearson/Spearman/rolling
  correlation. Pair native returns only on identical start AND end dates; no fills.
  Unknown/short/constant cases and source/adjustment declarations remain explicit.
- Side-by-side charts use each file's causal history through the selected end
  for indicators, then crop charts to the chosen period. Two-date comparisons
  remain available while the technical-analysis minimum is separately disclosed.
- Fixed chart weekend hiding: calendar-date axes now preserve special Sunday
  sessions instead of universally removing weekends. Comparison charts have
  unique explicit keys even when uploaded numerical content is identical.
- First new-feature suite: **29 passed, 3 failed in 32.39 seconds**. Two numerical
  failures exposed floating-point tie fragmentation in rank correlation; ranks
  now use returns rounded to12 decimals with that convention exported. The UI
  failure exposed duplicate chart IDs for identical content; explicit keys fixed
  it. Nested event geometry is serialized to strings for readable Arrow tables.
- Follow-up new-feature run: **32 passed in33.04 seconds**. First complete
  regression: **200 passed in99.32 seconds**. Added one final negative formation
  case and explicit fitted diagnostics, and optimized reference-range/anchor
  iteration before the final complete run, whose result follows after observation.
- Added `ANALYSIS_AND_COMPARISON.md`, updated reference entries (122 concepts),
  original-phase scope and shared 349-item checklist. Expanded task labels stay
  Partial where broader definitions/context/validation remain incomplete; five
  precisely bounded feature gates were added. Full source/CI/browser evidence
  follows after verification. No real upload is included in repository fixtures.

Sources checked: Fidelity fast stochastic/RSI, Zerodha Varsity Morning/Evening Star,
and NIST correlation coefficient. Direct references and this implementation's
distinct exact definitions are in ANALYSIS_AND_COMPARISON.md. Statistical pattern
outcomes, strategy comparison, full pattern catalogue, model probabilities and
synchronized chart editing remain pending. Existing exercises remain paused.

Final complete regression after the negative-fit/diagnostic/performance changes:
**201 passed in94.30 seconds** (168 existing plus33 new cases). User-facing
comparison metrics are displayed as percentages; numerical evidence retains
fractional return conventions. Browser acceptance and remote publication follow
after observation. No test result is inferred from the earlier intermediate runs.

Acceptance observed on 2026-11-04:
- Comparison display follow-up: **9 passed in13.88 seconds**. The complete suite
  above plus this focused run cover the final numerical/UI source.
- Live browser: Compare two stocks synthetic pair showed Pearson0.682,
  Spearman0.654, 149 matched return intervals and150 common price dates. Verified
  two technical charts and momentum summaries side by side. Research dashboard
  showed breakout/retest, chart patterns, candlestick context and momentum tabs,
  with rule/evidence/event-export controls. Saved local screenshots
  `outputs/stock-comparison-verified.png` and `outputs/patterns-momentum-verified.png`.
- Published source commit `ce7cd3fcfb0f12c5f3947be2d59e72afde8f53af` on private
  `main` using an expected-head check. Fetched all66 allow-listed files and matched
  each remote blob SHA; binary assets were fetched as base64. Source only, no
  owner market-data files, credentials or runtime screenshots uploaded.
- GitHub Actions run41813021609 / job126516723649 completed successfully:
  **201 passed in23.83 seconds**. Final audit records this already observed source
  result; its own later documentation commit does not claim a predicted CI result.
- Where we stand: requested first analysis/comparison release works; broader
  original stages stay Partial. Next feature priorities are event outcome studies
  and an explicit breakout-retest strategy, followed by strategy comparison and
  remaining pattern families. Existing learning assignments stay paused.
