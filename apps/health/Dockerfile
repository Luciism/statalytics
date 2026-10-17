FROM python:3.11.11-slim-bullseye AS base

ENV PYTHONPATH /app/


FROM base AS deps

WORKDIR /app

RUN pip install uv
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --group=health --frozen


FROM deps AS builder

WORKDIR /app

# COPY ./assets/ assets/
# COPY ./statalib/ statalib/
# COPY ./config.json ./config.dev.json ./schema.sql ./commands.json ./

COPY ./apps/health/ health/


FROM builder AS runner

WORKDIR /app/health
ENTRYPOINT [ "/app/.venv/bin/fastapi", "run", "app.py", "--host=0.0.0.0", "--port=8000", "--workers=2"]
