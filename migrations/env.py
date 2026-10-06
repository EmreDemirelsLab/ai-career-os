from alembic import context
from career_os import (  # noqa: F401
    auth,
    collection_models,
    intelligence_models,
    models,
    workspace_models,
)
from career_os.config import Settings
from career_os.db import Base
from sqlalchemy import create_engine

url = context.config.attributes.get("database_url") or Settings().database_url
if context.is_offline_mode():
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    with create_engine(url).connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
