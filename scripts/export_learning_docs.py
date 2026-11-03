"""Export app catalogues as reviewable, portable Markdown. No market data needed."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from learning.concepts import handbook_markdown  # noqa: E402
from learning.roadmap import checklist_markdown  # noqa: E402
from learning.progress import progress_markdown  # noqa: E402


def export():
    outputs = {"EDUCATION_AND_CONCEPTS.md": handbook_markdown(), "MASTER_CHECKLIST.md": checklist_markdown(),
               "PROJECT_STATUS.md": progress_markdown()}
    for filename, content in outputs.items():
        (ROOT / "docs" / filename).write_text(content, encoding="utf-8")


if __name__ == "__main__":
    export()
