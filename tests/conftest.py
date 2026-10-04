import os
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from career_os.db import build_engine
from career_os.governance import seed_sources


def migrate(url, revision="head"):
    config = Config("alembic.ini")
    config.attributes["database_url"] = url
    command.upgrade(config, revision)


@pytest.fixture(params=["sqlite", "postgres"])
def engine(request, tmp_path):
    if request.param == "postgres":
        url = os.getenv("TEST_DATABASE_URL")
        if not url:
            pytest.skip("TEST_DATABASE_URL absent: PostgreSQL verification NOT performed")
        if not url.rsplit("/", 1)[-1].startswith("career_test"):
            pytest.fail("Use a disposable PostgreSQL database named career_test...")
    else:
        url = f"sqlite:///{tmp_path / 'test.db'}"
    config = Config("alembic.ini")
    config.attributes["database_url"] = url
    command.downgrade(config, "base")
    command.upgrade(config, "head")
    db = build_engine(url)
    seed_sources(db, Path("seed/source_registry_seed.csv"))
    yield db
    db.dispose()
    command.downgrade(config, "base")
