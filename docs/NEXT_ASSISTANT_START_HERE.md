# Start here · continuation prompt for the next assistant

Prepared16 November2026. Copy the message below into a new assistant and attach
the complete handoff ZIP, or give it authorized access to the private repository.
The message assumes it has file/code access; if it does not, first ask that service
how to attach/extract a project archive. No access credentials are included.

---

I am continuing an existing project called **Signal Ledger**. Help me build it
further; do not start a replacement website from scratch. I have supplied the
complete source, tests, original project brief, decisions, status and handoff.

My original vision is a rigorous, interpretable quantitative technical-analysis
and trading-research platform: structure/patterns/candles/volume/momentum,
multi-timeframe analysis, historical evidence, exact strategies and risk management,
annotated charts, and later validated ML and evidence-bound AI explanations.
The complete first prompt is preserved in `docs/ORIGINAL_BRIEF.md`.

The current build is a local Python/Streamlit daily-data workbench for Indian-stock
swing research. It accepts generic CSV/XLSX and unchanged native NSE security-history
CSV, has five workspaces, supported deterministic analysis, descriptive event
studies, two-stock comparison/correlations and two long strategy simulators.
There are no live feeds/orders, trained ML models, connected LLM, screenshot input,
permanent saved-history database or demonstrated trading edge.

Read these before editing:

1. `AGENTS.md` and `docs/AI_HANDOFF_2026-11-16.md`.
2. `docs/ORIGINAL_BRIEF.md`, `docs/BUILD_PLAN.md`, `docs/PROJECT_STATUS.md` and
   `docs/FEATURE_PRIORITIES.md`.
3. The latest entries of `docs/WORK_LOG.md`, `docs/BUILD_REPORT.md` and
   `docs/GITHUB_SYNC.md`; distinguish old historical snapshots from current scope.
4. `docs/NEXT_MILESTONE_STRATEGY_COMPARISON.md` and the relevant implementation/tests.

If using the handoff ZIP, start with its root `START_HERE.md`, run
`python VERIFY_HANDOFF.py`, and enter `project/`. `PROJECT_SNAPSHOT.json` contains
the checkpoint, complete task/phase inventory and source hashes. An authenticated
repository clone may contain newer changes; preserve them and inspect its current
head before editing. This source package does not include `.venv` or Git history.

Important continuing preferences:

- I want to understand finance and software while building useful features. Keep
  the Education and Concepts reference clear and current. **Exercises, assignments
  and quizzes are paused**; do not require learner responses or claim mastery.
- Prioritize visible analytical/strategy/research functionality. Defer extra data
  adapters and automatic corporate-action downloads unless necessary for the
  selected feature or an actual defect.
- Build one bounded, usable increment at a time. Explain important tradeoffs,
  verify meaningful arithmetic/chronology/UI behavior, and maintain a working app.
- Preserve formation versus detection times, no-look-ahead/no-repainting behavior,
  conservative fills/costs/gaps, action execution restrictions, immutable saved-run
  evidence and explicit stale-input labels. Session memory is not permanent history.
- Do not invent probabilities or call a simulated result validated. A detector,
  event study, executable strategy and predictive probability are separate things.
- Log work in `docs/WORK_LOG.md`; update current build/status/reference sources as
  relevant. The shared sources are `learning/roadmap.py`, `concepts.py` and
  `progress.py`; regenerate documents with `scripts/export_learning_docs.py`.
- Keep the private repository private and exclude credentials, my actual uploads,
  account data, environments and runtime outputs. No live orders, new paid services
  or public deployment. Use your own supported authorized GitHub connection; do not
  assume access to the previous assistant's tools or login.
- End milestones with a concise done/partial/planned checklist mapped to the
  original plan, actual tests/publication status and the next step.

The latest accepted application suite recorded **336 passing tests**, including
clean GitHub CI. Treat this as evidence for that checkpoint; run checks yourself
before claiming the current environment passes. The original plan remains8 Done,
20 Partial,15 Planned; the expanded roadmap is361 tasks (54 Done,48 Partial,
247 Planned,12 Optional), with131 concepts. No entire original phase is complete.

First verify the source/environment and explain briefly where we stand. Then
continue the proposed **fair baseline-versus-breakout-retest strategy comparison**
increment using its acceptance specification. It is not the existing two-stock
comparison. Preserve the two original strategy versions; do not tune them and
declare a winner on the same data. If a necessary decision is unresolved, explain
the concrete choice; otherwise make routine implementation decisions and build.

---

## Files and launch commands

The private repository is `https://github.com/aryankjain11/signal-ledger`.
For a new Python3.13 environment, from the extracted `project/` directory:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

macOS/Linux equivalents are in the full report. No API key is required. The site
binds to `127.0.0.1:8501`; the historical synthetic fixtures are invented data.

If an assistant can only read one context file initially, attach the full handoff
report. It must still inspect source/tests before implementing a financial feature.
The report alone is not a substitute for the code archive.
