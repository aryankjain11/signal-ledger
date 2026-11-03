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
