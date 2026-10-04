from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, text

from career_os.config import Settings
from career_os.db import build_engine

SCHEMA_REVISION = "0001_foundation"


def create_app(engine: Engine | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.engine = engine if engine is not None else build_engine(Settings().database_url)
        yield
        if engine is None:
            app.state.engine.dispose()

    app = FastAPI(title="AI Career OS", lifespan=lifespan)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> JSONResponse:
        try:
            with app.state.engine.connect() as connection:
                versions = (
                    connection.execute(text("SELECT version_num FROM alembic_version"))
                    .scalars()
                    .all()
                )
                if versions != [SCHEMA_REVISION]:
                    raise ValueError("schema_not_current")
            return JSONResponse({"status": "ready"})
        except Exception:
            return JSONResponse({"status": "not_ready"}, status_code=503)

    return app


app = create_app()
