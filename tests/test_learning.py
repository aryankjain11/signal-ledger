from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from learning.concepts import CONCEPTS, BY_ID, find_concepts, handbook_markdown
from learning.pages import rsi_from_averages
from learning.roadmap import TASKS, STAGE_BY_ID, STATUS_LABELS, checklist_markdown

ROOT = Path(__file__).resolve().parents[1]


def education_app():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.radio(key="workspace_page").set_value("Learn").run()
    assert not app.exception
    return app


def test_catalogue_integrity_and_implementation_honesty():
    assert len(CONCEPTS) == len(BY_ID)
    assert len(CONCEPTS) >= 100
    assert all(c["definition"] and c["title"] and c["category"] and c["app_status"] for c in CONCEPTS)
    assert {"rsi", "macd", "evening-star", "risk-sizing", "leakage"} <= BY_ID.keys()
    assert "Contextual detector implemented" in BY_ID["evening-star"]["app_status"]
    assert "probability" in BY_ID["rsi"]["mistake"]
    assert "rsi" in {c["id"] for c in find_concepts(implementation="Has current engine behavior")}
    assert "evening-star" in {c["id"] for c in find_concepts(implementation="Has current engine behavior")}
    assert "head-shoulders" not in {c["id"] for c in find_concepts(implementation="Has current engine behavior")}


def test_search_and_category_return_expected_concepts():
    matches = find_concepts("Evening Star", "Candlestick patterns")
    assert matches[0]["id"] == "evening-star"
    assert all(c["category"] == "Candlestick patterns" for c in matches)
    assert "morning-star" in {c["id"] for c in matches}  # The related definition mentions its counterpart.
    assert "macd" in {c["id"] for c in find_concepts(" macd ")}
    assert not find_concepts("there is no such concept xyz")


def test_checklist_ids_statuses_scope_and_exports_are_consistent():
    assert len(TASKS) == len({t["id"] for t in TASKS})
    assert len(TASKS) >= 300 and len(STAGE_BY_ID) == 21
    assert all(t["stage"] in STAGE_BY_ID and t["status"] in STATUS_LABELS for t in TASKS)
    titles = {t["title"] for t in TASKS}
    assert {"Evening star", "Head and shoulders", "Purging and embargo for overlapping event labels"} <= titles
    assert (ROOT / "docs" / "MASTER_CHECKLIST.md").read_text(encoding="utf-8") == checklist_markdown()
    assert (ROOT / "docs" / "EDUCATION_AND_CONCEPTS.md").read_text(encoding="utf-8") == handbook_markdown()


@pytest.mark.parametrize("gain,loss,expected", [(2, 1, 100 - 100 / 3), (3, 1, 75), (0, 0, 50), (1, 0, 100), (0, 1, 0)])
def test_rsi_teaching_arithmetic(gain, loss, expected):
    assert rsi_from_averages(gain, loss) == pytest.approx(expected)


@pytest.mark.parametrize("gain,loss", [(-1, 1), (1, -1), (float("nan"), 1), (1, float("inf"))])
def test_rsi_teaching_rejects_invalid_averages(gain, loss):
    with pytest.raises(ValueError):
        rsi_from_averages(gain, loss)


def test_education_page_search_lab_and_quiz_flow():
    app = education_app()
    assert app.title[0].value == "Learn"
    app.text_input(key="concept_search").set_value("Evening Star").run()
    assert not app.exception
    assert app.selectbox(key="chosen_concept").value == "evening-star"
    assert any("Contextual detector implemented" in m.value for m in app.markdown)
    app.number_input(key="rsi_gain").set_value(3.0).run()
    assert not app.exception
    assert any(m.label == "Illustrative RSI" and m.value == "75.00" for m in app.metric)
    app.radio(key="rsi_quiz").set_value("Recent smoothed gains dominate losses; future direction is still uncertain").run()
    app.button(key="check_rsi_answer").click().run()
    assert any("Correct" in s.value for s in app.success)
    app.number_input(key="lab_stop").set_value(250.0).run()
    assert not app.exception
    assert any("stop must be below" in w.value for w in app.warning)


def test_no_result_search_and_build_journal_navigation():
    app = education_app()
    app.text_input(key="concept_search").set_value("zzzzz-no-entry").run()
    assert any("No matching concepts" in w.value for w in app.warning)
    # The developer checklist is no longer in the main navigation; it stays reachable at ?page=build.
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    app.query_params["page"] = "build"
    app.run()
    assert not app.exception
    assert app.title[0].value == "Build checklist and journal"
    app.selectbox(key="build_stage").set_value("S05").run()
    assert not app.exception
    stage_tables = [d.value for d in app.dataframe if "ID" in d.value.columns]
    assert len(stage_tables) == 1 and "Evening star" in stage_tables[0].Feature.tolist()


def test_original_plan_progress_mapping_and_export():
    from learning.progress import PHASES, progress_markdown, progress_rows
    assert [p[0] for p in PHASES] == ["1", "2", "3", "4", "5"]
    assert [len(p[2]) for p in PHASES] == [10, 9, 9, 8, 7]
    assert len(progress_rows()) == 43
    assert {r["Status"] for r in progress_rows()} == {"Done", "Partial", "Planned"}
    assert (ROOT / "docs" / "PROJECT_STATUS.md").read_text(encoding="utf-8") == progress_markdown()
    assert "assignments are paused" in progress_markdown()
