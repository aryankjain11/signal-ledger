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
