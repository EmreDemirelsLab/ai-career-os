from copy import deepcopy

from career_os.contracts import digest
from career_os.lessons import CATALOG
from career_os.practice import next_practice


def test_practice_actions_never_turn_scores_into_mastery():
    units = CATALOG["units"]
    unit = units[0]
    assert next_practice(units, {})["suggested_lesson_id"] == unit["id"]
    row = dict(
        id="attempt",
        content_fingerprint=digest(unit),
        objective_correct=1,
        objective_total=2,
        assistance="independent",
    )
    history = {unit["id"]: row}
    assert next_practice(units, history)["items"][0]["state"] == "revisit_concept"
    row["objective_correct"] = 2
    row["assistance"] = "generated"
    assert next_practice(units, history)["items"][0]["state"] == "independent_practice"
    row["assistance"] = "independent"
    result = next_practice(units, history)
    assert result["items"][0]["state"] == "defend_and_review"
    assert result["review_backlog"] == [unit["id"]]
    assert result["suggested_lesson_id"] == units[1]["id"]
    changed = deepcopy(units)
    changed[0]["exercise"] += " new requirement"
    assert next_practice(changed, history)["items"][0]["state"] == "refresh_lesson"
    assert next_practice([], {})["suggested_lesson_id"] is None


def test_practice_uses_latest_per_lesson_beyond_history_window(engine):
    from datetime import UTC, datetime, timedelta
    from uuid import uuid4

    from career_os.api import create_app
    from career_os.workspace_models import LearningAttempt
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import Session

    token = "synthetic-practice-token-at-least-32-chars"
    first, second = CATALOG["units"][:2]
    with Session(engine) as session, session.begin():
        for i in range(52):
            unit = first if i == 0 else second
            session.add(
                LearningAttempt(
                    id=str(uuid4()),
                    created_at=datetime.now(UTC) + timedelta(seconds=i),
                    week=unit["week"],
                    data=dict(
                        lesson_id=unit["id"],
                        content_fingerprint=digest(unit),
                        objective_correct=2,
                        objective_total=2,
                        assistance="independent",
                    ),
                )
            )
    with TestClient(
        create_app(engine, token), headers={"Authorization": f"Bearer {token}"}
    ) as client:
        data = client.get("/workspace/lessons").json()
        assert len(data["attempts"]) == 50
        assert data["practice"]["items"][0]["state"] == "defend_and_review"
        assert data["practice"]["suggested_lesson_id"] == CATALOG["units"][2]["id"]
