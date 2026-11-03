# Project working agreement

The owner's primary goal is to LEARN finance, quantitative research and software
engineering while building a useful application. These are continuing project
instructions, not a request to finish the entire roadmap in a single change.

## Owner update · 2026-11-03

Pause learning exercises and assignments until the owner revisits that scope.
Continue product implementation, testing, documentation and GitHub synchronization.
Keep existing reference material available; do not add exercises or require learner
responses to progress. Include a concise done/partial/pending checklist mapped to
the original plan in completion updates. This supersedes exercise-related steps below.

Feature-priority steering: prioritize visible analytical/strategy/research features
and the concepts demonstrated by using them. Defer further file-format adapters,
automatic corporate-action downloads and data plumbing unless they block a selected
feature or correct an actual reliability problem. Conceptual learning does not mean
homework or exercises. See docs/FEATURE_PRIORITIES.md for the current recommendation;
its proposed features remain unimplemented until their acceptance gates pass.

## Work one milestone at a time

1. Read `docs/WORK_LOG.md`, `docs/MASTER_CHECKLIST.md` and the relevant source.
2. State the next small milestone, its prerequisite concepts and completion gate.
3. Explain the financial idea with a small original, labelled hypothetical example.
4. Implement a usable increment, verify meaningful numerical/UI behavior and
   explain the result. Never turn a glossary entry into a claim of implementation.
5. Update the relevant checklist item, education entry, `docs/WORK_LOG.md` and
   `docs/BUILD_REPORT.md` before closing the milestone. Regenerate documentation
   with `python scripts/export_learning_docs.py` after catalogue changes.
6. Record the user's exercise and the next milestone. Do not claim the user has
   completed a lesson or understood a concept without their confirmation.

## Durable records

- `learning/roadmap.py`: implementation status, scope, original-brief references,
  acceptance gates and stage learning objectives. Source of the master checklist.
- `learning/concepts.py`: shared educational content for the app and handbook.
- `docs/WORK_LOG.md`: append dated entries with changes, reasons, files, tests,
  results, limitations, mistakes/blockers, sources and next step. Log meaningful
  work batches, not every mouse click. Label retrospective reconstruction clearly.
- `docs/BUILD_REPORT.md`: current detailed architecture, curriculum and build state.
- `docs/EDUCATION_AND_CONCEPTS.md`: generated handbook, including worked examples.
- `docs/lessons/`: longer walkthroughs, exercises and answer explanations.

## Evidence and scope

Mark Done only after the specific acceptance gate passes. Distinguish implemented,
partially implemented, planned and optional features. Record tests actually run;
do not manufacture dates, results, model probabilities or trading performance.
Keep numerical engines independent from educational UI and optional LLM narration.
Preserve formation/detection times and prevent look-ahead. Use licensed data and
disclose adjustments and costs. Live orders are outside current authorization.

## GitHub and privacy

Use the owner's private Signal Ledger repository once verified. Commit source,
tests, synthetic fixtures and learning documentation; exclude local environments,
credentials, private uploads, real account data and licensed datasets. Do not change
repository visibility or add paid services without the owner's instruction. Run
relevant checks before commits; report the commit and any remote CI limitations.
An upload is not complete until its branch/files are verified on GitHub.
