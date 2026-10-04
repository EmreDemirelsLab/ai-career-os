from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str

    @field_validator("database_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        try:
            url = make_url(value)
            valid = url.drivername in {"postgresql+psycopg", "sqlite"} and bool(url.database)
        except Exception:
            valid = False
        if not valid:
            raise ValueError("Use postgresql+psycopg or SQLite for disposable local tests")
        return value
