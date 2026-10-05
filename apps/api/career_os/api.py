from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import Engine, text

from career_os.auth import router as auth_router
from career_os.config import Settings
from career_os.db import build_engine
from career_os.intelligence import router as intelligence_router
from career_os.workspace import router

SCHEMA_REVISION = "0003_intelligence"


def create_app(engine: Engine | None = None, api_token: str | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        settings = Settings() if engine is None else None
        app.state.api_token = (
            api_token if api_token is not None else (settings.career_api_token if settings else "")
        )
        app.state.engine = engine if engine is not None else build_engine(settings.database_url)  # type: ignore[union-attr]
        yield
        if engine is None:
            app.state.engine.dispose()

    app = FastAPI(title="AI Career OS", lifespan=lifespan)
    app.include_router(auth_router)
    app.include_router(router)
    app.include_router(intelligence_router)

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
