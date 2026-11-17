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

## 2026-11-05 · After the pattern: descriptive event-outcome research

Authorized milestone: build the accepted event-study feature professionally, with
finance/coding discipline, continuing documentation and private GitHub publication.
Exercises remain paused. Completion gate is numerical timing/selection/coverage
acceptance, replay/UI behavior, auditable exports, synchronized concept/checklist
records and verified source publication, without claiming empirical investment validity.

- Added `quant_engine/event_study.py`, version `pattern-outcomes/1`, and validated
  `StudyRules`. Immutable occurrence snapshots distinguish formation from knowledge,
  preserve lifecycle states, deduplicate copied/same-cohort same-date paths and
  retain actual knowledge-close price/EMA50/RVOL values. Later failure never removes
  an initial breakout; neutral events get no invented direction.
- Implemented fixed observation-horizon movement from next observed open or
  detection close, bearish alignment, complete-window MFE/signed MAE, null censored
  outcomes and separate audited raw action-crossing exclusions. Horizons are
  observed bars, not guaranteed exchange sessions. No prices are filled.
- Added deterministic maximum-horizon spacing within cohorts before examining
  maturity, context/date/subtype filters, descriptive mean/median/quartiles/positive
  frequency, flat counts and small-sample labels. Inter-cohort dependence remains.
- Added same-stock retrospective non-event pools matched on knowledge-close
  EMA50/RVOL buckets. Controls may contain future events, are thinned within
  context pools and are reused transparently. Matched means use identical event
  coverage, preventing a misleading full-sample versus partial-baseline comparison.
- Added **After the pattern** workspace reusing the existing input/replay pipeline;
  form controls, comparison bars, distribution boxes, individual occurrence chart,
  evidence/audit and JSON/outcome/baseline/summary CSV exports. Cached calculations
  include rules/events/data identity; portable records are not a history database.
- Added `docs/EVENT_STUDIES.md` with original formulas, hypothetical examples,
  assumptions, software/record design, sources and remaining research scope. Four
  new reference concepts and two expanded entries yield126 concepts. Updated
  checklist/phase mappings:351 items (43 Done,45 Partial,251 Planned,12 Optional);
  original43 bullets now8 Done,20 Partial,15 Planned. No original phase is complete.
- First targeted acceptance: **33 passed in33.39 seconds**. Added two further
  independent fixtures for matched coverage and missing-date observation horizons,
  and extended replay/UI coverage; full regression was then started. Record its
  observed result below rather than inferring a pass from the earlier subset.

Sources checked 2026-11-05: CFA Institute Backtesting and Simulation, and
EventStudyTools Introduction to event studies. Exact links/interpretation are in
EVENT_STUDIES.md. The implementation is a descriptive pattern-outcome study, not
a market-model abnormal-return/causal event study. No new source data, external
services, orders, calibrated probabilities or invented trading-performance claims.

Remaining: target-before-stop/expiry labels, dependent-data inference, held-out
validation, cross-stock point-in-time universes and persistent research history.
Recommended next usable feature is a versioned breakout-retest strategy with
execution timing, invalidation, exits, expiry and costs, then strategy comparison.

Follow-up verification and corrections:
- First full run: **235 passed,1 failed in109.38 seconds**. The failing replay UI
  assertion exposed empty event selection after the available cohort catalogue
  shrank. Reproduced the state: old event choices disappeared while an earlier
  bearish-engulfing occurrence remained available; no numerical exception occurred.
- Preserve valid selected types when the catalogue changes; if none remain, reset
  to available defaults with an explanation. Clamp event dates to the visible
  observed range. Added explicit replay assertions and four independent three-bar
  extreme/reference/direction fixtures. Follow-up event suite: **39 passed
  in26.80 seconds**.
- Improved comparison readability with horizontal grouped bars; occurrence charts
  now have percentage movement/excursion metrics and collapsed exact JSON. Corrected
  synthetic adjustment labeling to use Synthetic example, rather than the unused
  unknown declaration, across the shared data flow. Baseline audit distinguishes
  candidate anchors before spacing from retained anchors.
- The final full suite and live-browser acceptance follow after observation.

Final full local regression observed: **240 passed in92.41 seconds** (201 existing
plus39 event-study cases). This includes final replay/form fixes, synthetic basis
labeling, outcome math, context feature exports and updated audit anchor counts.
No further numerical/UI source changes were made after this run. Restarted the
local app to clear previously imported UI modules before final browser acceptance;
ordinary page reload had retained the old chart orientation in that process.

## 2026-11-06 · Event-study live acceptance and verified publication

Implementation and full local testing were completed2026-11-05; the following
publication/verification records use the client's Asia/Calcutta date2026-11-06.

- Live synthetic default:21 included occurrences,6 overlap exclusions,6 event
  types and19 complete outcomes at20 observations. Verified grouped comparison
  bars, matching explanations, known-time occurrence chart and percentage metrics.
  Example one-observation movement−1.51%, MFE1.05%, signed MAE−2.55%,14 matching
  controls are synthetic fixture observations, not stock-performance claims.
- Downloaded the actual JSON through the page and parsed it: schema
  `pattern-outcomes/1`; run915927ac1497a0c132b008ce6d98b3ba1843fd29dab49b2ca9746baae4aabb93;
  272 occurrence decisions,84 outcome rows,536 control rows and24 summary rows.
  Verified source basis Synthetic example and null movements for incomplete rows.
  Kept `outputs/verified-synthetic-study.json` locally, outside the publication list.
- Saved `outputs/event-study-comparison.png` and `outputs/event-study-occurrence.png`.
  An additional optional browser action timed out in automatic approval, explicitly
  not a determination of unsafe action. Continued independent authorized connector
  work. Browser approval recovered; one allowed retry of occurrence inspection
  succeeded. No browser security controls or approval checks were bypassed.
- Published source commit `d931316367a204664bc618a9e650a47e0cf3f28b` on private
  main with the expected previous-head check, without force. Reconstructed only the
  reviewed70-file source tree; fetched every file at the resulting commit and
  matched its Git blob SHA. Source credentials scan passed. No owner uploads,
  environment, runtime study records or screenshots were committed.
- Remote Actions run42098482104 / job127494694051 completed successfully:
  **240 passed in15.74 seconds**. Repository private visibility reconfirmed.
  The connector's combined-status wrapper omitted Actions checks and its workflow
  list is PR-only; found the push run through GitHub's visible Actions page, then
  verified its job/log using the connected GitHub tools.
- This final documentation audit records the observed source/CI snapshot; its own
  later commit does not predict its own CI result. Current state: bounded event
  study complete, broader phase4 research database/inference/validation Partial or
  Planned as recorded in PROJECT_STATUS.md. Next: versioned breakout-retest
  execution strategy, then fair strategy comparison. Exercises remain paused.

## 2026-11-15 · Researcher walkthrough and full product inspection

- User requested a very thorough inspection/report for human and AI readers:
  vision, current functionality, missing capabilities, user friendliness, routine
  workflows, defects, progress and a plan. This was an audit/documentation increment;
  analytical source and existing tests were left unchanged.
- Read original brief, refined plan, current status, shared checklist/concepts,
  source and prior acceptance records. Relaunched local loopback app. Fresh
  regression: **240 passed in99.08 seconds**. Reconfirmed private repository;
  all70 audited files matched commit `6a64fed3f28fa397ed889417eb84fa73d911eb9f`.
- Browser-inspected all five workspaces, default synthetic analysis/backtest,
  candle explanations, unchanged owner-provided NSE upload and completed-session
  gate, short-history/freshness details, two-stock comparison, event inspection,
  reference search and build journal. Kept real upload out of screenshots/report
  artifacts intended for sharing. No source market-data rows were published.
- Actual synthetic JSON downloads parsed: comparison/labels/passports object and
  study schema/outcomes84/controls536/summary24 with null incomplete returns.
- Eleven supplemental probe groups covered CSV/XLSX parity, five invalid-input
  classes, original NSE parsing, narrow chart bounds, cost sensitivity, backtest
  state, navigation context, study empty/neutral modes, comparison short period
  and UDiFF synthetic preview. Probe script/results stay in excluded runtime outputs.
- Reproduced F01: selected three-candle window beginning2023-03-28 still draws
  older double-pattern/breakout coordinates. Reproduced F02: completed backtest
  output disappears after an unrelated overlay toggle. Documented repair gates;
  no repairs were claimed or made during the inspection.
- Corrected an early audit probe that used a positional number-input selector;
  label-based probe confirmed account capital and research label survive the
  tested workspace round trip. First last-ten-demo-date chart probe had no active
  out-of-window pattern; a deliberately pattern-containing narrow window exposed
  F01. Neither probe correction is an application defect.
- A390x844 viewport request was ineffective: actual browser stayed1280x720;
  reset override and explicitly left mobile acceptance unverified. Keyboard search
  was exercised, not a full screen-reader/accessibility audit. No penetration,
  production multi-user, fresh-machine or full50,000-row UI acceptance claimed.
- One uncached5,000 repeated-synthetic-bar computational probe:9.852s analysis,
  7.780s event study; no exception. This excludes browser rendering and is not a
  load/scalability guarantee. Data are artificial, not market observations.
- Added `PLATFORM_INSPECTION_2026-11-15.md`, `PLATFORM_CONTEXT.md`, linked from
  README and current build records; retained351-task/126-concept software status.
  A readable HTML companion with synthetic screenshots is generated locally.
  Next recommendation: chart/state/readiness fixes, then breakout-retest execution
  strategy, saved research and independent validation. Exercises remain paused.
- Source publication and final artifact checks are recorded after observation;
  this entry does not predict remote CI or claim a newly implemented feature.

Inspection delivery acceptance:
- Detailed report:12 main sections, approximately7,000 words, feature/workspace
  inventories,15 findings/maturity gaps,33-row check matrix and18 original
  acceptance-criterion mappings. Compact continuation brief written separately.
- HTML companion visually checked in the browser; section navigation and findings
  table rendered correctly. Validated all internal section links and two embedded
  synthetic/reference screenshots. Actual comparison JSON confirms149 paired
  intervals and two source passports. No mobile result was mislabelled as passed.
- Published documentation commit `e4f6adccc0e05ec3573f5f74977c8d6b6267430b` on
  private main with an expected-head check. All72 files fetched and blob-SHA
  matched. No analytical source/test changes, uploaded data or runtime artifacts
  included. Documentation-only remote CI not separately observed; local240-test
  result and historical feature CI remain distinct evidence.
- This final synchronization record references the observed documentation commit;
  its own later commit is an audit, not a prediction of its CI. Open findings are
  documented, not fixed. Original351-task software completion counts are unchanged.

## 2026-11-15 · Research reliability and connected workflow

- Owner authorized the next recommended milestone after the inspection. Bounded
  scope: chart-window correctness, immutable baseline session retention/staleness,
  visible data readiness/actual counts and task/reference links. The dedicated
  breakout-retest strategy remains the next major feature. Exercises stay paused.
- `charts.py` clips line segments to visible dates, separates original-anchor
  markers from interpolated drawing vertices, filters unavailable detections and
  fixes shared date axes with half-day edge padding. The caption uses actual
  displayed/total counts. Full original coordinates remain in analytical evidence.
  No detector thresholds or numerical simulator rules changed.
- Added pure `saved_backtest.py` and UI renderer: immutable original evidence,
  assumptions, metrics, trades/equity and downloads in one session slot. Identity
  includes actual baseline inputs/source/replay/basis/policy/settings; display
  overlays and separate descriptive rules do not invalidate this fixed strategy.
  Changed inputs retain the old result under an explicit stale warning. New runs
  remain blocked by execution restrictions. No durable history database is claimed.
- Added `readiness.py`: actual final-value availability, minimum-history recovery
  counts, undefined-value reasons, weekly/structure/baseline context, freshness,
  calendar flags, basis and execution scope. A21-observation input explicitly
  needs29 more for EMA50; an available calculation is not a trade or source audit.
- Added task pills, direct concept shortcuts and observation selection → cohort
  study → fixed-baseline-tab routes. Diagnostic lifecycle states cannot create
  unsupported studies. Neutral study requests use upward price change. Scope labels
  distinguish descriptive detector settings, gross event outcomes and cost-bearing
  baseline simulation. Avoided a default/session-value collision in the study slider.
- Browser found research sidebar inputs reset after a reference-page visit. Moved
  their rendering before reference/comparison/checklist branches; uploaded file,
  completed-bar declaration and monetary assumptions now survive those routes.
  Non-sidebar replay/rule/action state is not a full saved workspace: documented
  separately. Comparison labels its independent two-dataset controls explicitly.
- Added128th/127th shared concepts (readiness and saved/stale results), original
  examples and four bounded S15 Done gates. Regenerated shared docs. Current counts:
  **355 tasks:47 Done,45 Partial,251 Planned,12 Optional;128 concepts**. Original
  43-bullet mapping remains8 Done,20 Partial,15 Planned. Added detailed
  `RESEARCH_RELIABILITY.md`; updated README, build/context/priorities and the dated
  inspection's follow-up/erratum without rewriting the historical observations.
- Tests actually run: initial app/study smoke5 passed in12.56s; first new suite
  27 passed/1 failed in19.09s because the test chose the first checkbox (an action
  ledger), not Show Bollinger bands. Corrected the selector by label;28 passed
  in18.47s. The original audit supplemental probe had the same interaction-label
  mistake. Correctly labelled reproduction against pre-change publisheda482bc7
  confirmed completed-trade output before the overlay toggle and none after,
  with zero app exceptions. The finding was valid; initial interaction evidence
  was inaccurate. Erratum is explicit in the inspection and reliability document.
- Subsequent restricted test attempts stalled before application execution in
  Python Windows asyncio/socketpair initialization. Full-suite result retrieval
  from an earlier session was unavailable; no pass was inferred from empty cache.
  A run permitted local communication: **268 passed in53.80s** (all240 prior
  cases plus28 new reliability cases). Closed only the identified stalled pytest
  processes. This was an execution-environment problem, not an app failure or an
  approval-service capacity/safety rejection.
- Browser checks:600-row synthetic analysis, overlay/cost-stale retained record,
  visible original10-bps assumptions alongside current25-bps input, top navigation,
  direct RSI article, original unchanged21-row NSE upload, partial readiness and
  true21-of21 caption, upload retention on Education round trip, keyboard-selected
  observation cohort and baseline-tab handoff. The synthetic fixture's5 trades
  demonstrate software only. Real upload rows/screenshots were not published.
  Two synthetic proof screenshots stay in excluded `outputs/reliability-2026-11-15/`.
  Actual mobile/accessibility and production concurrency remain unverified.
- Reference checks: official Streamlit session-state and pandas windowing docs,
  linked in `RESEARCH_RELIABILITY.md`. Application-specific counts/identities are
  documented as tested project conventions rather than library trading rules.
- Next verification: generated-catalogue regression, source/privacy allow-list,
  private GitHub upload/tree verification and actual remote CI if available.
  These publication results are recorded only after observation below.

Reliability delivery acceptance:
- Regenerated catalogue/handbook/status consistency and reference/build UI:
  **15 passed in6.46s** after the catalogue changes. Counts independently checked:
  355 tasks (47/45/251/12) and128 concepts. Source allow-list/credential scan passed.
- Published `6cac2f8be5fc8f04c6d780410f9bf6931713ac88` to private main with an
  expected-head check and no force. All78 source files fetched at that commit and
  matched to local Git blob SHAs. Changes:24 new/modified reviewed files; original
  numerical detector/simulator source unchanged. No owner-uploaded data or runtime
  screenshots/records included.
- GitHub Actions run43728863777 / job132856650486 completed successfully:
  **268 passed in23.13s**, Ubuntu26.04 / Python3.13.18. Inspected the completed job
  and decoded log. General GitHub GET now supports discovering this push run by
  head SHA; older PR-only workflow-list wrapper remains a separate limitation.
- Updated sync record and README to reflect these observed results. This final
  documentation commit follows the verified source snapshot; it does not predict
  its own remote CI. The milestone is complete at its bounded gates; the next
  feature is the versioned breakout-retest execution strategy, then fair strategy
  comparison. Durable history/reopen, independent validation and wider catalogue
  remain planned. New exercises remain paused.

## 2026-11-15 · Breakout-retest strategy implementation begins

- Owner requested the next feature and emphasized correctness. Read continuing
  agreement, current checklist/log, descriptive detector and baseline simulator.
  Work is bounded to one versioned long daily strategy with website/audit/exports;
  fair comparison and independent validation follow separately.
- Wrote `BREAKOUT_RETEST_STRATEGY.md` before implementation: frozen prior range/ATR,
  later close-confirmed retest, one next-open attempt, structural stop, gap/level
  cancellation, target/cost/risk/cash/volume rules, single setup/position capacity,
  expiry and explicit no-trade/boundary outcomes. Numerical/causal/UI gates remain
  unaccepted until actual results are recorded below. No live execution or new
  assignments. Official Fidelity/CFA references checked; exact thresholds are
  project choices rather than externally validated trading rules.

Breakout-retest implementation and local acceptance:
- Added pure `retest_strategy.py` with validated immutable RetestRules, frozen
  prior range/ATR, later close-confirmed retest/EMA50, one next-open attempt,
  structural stop, actual-fill target and shared cost-aware whole-share sizing.
  One setup/position; no same-bar restart. Audits rejected trend, lost level,
  excessive gap, invalid stop, nonpositive net reward, zero quantity, expiry and
  busy capacity. Observed attempted open and permitted gap limit are retained.
- Preserved the original `strategy.py` baseline engine unchanged. Reused its
  sizing convention and matched exit precedence/cost/marked-equity conventions.
  Pending setups remain pending at cutoff; forced open-position liquidation is
  explicitly counted and stays out of the natural transition tape. Current state
  captures the position before that artificial exit. Gaps can exceed planned risk.
- Added immutable `retest_records.py` schema breakout-retest-run/1 with actual
  rules/execution settings, source/basis/policy/visible-feature identity, provenance,
  original prices, decisions, transitions, equity, trades and cutoff state. Identity
  excludes unrelated descriptive rules and unused baseline stop/lookback settings.
  Execution policy is checked in engine, builder and UI. Downloads/charts always
  use the saved snapshot, including when stale; no durable database/reopening claim.
- Added `retest_ui.py` and strategy selection in Backtest lab, separate session
  slots, meaningful no-trade/pending explanations, human-readable audit/ledger
  headings, exact-evidence expander and frozen-price setup inspection. Event-study
  links select the intended simulator. Added131st–129th concepts for strategy,
  structural risk and entry cancellation with original hypothetical examples.
- Initial numerical suite:36 passed/1 failed in2.35s. Empty event output lacked
  headers in the prefix comparison; fixed stable table schemas for empty exports.
  After an added boundary case:38 passed in5.48s, with5 pandas null-comparison
  warnings. Explicit numeric event columns removed the None/NaN mismatch.
- First combined new suite:52 passed/1 failed in25.35s. The added strategy radio
  exposed an old positional Data source selector; the test changed the wrong
  widget. Replaced only those selectors in existing upload/calendar/action tests
  with the explicit label; no original expectations were relaxed. New plus app/
  action regression then **84 passed in30.73s**.
- Broader intermediate checks after new chronology/record cases: **322 passed
  in75.45s**, then **322 passed in74.31s** after attempted-open audit additions.
  Browser inspection motivated a smaller cancelled-setup chart window, readable
  ledger headings and visibility of a target when entry/exit share a date. Frozen
  level/stop/target display begins when each becomes known rather than projecting
  execution levels backwards. Source input and numerical trade rules unchanged.
- Browser reference/upload gates exposed selected-strategy cleanup when its widget
  was absent. Explicitly preserved that widget key across omitted controls; retest
  rule values also survive strategy switching. Added a regression for missing-file
  and reference routes. Other main replay/action state remains a separate broader
  workspace-persistence scope, not silently claimed complete.
- Final full suite: **323 passed in84.15s**, all268 existing +55 new. After final
  target tick color adjustment, focused saved-record/inspection check **1 passed
  in4.35s**. Tests cover independent P&L/equity arithmetic; risk/cash/prior-volume
  caps; fixed references; no hindsight entry; every-prefix natural event invariance;
  same-bar barriers; adverse/favorable gaps; exact expiry/hold/open boundaries;
  negative/undefined/no-trade cases; execution policy; all strategy-rule identities;
  immutable strict JSON; stale saved charts; UI switching, replay and concept routes.
- Browser: default synthetic strategy5 setups/4 trades/1 entry cancellation;
  inspected cancelled and stopped trade charts, audit/transitions/ledger, changed
  holding rules/stale warning and restored matching rules, concept and strategy
  retention. Original unchanged21-row NSE upload ran with0 trades,0 ready-context
  observations and unavailable win rate; it was not presented as evidence of a
  losing strategy. Actual downloaded JSON parsed: schema1,600 synthetic bars,
  5 decisions,4 trades, frozen rules and attempted/maximum open fields present.
  Runtime download and proof screenshots remain local/excluded. A few browser
  actions hit transient Streamlit rerun/duplicate-tab states; fresh state and the
  completed rerun resolved them. No automation workaround changed source data.
- Generated shared docs; current counts357 tasks (50 Done,48 Partial,247 Planned,
  12 Optional),131 concepts. S08 breakout-retest gate Done; broader registry/order/
  stop families remain Partial/Planned. Original43 bullets still8/20/15; no full
  phase, strategy superiority, calibrated probability or learner mastery claimed.
- Updated strategy specification, README, current build/context/priorities and
  historical-inspection follow-ups. Next: fair baseline-versus-retest comparison
  under a declared protocol, followed by independent chronological validation and
  durable research storage. Private publication/CI are recorded after observation.

Breakout-retest publication acceptance:
- Published source commit `98f097bf0dce83f735ec24153e6c49104b1b3ec5` on private
  main with the expected previous head55a80bb and no force.28 files new/modified;
  final84-file Git tree paths and every blob SHA matched the reviewed local
  manifest. Verified branch head. Original baseline simulator SHA unchanged;
  existing tests changed only their Data source selectors where necessary.
- GitHub Actions run43740352903 / job132891933822 completed successfully:
  **323 passed in49.59s**, Ubuntu26.04 / Python3.13.18. Inspected completed job
  and decoded log. Generated handbook/checklist/original-plan files were also
  directly compared with their shared sources. Credential/source allow-list passed.
- Packaged84 reviewed files plus SOURCE_MANIFEST.json; ZIP member-integrity and
  every SHA256 check passed. Actual NSE file, browser JSON downloads, screenshots,
  environments and credentials excluded. Runtime proof images remain local.
- Updated README and GITHUB_SYNC with observed source/CI evidence. This final
  documentation audit is later than the accepted source snapshot and does not
  claim its own future CI result. Bounded strategy milestone complete; next is fair
  comparison, then independent validation and durable research storage. No trading
  edge, full phase completion or learner mastery is claimed. Exercises stay paused.

### 2026-11-15–16 · user-flow audit and bounded usability improvements

- Request: inspect whether the site works as intended and reduce the researcher's
  effort. Kept this a workflow/reliability increment; fair strategy comparison
  remains the next feature. Read continuing project instructions and current
  inspection, checklist, build records and source before editing. All five
  workspaces inspected. No subagents, new exercises, paid services or live orders.
- Fresh baseline: **323 passed in90.96s**. Browser reproduced research replay
  17 April becoming18 April after Education and comparison window10 resetting20.
  Source/automated probes also exposed omitted file-picker and action state risks.
- Added `ui_state.py`: immutable in-session upload copies, exact filename/content
  confirmation signatures, retired-picker generations and render/workspace/source
  guards, explicit clear, per-source observed-date context/clamping, date reset,
  valid-option guards and selected-tab preservation. Kept source files unchanged.
- Retained research/descriptive rules, strategy selection/rules, committed study
  definitions, comparison mode/window/labels/basis/ranges and relevant tabs through
  tested reference routes. Data confirmation resets when the actual files change.
  Retained action ledger/research view still blocks unsupported execution.
- Compacted landing layout; collapsed capital/risk/costs and advanced detector/
  action settings while showing a monetary summary. Synthetic basis no longer
  conflicts with Unknown. Explain label-only symbol input and scope of settings.
  Reference defaults to searchable library with clear filters and exercise-free
  displayed articles. Existing optional labs/lessons remain; no new assignments.
- Made strategy ledgers lead with readable entry/exit/shares/P&L/reason. Outcome
  axes/titles explicitly label gross movement direction and observation horizon;
  both event/baseline hovers show matched/complete/selected event coverage, and
  distribution titles show actual n. Raw numerical/export definitions unchanged.
- First focused existing suite:57 passed/1 failed in50.05s. Date helper created a
  single-handle prototype when a range was initialized through state alone.
  Explicit range default corrected it; targeted comparison/study2 passed in30.40s.
- Initial new usability runs:10 passed/1 failed in55.74s, then11 passed/1 failed
  in56.07s. These failures came from a new test changing form widgets through
  separate reruns without submitting the combined definition. Corrected the test
  to submit all intended edits together; focused1 passed in17.02s. Expectations
  were not relaxed. Intermediate complete regression: **335 passed in214.51s**.
- Real browser acceptance then exposed an empty cleanup callback erasing cached
  comparison bytes after a reference visit despite the earlier mocked-picker test.
  Added generation/context guards and a separate stale-callback/current-removal
  regression. A running process collected an earlier test edit before its trailing
  block was relocated:12 passed/1 failed in45.06s; rerun of corrected isolated
  callback test **1 passed in5.08s**. This was a test-source timing error, not a
  new application failure. Final suite must be read from the later entry below.
- A final browser check found latest-date recovery changed analysis to600 rows
  but left the visible slider at the earlier date. Replaced delete/default-only
  recovery with explicit state synchronization. Strengthened the regression to
  assert outgoing set_value and its actual date. Focused1 passed/1 failed in31.26s
  because the new assertion initially expected a numeric index; pinned runtime
  serializes date strings. Corrected expected raw value to2025-04-18.
- Browser acceptance after fixes: two synthetic uploads retained through Education
  with window10 and completed declaration; explicit Clear Stock A removed its
  session copy and requested both files; actual comparison JSON download parsed
  successfully (4,856 bytes; comparison/labels/source_passports). Evening Star
  search visibly returned3 related entries and selected its contextual article.
  Research reference return preserved replay and Backtest tab. Latest recovery
  visibly synchronized slider599/date2025-04-18 and600-row analysis. Saved baseline/
  retest success observed; final screenshot saved locally under outputs. No owner's
  real dataset was uploaded again or included in publication during this audit.
- Browser tools encountered short CDP/selector deadlines and stale intermediate
  Streamlit snapshots; fresh completed states resolved them. Do not count these
  automation failures as site crashes. Windows restricted AppTest socket startup
  still needs the authorized local test runner; no runtime dependency was changed.
- Updated saved-result reference scope (still131 concepts), added four bounded
  S15 acceptance gates and regenerated handbook/checklists/status. **361 tasks:
  54 Done,48 Partial,247 Planned,12 Optional**; original43 bullets unchanged at
  8 Done/20 Partial/15 Planned. No whole phase, mobile/accessibility certification,
  durable history or predictive/trading validation is claimed.
- Added `USABILITY_REVIEW_2026-11-16.md`; refreshed current build/context/priorities
  and README. Compared source manifests: original strategy/retest/event-study/
  comparison/indicator/parser engines unchanged. Source allow-list excludes owner
  uploads, runtime files/screenshots/downloads, environments and credentials.
- Sources: local pinned Streamlit1.66.1 signatures/implementation, official widget
  behavior https://docs.streamlit.io/develop/concepts/architecture/widget-behavior
  and file uploader https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader.
- Next: final full regression, reviewed private publication/file verification and
  observed CI; then fair declared strategy comparison, independent validation and
  durable saved research. Learning exercises remain paused.

Usability local acceptance ·2026-11-16:
- Final complete regression after picker/date fixes and catalogue regeneration:
  **336 passed in211.85s**, all323 existing cases plus13 new usability cases.
  This includes the corrected date serialization/outgoing-set-value assertion
  and stale-picker-versus-native-removal case. No failing checks remain in this run.
- Bounded workflow gate accepted.87 reviewed source files are prepared for private
  publication (three new files: UI-state helper, usability tests and dated report).
  Actual publication/remote CI evidence will be recorded after observation.

Usability publication acceptance ·2026-11-16:
- Published source commit `48c9b9d44f70cec696f8ad53dc49e5b78605fe23` on private
  main from expected previous headb85a206, without force.23 new/modified files;
  all87 final tree paths/blob SHAs match the reviewed local manifest. The branch
  update returned success:true (rather than a ref object); the subsequent explicit
  branch/tree read verified the actual result. No automatic approval rejection.
- GitHub Actions run43748677879 / job132917552071 completed successfully:
  **336 passed in57.30s**, Ubuntu26.04.1 / Python3.13.18. Inspected completed job,
  matching source head and decoded log. Local final acceptance remains336 passed
  in211.85s; these are distinct executions. All three generated records were
  additionally compared directly against their shared source functions.
- Archive87 reviewed files plus SOURCE_MANIFEST.json passed ZIP member integrity
  and every SHA256 check. Verified repository metadata remains private. Actual
  datasets, runtime records/screenshots/downloads, environments and credentials
  excluded. Archive is rebuilt after the final documentation update.
- Updated README and GITHUB_SYNC with observed source/CI evidence. This later
  documentation audit does not predict its own future CI. Bounded usability gate
  complete; no whole original phase or investment-performance claim. Next feature:
  fair declared strategy comparison, then independent validation and durable saved
  research. Original43 bullets8 Done/20 Partial/15 Planned;361 expanded tasks
  54 Done/48 Partial/247 Planned/12 Optional. Exercises remain paused.

## 2026-11-16 · complete context and portable handoff for another assistant

- Owner request: preserve the entire project context for another AI assistant as
  the current subscription ends; refer to the first prompt, original vision,
  changes, work done, remaining work and deliver all necessary continuation files.
  This increment prepares the transfer; it does not implement the next strategy
  feature or change numerical behavior.
- Read original brief/attachment, current architecture/source/settings/specs,
  phase/task/concept catalogues, chronological log and publication record.
  Original attachment and `docs/ORIGINAL_BRIEF.md` are byte-identical:50,000 bytes,
  SHA256 f2c7c3286b7fcd14725b2412f8af5a3dcbad227de38a509626a437173442f160.
- Independently verified private repository main at0442e36912ca37bcb34d03760b61d82280745a55,
  matching all87 local reviewed files before edits. Its push run43749507116 was
  observed completed/successful; no new test count inferred without its log.
  Accepted application evidence remains local336/211.85s and source CI336/57.30s.
- Added detailed `AI_HANDOFF_2026-11-16.md`: original section-by-section vision,
  owner steering/timeline, exact current inputs/indicators/timing/strategies/research,
  five-page user journey, architecture/source map, tests, repaired/open issues,
  remaining43-phase/361-task scope, safe data/privacy boundaries, setup/migration
  and instructions for a replacement assistant. Historical notes distinguished
  from current scope; no fabricated complete chat transcript or learner mastery.
- Added `NEXT_ASSISTANT_START_HERE.md` with a reusable continuation prompt and
  reading/verification order. Added `NEXT_MILESTONE_STRATEGY_COMPARISON.md` as an
  explicitly unimplemented proposal: frozen engines, common protocol and coverage,
  warm-up/evaluation/cutoff policies, immutable evidence, metrics and acceptance.
- Added standard-library `scripts/package_handoff.py` using the existing reviewed
  source allow-list/credential scan. Builds a dated portable ZIP with project
  source/tests/synthetic/docs, startup guide, full machine-readable roadmap/phase/
  concept index and source hashes, source/package manifests and read-only verifier.
  Excludes environments, credentials, real uploads, licensed data and runtime output.
  Source snapshot does not include Git history; private repository retains it.
- Refreshed README/current build/context entry points. No financial engine, app UI,
  dependency pin, shared status or concept content changed. Remains131 concepts,
  361 tasks54/48/247/12; original43 bullets8/20/15. Exercises remain paused.
- Preliminary package:91 reviewed source files,96 members. ZIP integrity and every
  payload SHA256 passed. Final contents/digest are regenerated after verification
  and publication; no preliminary archive hash is claimed as the final artifact.
- Next: verify extracted portable checker, relevant documentation checks, reviewed
  private publication and final branch/tree/package identities; then deliver the
  archive/report/prompt/spec. Recipient must verify its own environment and any
  later owner edits before building. Detailed financial research validation remains
  separate from software acceptance and from the archive's integrity checks.

Handoff local acceptance:
- Relevant documentation/reference regression: **15 passed in12.03s**. No financial
  or app behavior changed, so the earlier full336-case acceptance remains separately
  dated evidence rather than a fabricated new full run.
- Rebuilt/extracted91-source-file,96-member ZIP. Standalone read-only verifier
  checked95 manifest payload files successfully. Deliberately changed the extracted
  README only: verifier returned failure and named that path. Restored bytes and
  verified success again. No original project file/data was altered by the probe.
- Source allow-list/credential scan passes. Final archive will be regenerated after
  observed publication so its checkpoint and all final file hashes are accurate.

Handoff publication acceptance:
- Published `ee2244147b72c0c1a8db3b2ca6bda1091355f9c0` from expected head0442e369
  without force;9 new/modified paths,91 reviewed files, no source removals. All
  final Git tree paths/blob SHAs matched the reviewed local manifest. App, numerical
  engines, tests, concept/status sources and pinned dependencies unchanged.
- Fresh GitHub Actions run43911784583/job133455309551 completed successfully:
  **336 passed in37.68s**, Ubuntu26.04/Python3.13.18. Completed job and decoded
  log inspected. Local handoff checks remain15 passed in12.03s plus archive/
  extraction/verifier/negative integrity acceptance; no fresh full local run claimed.
- Updated this log, full handoff report and sync record with observed evidence.
  These later documentation changes do not predict their own CI. Final private
  branch/files and regenerated portable archive are verified before delivery;
  PROJECT_SNAPSHOT.json records the actual final published head. All necessary
  source, tests, original brief, reference/roadmap records, starter prompt and next
  milestone proposal are included. Real uploads, credentials and runtime probes
  remain excluded. No new feature gate or original phase was marked complete.

## 2026-11-16 · Product pass: ticker data, Market read, H&S, navigation (new assistant)

Context: owner moved the project to a new assistant and asked for a fundamental
inspection, decluttering and feature progress toward the original brief.

Baseline verified first: handoff archive integrity OK; fresh environment
(Python 3.13.18, pinned deps); **336 passed**; all five pages loaded in a real browser
with no exceptions.

Assessment: engines (causal timing, costs/gaps, no invented probabilities) are sound.
Effort had drifted toward process documentation; user-facing gaps vs brief §2/§7/§14:
no ticker entry (the "Research label" box looked like one but fetched nothing), no
bullish/bearish/conflicting summary, no head-and-shoulders (acceptance criterion 8),
limited indicator catalogue, developer checklist exposed as a user page, heavy caveats.

Changes:
- `quant_engine/providers.py`: ticker → Yahoo Finance (yfinance 0.2.66) daily history,
  NSE/BSE suffix mapping, invalid-price rows dropped and counted (never filled),
  still-forming session excluded before 18:00 IST, rounding-only OHLC containment
  (<0.0001%) disclosed, then the normal `load_bars` validation/passport path.
  Declared basis "Split-adjusted by provider; dividends not adjusted" (added to the
  passport allow-list; corporate-action adjustment stays blocked so splits are not applied twice).
- `indicators.py`: ADX/±DI, Supertrend(10,3), Donchian20, Keltner(EMA20±2ATR) and
  squeeze flag, A/D line, CMF20, MFI14, rolling VWAP20, Williams %R, CCI20, Stoch RSI,
  20-session annualized volatility, ATR %, 52-week high/low. ADX, +DI, CCI, MFI,
  Williams %R and CMF matched the independent `ta` library to ≤5e-10 after warm-up.
- `research.head_shoulders`: H&S and inverse from five alternating confirmed pivots;
  knowable at right-shoulder confirmation; neckline frozen then; developing →
  confirmed break / invalidated beyond head / expired (40). Flows into Pattern research.
- `market_read.py`: one vote per family (structure, trend, momentum, volume flow,
  weekly, recent patterns); correlated indicators combined inside a family first;
  ADX/stretch/volatility shown as non-voting context; verdict labelled heuristic,
  `probability=None`. Key levels with % and ATR distances. Added to the report.
- UI: four pages (Analyze · Pattern research · Compare stocks · Learn); developer
  checklist only at `?page=build`. Data source: Fetch by ticker (default) / Upload /
  Demo / NSE reports (demo reports now a checkbox). Header + Market read first; chart
  overlays, lower-panel selector and range control; equity curves scaled to their
  range with drawdown; Compare can fetch two tickers; duplicate sections and
  repeated caveats removed; Streamlit deploy toolbar hidden; friendlier fetch errors.
  Data/Settings sidebar shown only where it applies.
- Tests: `test_providers.py` (13, incl. offline AppTests with stand-in provider),
  `test_extended_analysis.py` (7: causality on truncated data, ranges, H&S lifecycle
  and no-repaint, market-read invariants). `conftest.py` defaults app tests to demo
  data and clears st.cache_data per test. Existing tests updated only for renamed
  labels/widgets; no numerical expectation was changed.

Verification: **356 passed** locally. Browser walkthrough of every tab/page, both
backtests, round trip Analyze→Learn→Analyze (source and saved backtest retained).
Limitation: live Yahoo fetch could not be exercised from the build sandbox (no
outbound access); first live run on the owner's machine is the remaining check.

Next: multi-timeframe confirmation inside the Market read; flags/wedges/cup-and-handle;
cross-stock pattern database (run Pattern research over a watchlist) for larger samples;
fair baseline-vs-retest comparison; persistent analysis history.


## 2026-11-17 · Hosted on Streamlit Cloud; multi-timeframe read; Scanner

Deployment: pushed to `aryankjain11/signal-ledger` (02aa2f5) from the owner's laptop and
deployed on Streamlit Community Cloud. First boot failed (`ModuleNotFoundError: plotly`)
because the host used Python 3.14 and `pandas==2.3.2` has no 3.14 wheel, so the whole
requirements install failed. Pinned `pandas==2.3.3` (5222514); verified wheels for
3.12/3.13/3.14 and the full suite on Python 3.14.6. Live Yahoo fetch confirmed working
from the hosted app (owner screenshot, SBIN).

Changes:
- `timeframes.py`: completed monthly bars (forming month dropped, like weeks); per-timeframe
  trend vote (close vs EMA20, EMA10 vs EMA20, Supertrend; majority rule) and swing structure;
  `alignment_verdict` covers aligned / counter-trend / pause / conflict / unavailable.
- Market read: the weekly-only family became **Higher timeframes** (monthly + weekly, one vote;
  disagreement or sideways votes neutral). Timeframes strip on Overview; table in the report.
- **Scanner** page: NIFTY 50 preset (as of 30 Sep 2026: BSE in, WIPRO out, per NSE Indices'
  10 Aug 2026 notice; constituents from a published weight list dated 29 Sep 2026) or custom
  list (max 100). Parallel fetch, sequential analysis with the same engine; failures isolated
  as error rows; results cached 1 h; filters, CSV export, "Open in Analyze".
- Fixes: tickers containing `&` (M&M) were rejected; calendar notice is now a specific caption
  (counts + dates) instead of a generic warning; metric values no longer truncate.
- Tests: `test_timeframes.py` (aggregation, forming-period exclusion, unavailable on short
  history, every alignment case), `test_scanner.py` (parsing, default list validity, row =
  single-stock analysis, failure isolation, page run, open-in-Analyze). **371 passed**.
  Browser walkthrough with a stand-in provider: Analyze (timeframes) and a 50-stock scan.


## 2026-11-17 · Watchlist-wide pattern research (pooled)

- `pooled_study.py`: runs the unchanged single-stock `build_study` per symbol (own detectors,
  knowledge-date timing, overlap thinning and the stock's *own* non-event baseline), then
  stacks outcomes. Per cohort × horizon: events, stocks, distinct dates, top-stock share,
  mean/median/quartiles, share in the pattern's direction, MFE/MAE, matched baseline
  difference, and a 90% interval for that difference from a bootstrap that resamples whole
  event dates (shown only with >= 30 matched events on >= 20 dates). Sample notes flag
  small, concentrated (>40% from one stock) or heavily date-clustered cohorts.
- Pattern research page: "This stock" (default; unchanged) / "Watchlist (pooled)" switch.
  Pooled view: results table, difference chart of rows with a range (bright = excludes
  zero), a multiple-comparisons notice ("M of N exclude zero; ~N/10 expected by chance"),
  drill-down by stock + outcome histogram, coverage, CSV, method and limits (incl.
  survivorship bias of today's index list).
- Verification: `test_pooled_study.py`. A one-stock pool reproduces the single-stock summary
  exactly; duplicating a stock doubles events but leaves distinct dates and the interval
  unchanged (date clustering works), while relabelling the copies as new dates would wrongly
  narrow it; thresholds, cohort filter, failure isolation; end-to-end page test (2 of 3 stocks,
  one fetch failure). **Null check** on 50 random-walk stocks (5 y, 4,713 events at 10 sessions):
  5 of 66 intervals (8%) excluded zero vs ~10% expected by chance, so the method does not
  manufacture edges. Full suite **377 passed**; browser run of a 50-stock pooled study.


## 2026-11-17 · Portfolio strategy backtest with out-of-sample test and random-entry control

GitHub: aryankjain11 connected to Claude; pushes now go directly from the session.

- `portfolio.py`: long-only portfolio simulation of one pattern cohort across a watchlist.
  Conventions identical to `strategy.backtest` (next-open entry + slippage, per-side costs,
  ATR stop, R target, gap-through-stop at the open, stop-first when both touched, holding
  limit, liquidation-cost marking). Portfolio rules: risk % of current equity, position %
  cap, cash cap, max open positions, one position per stock; excess same-day signals taken
  by pre-known relative volume then symbol, the rest recorded as skipped.
  `random_entry_control`: same rules and number of signals on random (stock, day) entries,
  40 simulations, so a pattern is compared with random entries rather than with zero.
- `portfolio_ui.py` (new page "Strategy backtest"): load watchlist (shared cached loader with
  Pattern research) → split (last 30% held out by default) → choose a bullish pattern from a
  pooled study whose outcomes are measured only up to split − horizon (no training measurement
  touches test years) → rules → side-by-side training/test metrics, equity vs gross
  equal-weight buy-and-hold, trades, skipped signals, CSV. Verdict: Held up (test R beats ≥80%
  of random runs) / Weakened / Failed / No clear edge even in training.
- Verification (`test_portfolio.py`, 11 tests): hand-computed target trade (500 shares,
  +2,000, 2.0R); costs + gap-through-stop fill; stop-first when both touched; capacity priority
  and skip records (this caught a real bug: externally supplied signals were not re-sorted
  by priority); cash accounting identity; position caps; future bars do not alter earlier
  trades; split/benchmark; rules validation; deterministic random control; verdict judged
  against random entries; end-to-end page test. Loop optimisation re-verified by the same tests.
- Null checks on 50 drifting random walks (5 y): the top training pattern collapsed out of
  sample, and a zero-based verdict would have called market drift an edge (+0.17R both
  periods). Against the random-entry control, 0 of the 8 best training patterns were rated
  "Held up". Full suite **388 passed**; browser run of the full flow on 50 stand-in stocks.
- Not yet: roadmap/checklist status entries for this feature (learning/roadmap.py) — the
  generated PROJECT_STATUS is unchanged.


## 2026-11-17 · Paper-trading tracker (prospective evaluation)

- `paper.py`: frozen `PaperPlan` (signal date/close, ATR, stop ATR, R target, holding limit,
  costs, source, pattern, context snapshot). `evaluate` is a pure function of the plan and
  completed daily bars dated after the signal, with the backtests' rules (next-open entry +
  slippage, gap-through-stop at the open, stop-first, holding limit, R after costs, MFE/MAE
  capped at the exit). `check_recordable` refuses replay, non-latest sessions and signals more
  than 4 calendar days old (hindsight). `ledger_stats` excludes voided trades.
- `paper_store.py`: SQLAlchemy table; plan columns insert-only, evaluation columns and void
  flag updatable; unique per (ledger, provider symbol, signal date, source, pattern).
  `DATABASE_URL` (Streamlit secret or env) selects a hosted database; otherwise SQLite under
  data/ (ignored by git). Added pins: sqlalchemy 2.0.44, psycopg[binary] 3.2.12 (wheels
  verified for Python 3.14).
- UI: "Paper trades" page (ledger name, update outcomes, stats in R, cumulative curve,
  per-source table, CSV, void with reason, method). Recording from Analyze → Trade plan
  (ticker data only, so outcomes can be fetched later), from a selected Scanner row, and
  "record today's signals" on Strategy backtest (same rules as the backtest).
- Verification (`test_paper.py`, 11): hand-computed target/gap/both-touched/expiry/cost cases;
  bars on or before the signal are never used and later bars never change a closed outcome;
  recording-time rules; storage round trip, dedup, void; end-to-end app test record → waiting →
  three new sessions → "Target hit". That test first failed because the provider layer correctly
  dropped a future-dated final session; fixed by advancing the test clock, not the code.
  Full suite **399 passed**; browser check of recording and the page.
- Open item: the hosted app has no persistent database yet, so its ledger resets on restart
  (the page says so). Owner decision needed on a hosted database.
