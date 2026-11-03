# GitHub sync status

Updated: 2026-11-03.

- Repository: https://github.com/aryankjain11/signal-ledger
- Visibility: **private**, verified through the GitHub page and connected metadata.
- Initial branch: `main`.
- Initial README commit: `bc09670a45e3776f5fcb47b393d93e685974fe63`.
- **Latest calendar/status source: complete and verified.** Commit
  [`9a41497dd7024d0a1d3b39534573f80df6f45e77`](https://github.com/aryankjain11/signal-ledger/commit/9a41497dd7024d0a1d3b39534573f80df6f45e77)
  has 54 reviewed files, all fetched and blob-SHA matched; repository remains private.
  No owner market-data upload or screenshot was included.
- **Latest CI:** [run 41657477162](https://github.com/aryankjain11/signal-ledger/actions/runs/41657477162),
  job 125991544026: **141 passed in 10.45 seconds**, Ubuntu 26.04 / Python 3.13.17.
  Local regression: **141 passed in 49.18 seconds**. This audit documents the already
  observed snapshot, rather than predicting the result of its own later commit.
- **Earlier native NSE stock-history upload: complete and verified.** Source
  [`dbb5a3db7e48cbf58f7bb3b2519e7ca063f6de8d`](https://github.com/aryankjain11/signal-ledger/commit/dbb5a3db7e48cbf58f7bb3b2519e7ca063f6de8d)
  contains 49 reviewed source files, all fetched and blob-SHA matched. The supplied
  market-data download was not uploaded. Repository remains private.
- **Earlier native-upload CI:** [run 41652886132](https://github.com/aryankjain11/signal-ledger/actions/runs/41652886132),
  job 125975413746: **117 passed in 12.78 seconds**, Ubuntu 26.04 / Python 3.13.17.
  Local full regression: **117 passed in 48.11 seconds**. This audit records the
  already-observed source result, rather than predicting its own later commit.
- **Earlier S02-A upload: complete and verified.** All 46 reviewed files matched
  their remote blob SHAs at source commit
  [`165264391dbdef6e0f1dcd1b3d88eec7c70e06c2`](https://github.com/aryankjain11/signal-ledger/commit/165264391dbdef6e0f1dcd1b3d88eec7c70e06c2).
- **Earlier S02-A remote CI: passed**, 90 tests in 11.79 seconds on Ubuntu 26.04 / Python 3.13.17.
  [Verified Actions run 41639106785](https://github.com/aryankjain11/signal-ledger/actions/runs/41639106785), job 125927744182.
  Local full regression: 90 passed in 52.97 seconds. These are synthetic/software
  checks; acceptance against a permitted real NSE file remains pending.
- This audit records the observed S02-A source snapshot; its own commit is later.
- **Earlier learning-foundation upload:** All 40 files in the reviewed
  source snapshot were committed on `main`; every remote content-object SHA matched
  the corresponding reviewed file.
- Source commit: [`189b15a6043dad2638f7c04d08920c52ada0d03a`](https://github.com/aryankjain11/signal-ledger/commit/189b15a6043dad2638f7c04d08920c52ada0d03a).
- **Remote CI: passed**, 49 tests in 3.13 seconds on Ubuntu 26.04 / Python 3.13.17.
  [Verified Actions run 41624242800](https://github.com/aryankjain11/signal-ledger/actions/runs/41624242800).
- Fresh local verification before upload: 49 tests passed in 13.05 seconds.
- This status/checklist/log update is a documentation audit after the source commit;
  the links above identify the already-verified snapshot and test evidence.

## Prior blocker: resolved

The owner requested a retry. A small write through the same tool succeeded on
2026-11-03. Individual file writes, tree assembly, commit creation and the branch
update then succeeded through the normal automatic approval checks. The `main`
update used an expected-head check and did not force-overwrite another change.

The connected GitHub tool's automatic approval service reported:
“Selected model is at capacity.” It explicitly identified this as a review failure,
not a determination that the upload is unsafe, and said the action was not executed.
The earlier reviewed upload was retried and hit the same condition. No branch
update was attempted during that failed session. Its immutable content-object
preparation was not treated as a committed source upload. The later successful
source commit and file verification above resolved this distinction.

The computer's separate Git client also has no saved GitHub login. Its non-interactive
access check failed without opening a login dialog. No token or password was extracted.
The agent did not bypass the failing approval check using a different write path.

## Future synchronization

The local allow-list and credential-pattern check are in `scripts/source_manifest.py`.
The existing repository should be reused, not recreated. For future work, upload
the reviewed files, create a commit based on the current remote head, update `main`
with an expected-head check, verify the files and resulting commit, then record
the outcome in `WORK_LOG.md` and this status document. Inspect the branch again
before retrying if the owner has changed it meanwhile.

## Owner-controlled manual option

Run `python scripts/package_source.py` to produce `outputs/signal-ledger-source.zip`.
It contains the reviewed source, synthetic sample, tests and learning documents,
plus `SOURCE_MANIFEST.json` with sizes/hashes. It excludes environments, private
uploads, credentials, databases and runtime outputs.

1. Download the archive and extract it into an empty folder.
2. Open the private repository, then **Add file → Upload files**.
3. Drop the extracted contents, including the `.github` and `.streamlit` folders.
   Uploading the ZIP itself stores a ZIP; GitHub does not expand it into source.
4. Review the file paths. They should start with `app.py`, `learning/`, `docs/` etc.,
   not an extra enclosing project folder. The initial README is replaced by the
   full project README.
5. Commit with a message such as `Add research prototype and learning foundation`.
6. Inspect the repository files and Actions result, then tell the assistant the
   commit URL so the journal/checklist can record the verified state.

No license was selected for public distribution. This repository remains private;
changing its audience is a separate owner decision.
