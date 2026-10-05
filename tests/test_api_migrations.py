from alembic import command
from alembic.config import Config
from career_os.api import create_app
from career_os.db import build_engine
from fastapi.testclient import TestClient
from sqlalchemy import text


def test_health_ready_and_schema_drift(engine):
    with TestClient(create_app(engine)) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/ready").status_code == 200
        with engine.begin() as connection:
            connection.execute(text("UPDATE alembic_version SET version_num='old'"))
        assert client.get("/ready").status_code == 503
        assert client.get("/health").status_code == 200
        with engine.begin() as connection:
            connection.execute(text("UPDATE alembic_version SET version_num='0002_workspace'"))


def test_missing_schema_is_not_ready(tmp_path):
    engine = build_engine(f"sqlite:///{tmp_path / 'empty.db'}")
    with TestClient(create_app(engine)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 503
    engine.dispose()


def test_migration_roundtrip_and_metadata(engine):
    config = Config("alembic.ini")
    config.attributes["database_url"] = engine.url.render_as_string(hide_password=False)
    command.check(config)
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    command.check(config)
    with TestClient(create_app(engine)) as client:
        assert client.get("/ready").status_code == 200
