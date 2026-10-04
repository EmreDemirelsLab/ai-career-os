FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir uv==0.12.19
COPY pyproject.toml uv.lock ./
COPY apps/api apps/api
RUN uv sync --locked --no-dev
COPY alembic.ini ./
COPY migrations migrations
COPY seed seed
COPY tests/fixtures tests/fixtures
RUN useradd --create-home app
USER app
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "career_os.api:app", "--host", "0.0.0.0", "--port", "8000"]
