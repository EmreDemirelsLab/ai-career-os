from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

Short = Annotated[str, Field(min_length=1, max_length=200)]
Note = Annotated[str, Field(min_length=1, max_length=10000)]
LanguageLevel = Literal["unknown", "none", "A1", "A2", "B1", "B2", "C1", "C2"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Profile(Contract):
    name: Short
    target_role: Literal["AI_ENGINEER", "APPLIED_AI_ENGINEER", "ML_ENGINEER", "LLM_ENGINEER"]
    weekly_hours: Annotated[int, Field(ge=1, le=60)]
    english: LanguageLevel
    german: LanguageLevel
    work_authorization: Literal["yes", "no", "unknown"] = "unknown"
    relevant_degree: Literal["yes", "no", "unknown"] = "unknown"
    professional_years: Annotated[int | None, Field(ge=0, le=60)] = None
    location: Short


class Evidence(Contract):
    skill: Short
    dimension: Literal[
        "conceptual",
        "implementation",
        "debugging",
        "production",
        "system_design",
        "explanation",
        "interview",
    ]
    artifact_url: HttpUrl
    notes: Note
    assistance: Literal["independent", "assisted", "generated"]
    verifier: Literal["self_report", "external_review"] = "self_report"
    review_reference: HttpUrl | None = None


class LearningSubmission(Contract):
    week: Annotated[int, Field(ge=1, le=24)]
    concept_answer: Note
    english_answer: Note
    artifact_url: HttpUrl | None = None


class ReviewSubmission(Contract):
    attempt_id: Short
    interval: Literal[3, 7, 14, 30]
    notes: Note


class InterviewSubmission(Contract):
    question_id: Short
    answer: Note


class Requirement(Contract):
    kind: Literal["german", "english", "degree", "experience", "work_authorization", "location"]
    value: Short
    mandatory: bool
    evidence_span: Annotated[str, Field(min_length=1, max_length=500)]


class Opportunity(Contract):
    title: Short
    company: Short
    source_url: HttpUrl
    observed_on: date
    skills: Annotated[list[Short], Field(max_length=50)]
    requirements: Annotated[list[Requirement], Field(max_length=20)]
    review_notes: Note


class Application(Contract):
    opportunity_id: Short
    cv_version: Short
    notes: Annotated[str, Field(max_length=5000)] = ""


class Stage(Contract):
    stage: Literal["saved", "applied", "screening", "technical", "offer", "rejected", "withdrawn"]
    notes: Annotated[str, Field(max_length=5000)] = ""
