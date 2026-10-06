"""Authored foundation lessons; objective checks are not mastery or CEFR assessment."""

import json
from importlib.resources import files
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import Field, HttpUrl, StrictInt
from sqlalchemy import select
from sqlalchemy.orm import Session

from career_os.auth import authorize
from career_os.contracts import digest
from career_os.workspace import serialize, stamp
from career_os.workspace_contracts import Contract, Note, Short
from career_os.workspace_models import LearningAttempt

CATALOG: dict[str, Any] = json.loads(
    files("career_os").joinpath("foundation_lessons.json").read_text()
)
router = APIRouter(prefix="/workspace/lessons", dependencies=[Depends(authorize)])


class LessonSubmission(Contract):
    lesson_id: Short
    lesson_version: Short
    answers: Annotated[dict[str, StrictInt], Field(min_length=1, max_length=10)]
    concept_answer: Note
    english_answer: Note
    assistance: Literal["independent", "assisted", "generated"]
    artifact_url: HttpUrl | None = None


@router.get("")
def lessons(request: Request) -> dict[str, Any]:
    public = json.loads(json.dumps(CATALOG))
    for unit in public["units"]:
        for question in unit["questions"]:
            del question["correct"]
            del question["explanation"]
    with Session(request.app.state.engine) as session:
        rows = session.scalars(
            select(LearningAttempt)
            .where(LearningAttempt.data["lesson_id"].as_string().is_not(None))
            .order_by(LearningAttempt.created_at.desc(), LearningAttempt.id)
            .limit(50)
        )
        return {"catalog": public, "attempts": [serialize(x) for x in rows]}


@router.post("/attempts", status_code=201)
def submit(body: LessonSubmission, request: Request) -> dict[str, Any]:
    if body.lesson_version != CATALOG["version"]:
        raise HTTPException(409, "Lesson version changed; reload before submitting")
    lesson = next((u for u in CATALOG["units"] if u["id"] == body.lesson_id), None)
    if lesson is None:
        raise HTTPException(422, "Unknown lesson")
    questions = {q["id"]: q for q in lesson["questions"]}
    if set(body.answers) != set(questions) or any(
        not 0 <= value < len(questions[key]["choices"]) for key, value in body.answers.items()
    ):
        raise HTTPException(422, "Answer every question with a valid choice")
    checks = [
        dict(
            question_id=key,
            prompt=q["prompt"],
            selected=body.answers[key],
            correct=body.answers[key] == q["correct"],
            explanation=q["explanation"],
        )
        for key, q in questions.items()
    ]
    with Session(request.app.state.engine) as session, session.begin():
        row = LearningAttempt(
            **stamp(),
            week=lesson["week"],
            data={
                **body.model_dump(mode="json"),
                "week": lesson["week"],
                "lesson_title": lesson["title"],
                "content_fingerprint": digest(lesson),
                "assessment_status": "objective_checks_only_not_mastery",
                "objective_checks": checks,
                "objective_correct": sum(x["correct"] for x in checks),
                "objective_total": len(checks),
                "technical_assessment": "requires_independent_review",
                "english_assessment": "unassessed_not_cefr",
                "lab_execution": "not_run_by_server",
                "technical_rubric": lesson["technical_rubric"],
                "english_rubric": lesson["english_rubric"],
            },
        )
        session.add(row)
        return serialize(row)
