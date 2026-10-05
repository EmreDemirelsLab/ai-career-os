import hashlib
from datetime import UTC, datetime, timedelta

from career_os.api import create_app
from career_os.auth import WorkspaceSession
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_sessions_expire_revoke_and_do_not_expose_master(engine):
    master = "test-only-master-token-at-least-32-characters"
    with TestClient(create_app(engine=engine, api_token=master)) as c:
        assert c.post("/workspace-session").status_code == 401
        token = c.post("/workspace-session", headers={"Authorization": f"Bearer {master}"}).json()[
            "session_token"
        ]
        assert token != master
        headers = {"Authorization": f"Bearer {token}"}
        assert c.get("/workspace", headers=headers).status_code == 200
        assert c.post("/workspace-session", headers=headers).status_code == 401
        with Session(engine) as s, s.begin():
            row = s.get(WorkspaceSession, hashlib.sha256(token.encode()).hexdigest())
            assert row.token_hash != token
            row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        assert c.get("/workspace", headers=headers).status_code == 401
        token = c.post("/workspace-session", headers={"Authorization": f"Bearer {master}"}).json()[
            "session_token"
        ]
        headers = {"Authorization": f"Bearer {token}"}
        assert c.delete("/workspace-session", headers=headers).status_code == 204
        assert c.get("/workspace", headers=headers).status_code == 401
