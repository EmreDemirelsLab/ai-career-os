import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy import DateTime, String, delete
from sqlalchemy.orm import Mapped, Session, mapped_column

from career_os.db import Base


class WorkspaceSession(Base):
    __tablename__ = "workspace_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    master_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


def token_from(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        return ""
    return authorization[7:]


def is_master(request: Request, token: str) -> bool:
    expected: str = request.app.state.api_token
    if len(expected) < 32:
        raise HTTPException(503, "Workspace disabled until CAREER_API_TOKEN is configured")
    return bool(token and hmac.compare_digest(expected.encode(), token.encode()))


def authorize(request: Request, authorization: str | None = Header(default=None)) -> None:
    token = token_from(authorization)
    if is_master(request, token):
        return
    if token:
        with Session(request.app.state.engine) as session:
            row = session.get(WorkspaceSession, hashlib.sha256(token.encode()).hexdigest())
            if row:
                expiry = row.expires_at
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=UTC)
                if (
                    expiry > datetime.now(UTC)
                    and row.master_hash
                    == hashlib.sha256(request.app.state.api_token.encode()).hexdigest()
                ):
                    return
    raise HTTPException(401, "Authentication required")


router = APIRouter()


@router.post("/workspace-session")
def login(request: Request, authorization: str | None = Header(default=None)) -> dict[str, str]:
    if not is_master(request, token_from(authorization)):
        raise HTTPException(401, "Authentication required")
    token = secrets.token_urlsafe(48)
    with Session(request.app.state.engine) as session, session.begin():
        session.execute(
            delete(WorkspaceSession).where(WorkspaceSession.expires_at <= datetime.now(UTC))
        )
        session.add(
            WorkspaceSession(
                token_hash=hashlib.sha256(token.encode()).hexdigest(),
                master_hash=hashlib.sha256(request.app.state.api_token.encode()).hexdigest(),
                expires_at=datetime.now(UTC) + timedelta(hours=8),
            )
        )
    return {"session_token": token}


@router.delete("/workspace-session", status_code=204)
def logout(request: Request, authorization: str | None = Header(default=None)) -> None:
    token = token_from(authorization)
    if token:
        with Session(request.app.state.engine) as session, session.begin():
            session.execute(
                delete(WorkspaceSession).where(
                    WorkspaceSession.token_hash == hashlib.sha256(token.encode()).hexdigest()
                )
            )
