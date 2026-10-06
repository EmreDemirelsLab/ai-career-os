"""Evidence-linked preparation pack; no invented achievements or automatic applications."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from career_os.auth import authorize
from career_os.contracts import digest
from career_os.workspace import evidence_fit, latest_profile, serialize
from career_os.workspace_models import EvidenceRecord, OpportunityRecord

router = APIRouter(prefix="/workspace/career-pack", dependencies=[Depends(authorize)])


def prepare_pack(
    opportunity: dict[str, Any], profile: dict[str, Any] | None, evidence: list[dict[str, Any]]
) -> dict[str, Any]:
    relevant = [x for x in evidence if x["skill"] in opportunity["skills"]]
    fit = evidence_fit(opportunity, profile, relevant)
    covered = {x["skill"] for x in relevant}
    gaps = sorted(set(opportunity["skills"]) - covered)
    lines = [
        "APPLICATION PREPARATION — REVIEW BEFORE USE",
        f"Role: {opportunity['title']}",
        f"Company: {opportunity['company']}",
        f"Job source: {opportunity['source_url']}",
        f"Observed: {opportunity['observed_on']}",
        "",
        "Eligibility: based only on your recorded profile and explicit requirements.",
        f"Current result: {fit['eligibility']}; not a hiring decision or legal determination.",
    ]
    for check in fit["checks"]:
        lines.append(
            f"- {check['kind']}: {check['status']} | Source excerpt: {check['evidence_span']}"
        )
    lines += ["", "EVIDENCE INVENTORY — USER-ENTERED, NOT INDEPENDENTLY VERIFIED"]
    for item in relevant:
        lines += [
            f"- Skill: {item['skill']} | Dimension: {item['dimension']}",
            f"  Artifact: {item['artifact_url']}",
            f"  Assistance: {item['assistance']}",
            f"  Your recorded notes: {item['notes']}",
        ]
        if item.get("review_reference"):
            lines.append(f"  Claimed review reference: {item['review_reference']}")
    if not relevant:
        lines.append("No relevant evidence recorded. Do not invent project experience.")
    lines += [
        "",
        "OPEN EVIDENCE GAPS",
        *[f"- {skill}" for skill in gaps],
        "",
        "ENGLISH PROJECT DEFENSE — COMPLETE WITH YOUR OWN FACTS",
        "1. Context: What problem did you solve, for whom, and what was your role?",
        "2. Decision: Which alternative did you reject and why?",
        "3. Evidence: Show a test, artifact or measured result. Do not invent numbers.",
        "4. Failure: Explain one bug or failed experiment and your correction.",
        "5. Limit: State what remains unverified and what you would test next.",
        "",
        "BEFORE APPLYING",
        "- Re-open the source and confirm the role is still available.",
        "- Review every hard requirement, especially unknown/conflicting items.",
        "- Write CV claims only from artifacts you can explain; disclose assistance honestly.",
        "- Keep private CV/interview material out of public repositories.",
        "- Record a CV version and application status yourself. Nothing was sent.",
    ]
    return {
        "policy_version": "evidence-preparation/1",
        "opportunity_id": opportunity["id"],
        "source_fingerprint": digest(
            {"opportunity": opportunity, "profile": profile, "evidence": relevant}
        ),
        "eligibility": fit,
        "evidence_count": len(relevant),
        "unlinked_skills": gaps,
        "claim_status": "user_entered_requires_review",
        "sent": False,
        "text": "\n".join(lines),
    }


@router.get("/{opportunity_id}")
def career_pack(opportunity_id: str, request: Request) -> dict[str, Any]:
    with Session(request.app.state.engine) as session:
        opportunity = session.get(OpportunityRecord, opportunity_id)
        if opportunity is None:
            raise HTTPException(404, "Opportunity not found")
        profile = latest_profile(session)
        evidence = list(
            session.scalars(
                select(EvidenceRecord).order_by(EvidenceRecord.created_at, EvidenceRecord.id)
            )
        )
        return prepare_pack(
            serialize(opportunity),
            profile.data if profile else None,
            [serialize(x) for x in evidence],
        )
