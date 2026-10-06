import subprocess
import sys

from career_os.api import create_app
from career_os.lessons import CATALOG
from career_os.workspace import CURRICULUM, SKILLS
from fastapi.testclient import TestClient

TOKEN = "synthetic-lessons-token-with-32-characters"


def submission():
    unit = CATALOG["units"][0]
    return dict(
        lesson_id=unit["id"],
        lesson_version=CATALOG["version"],
        answers={q["id"]: q["correct"] for q in unit["questions"]},
        concept_answer="Synthetic explanation",
        english_answer="I tested an invalid input.",
        assistance="generated",
    )


def test_catalog_and_reference_labs():
    assert len({u["id"] for u in CATALOG["units"]}) == 24
    for unit in CATALOG["units"]:
        assert unit["skill"] in SKILLS
        assert unit["skill"] == CURRICULUM["units"][unit["week"] - 1]["skill"]
        assert len({q["id"] for q in unit["questions"]}) == len(unit["questions"])
        assert all(0 <= q["correct"] < len(q["choices"]) for q in unit["questions"])
    process = subprocess.run(
        [sys.executable, "labs/foundation/check.py", "--reference"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert process.returncode == 0, process.stderr
    starter = subprocess.run(
        [sys.executable, "labs/foundation/check.py", "--week", "1"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert starter.returncode == 1
    assert "NotImplementedError" in starter.stderr


def test_lesson_attempt_export_recall_and_delete(engine):
    with TestClient(create_app(engine, TOKEN)) as client:
        assert client.get("/workspace/lessons").status_code == 401
        client.headers["Authorization"] = f"Bearer {TOKEN}"
        response = client.get("/workspace/lessons")
        assert response.status_code == 200
        question = response.json()["catalog"]["units"][0]["questions"][0]
        assert "correct" not in question and "explanation" not in question
        data = submission()
        assert (
            client.post(
                "/workspace/lessons/attempts", json={**data, "lesson_version": "old"}
            ).status_code
            == 409
        )
        for answers in (
            {},
            {**data["answers"], "invented": 0},
            {k: True for k in data["answers"]},
            {k: 99 for k in data["answers"]},
        ):
            assert (
                client.post(
                    "/workspace/lessons/attempts", json={**data, "answers": answers}
                ).status_code
                == 422
            )
        saved = client.post("/workspace/lessons/attempts", json=data)
        assert saved.status_code == 201
        item = saved.json()
        assert item["objective_correct"] == item["objective_total"] == 2
        assert item["assessment_status"] == "objective_checks_only_not_mastery"
        assert item["assistance"] == "generated"
        assert item["english_assessment"] == "unassessed_not_cefr"
        assert item["lab_execution"] == "not_run_by_server"
        assert client.get("/workspace/lessons").json()["attempts"][0]["id"] == item["id"]
        exported = client.get("/workspace/export").json()
        assert exported["attempts"][0]["content_fingerprint"] == item["content_fingerprint"]
        assert len([r for r in exported["review_queue"] if r["attempt_id"] == item["id"]]) == 4
        assert exported["evidence"] == []
        assert (
            client.delete(
                "/workspace", headers={"X-Confirm-Delete": "delete-personal-workspace"}
            ).status_code
            == 204
        )
        assert client.get("/workspace/lessons").json()["attempts"] == []


def test_data_ml_reference_labs():
    process = subprocess.run(
        [sys.executable, "labs/data_ml/check.py", "--reference"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert process.returncode == 0, process.stderr
    starter = subprocess.run(
        [sys.executable, "labs/data_ml/check.py", "--week", "5"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert starter.returncode == 1
    assert "NotImplementedError" in starter.stderr


def test_applied_reference_labs():
    process = subprocess.run(
        [sys.executable, "labs/applied_ai/check.py", "--reference"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert process.returncode == 0, process.stderr
    assert "Ran 16 tests" in process.stderr
    for week in range(9, 25):
        starter = subprocess.run(
            [sys.executable, "labs/applied_ai/check.py", "--week", str(week)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert starter.returncode == 1
        assert "NotImplementedError" in starter.stderr
