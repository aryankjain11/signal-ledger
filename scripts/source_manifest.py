"""Produce a reviewed source allow-list for connector upload, never credentials.

Default output is paths/hashes/sizes. --content emits one selected file's content
for the authenticated connector, not for application users. No network requests.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOP_LEVEL = ["AGENTS.md", "README.md", "app.py", "Start App.cmd", ".gitignore",
             "pyproject.toml", "requirements.txt", "requirements-dev.txt",
             ".streamlit/config.toml", ".github/workflows/tests.yml", "data/synthetic_daily.csv"]
EXTENSIONS = {".py", ".md", ".jpg", ".png"}
SECRET_PATTERN = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{32,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")


def source_files():
    paths = [ROOT / name for name in TOP_LEVEL]
    for directory in ("quant_engine", "learning", "scripts", "tests", "docs"):
        paths += [p for p in (ROOT / directory).rglob("*")
                  if p.is_file() and p.suffix in EXTENSIONS and "__pycache__" not in p.parts]
    paths = sorted(set(paths), key=lambda p: p.relative_to(ROOT).as_posix())
    for path in paths:
        if path.suffix not in {".jpg", ".png"} and SECRET_PATTERN.search(path.read_text(encoding="utf-8")):
            raise ValueError(f"Possible credential in {path.relative_to(ROOT)}; review before uploading.")
    return paths


def manifest():
    return [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
             "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
             "binary": p.suffix in {".jpg", ".png"}} for p in source_files()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", help="Exact allowed relative path to emit as text")
    args = parser.parse_args()
    if args.content:
        paths = {p.relative_to(ROOT).as_posix(): p for p in source_files()}
        if args.content not in paths:
            parser.error("Path is not in the reviewed source allow-list")
        path = paths[args.content]
        if path.suffix in {".jpg", ".png"}:
            import base64
            print(json.dumps({"path": args.content, "encoding": "base64", "content": base64.b64encode(path.read_bytes()).decode("ascii")}))
        else:
            print(json.dumps({"path": args.content, "encoding": "utf-8", "content": path.read_bytes().decode("utf-8")}))
    else:
        print(json.dumps(manifest(), indent=2))
