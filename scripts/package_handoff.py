"""Package reviewed source and portable continuation context; never local uploads.

Uses the existing source allow-list/credential scan. No network calls or secrets.
Snapshot publication identifiers must be supplied after their independent review.
"""
import argparse
from collections import Counter
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

from source_manifest import ROOT, source_files

sys.path.insert(0, str(ROOT))
from learning.concepts import CONCEPTS
from learning.progress import PHASES, progress_rows
from learning.roadmap import STAGES, TASKS


VERIFY_SCRIPT = '''"""Read-only integrity check. Run before installing/editing the extracted project."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

root = Path(__file__).resolve().parent
entries = json.loads((root / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
failures = []
for item in entries:
    relative = PurePosixPath(item["path"])
    target = root.joinpath(*relative.parts).resolve()
    if relative.is_absolute() or ".." in relative.parts or not target.is_relative_to(root):
        failures.append("Unsafe manifest path: " + item["path"])
        continue
    if not target.is_file():
        failures.append("Missing: " + item["path"])
        continue
    content = target.read_bytes()
    if len(content) != item["bytes"] or hashlib.sha256(content).hexdigest() != item["sha256"]:
        failures.append("Changed: " + item["path"])
if failures:
    print("Integrity check FAILED:\\n" + "\\n".join(failures))
    sys.exit(1)
print(f"Verified {len(entries)} packaged files. No files changed. No network requests made.")
'''


def record(path, content):
    return {"path": path, "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest()}


def json_bytes(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def git_sha(value):
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise argparse.ArgumentTypeError("Use an independently verified full 40-character commit SHA.")
    return value


def build_package(as_of, baseline_head, published_head=None):
    day = date.fromisoformat(as_of)
    payload = {}
    sources = []
    for path in source_files():
        relative = path.relative_to(ROOT).as_posix()
        content = path.read_bytes()
        archive_path = "project/" + relative
        payload[archive_path] = content
        sources.append(record(archive_path, content))

    phase_counts = [{"phase": number, "title": title,
                     "counts": dict(Counter(status for status, _, _ in items))}
                    for number, title, items in PHASES]
    snapshot = {
        "schema": "signal-ledger-handoff/1",
        "as_of": as_of,
        "timezone": "Asia/Calcutta",
        "product": "Signal Ledger",
        "repository": "https://github.com/aryankjain11/signal-ledger",
        "repository_visibility_at_review": "private",
        "branch": "main",
        "verified_pre_handoff_head": baseline_head,
        "published_handoff_head": published_head,
        "publication_note": "SHAs supplied by the packager after separate remote review; this script makes no network calls.",
        "accepted_application_source": "48c9b9d44f70cec696f8ad53dc49e5b78605fe23",
        "recorded_application_verification": {
            "local": {"tests_passed": 336, "seconds": 211.85},
            "github": {"run_id": 43748677879, "job_id": 132917552071,
                       "tests_passed": 336, "seconds": 57.30},
            "meaning": "Historical observed software checks for the accepted application; not a fresh target-machine run or investment validation."
        },
        "original_brief": record("project/docs/ORIGINAL_BRIEF.md", payload["project/docs/ORIGINAL_BRIEF.md"]),
        "scope": {"market": "Indian equities", "style": "Daily swing research",
                  "currency": "INR assumed, no conversion", "local_url": "http://127.0.0.1:8501/",
                  "implementation": "Local deterministic Python/Streamlit research prototype",
                  "learning_exercises": "Paused; financial references retained",
                  "next_feature": "Fair baseline-versus-breakout-retest strategy comparison (planned)"},
        "runtime_requirements": (ROOT / "requirements.txt").read_text(encoding="utf-8"),
        "development_requirements": (ROOT / "requirements-dev.txt").read_text(encoding="utf-8"),
        "python": "3.13; historically checked locally on 3.13.7 and in accepted source CI on 3.13.18",
        "counts": {"concepts": len(CONCEPTS), "tasks": len(TASKS),
                   "task_statuses": dict(Counter(t["status"] for t in TASKS)),
                   "original_phase_statuses": dict(Counter(r["Status"] for r in progress_rows())),
                   "reviewed_source_files": len(sources)},
        "original_phase_counts": phase_counts,
        "original_phase_rows": progress_rows(),
        "stages": [{"id": s[0], "title": s[1], "brief": s[2], "learning": s[3], "gate": s[4]}
                   for s in STAGES],
        "tasks": TASKS,
        "concept_index": [{"id": c["id"], "title": c["title"], "status": c["app_status"]}
                          for c in CONCEPTS],
        "source_files": sources,
        "excluded": [".venv", ".git history", "credentials", "owner/real uploads", "licensed datasets",
                     "outputs/runtime records", "browser downloads/screenshots", "caches"],
        "not_implemented": ["fair strategy comparison", "durable run/history database or archive reopening",
                            "independent held-out/walk-forward validation", "trained ML/calibrated probabilities",
                            "connected LLM", "screenshot inputs", "automatic licensed feeds", "live orders"],
        "authority_note": "New owner instructions/current source override this dated snapshot; preserve later repository edits."
    }
    payload["PROJECT_SNAPSHOT.json"] = json_bytes(snapshot)
    payload["SOURCE_MANIFEST.json"] = json_bytes(sources)
    payload["VERIFY_HANDOFF.py"] = VERIFY_SCRIPT.encode("utf-8")
    payload["START_HERE.md"] = f'''# Signal Ledger · portable handoff · {as_of}

This archive contains {len(sources)} reviewed source files under `project/`.
No environment, login credentials, real uploaded datasets or runtime records are included.

1. Extract into a new folder. Before editing/installing, run `python VERIFY_HANDOFF.py`.
2. Read `project/docs/NEXT_ASSISTANT_START_HERE.md` for the prompt to paste into your new assistant.
3. Read `project/docs/AI_HANDOFF_2026-11-16.md` for the full context and original-vision mapping.
4. The complete first prompt is `project/docs/ORIGINAL_BRIEF.md`.
5. Give the assistant the whole project, not just the screenshot or README.
6. Enter `project/`, create a Python3.13 environment, install `requirements-dev.txt`, run pytest and launch Streamlit as documented.

`PROJECT_SNAPSHOT.json` contains the full roadmap/phase inventory, source hashes and publication checkpoint.
`SOURCE_MANIFEST.json` hashes reviewed project source; `PACKAGE_MANIFEST.json` hashes every payload file except itself.
The SHA256 check detects changes against this manifest; it is not a cryptographic signature or provenance guarantee against an attacker replacing both.
The archive is a source snapshot, not full Git history. The private repository holds commit history.

Latest accepted application:336 passing tests; this is historical software evidence, not proof of investment performance.
The first task for the recipient is baseline verification, then the proposed fair strategy-comparison increment.
Exercises remain paused. No paid services, public exposure or live orders are authorized.
'''.encode("utf-8")
    payload["PACKAGE_MANIFEST.json"] = json_bytes([record(path, content)
                                                    for path, content in sorted(payload.items())])
    destination = ROOT / "outputs" / f"signal-ledger-handoff-{as_of}.zip"
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path, content in sorted(payload.items()):
            info = zipfile.ZipInfo(path, (day.year, day.month, day.day, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None, "ZIP member integrity failed"
        entries = json.loads(archive.read("PACKAGE_MANIFEST.json"))
        assert set(archive.namelist()) == {r["path"] for r in entries} | {"PACKAGE_MANIFEST.json"}
        assert all(record(r["path"], archive.read(r["path"])) == r for r in entries)
    return destination, snapshot, len(payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", required=True, help="Owner's local handoff date, YYYY-MM-DD")
    parser.add_argument("--baseline-head", required=True, type=git_sha,
                        help="Independently verified main before handoff edits")
    parser.add_argument("--published-head", type=git_sha,
                        help="Verified handoff commit, if already published")
    args = parser.parse_args()
    destination, snapshot, members = build_package(args.as_of, args.baseline_head, args.published_head)
    print(json.dumps({"archive": str(destination), "reviewed_source_files": snapshot["counts"]["reviewed_source_files"],
                      "members": members, "bytes": destination.stat().st_size,
                      "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                      "zip_integrity": "passed", "all_payload_sha256": "matched"}, indent=2))
