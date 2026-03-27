FROM python:3.11.11-slim-bullseye AS base

ENV PYTHONPATH /app/


FROM base AS deps

WORKDIR /app

RUN pip install uv
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --group=tests --frozen


FROM deps AS builder

COPY ./assets/ assets/
COPY ./statalib/ statalib/
COPY ./tests/ tests/
COPY ./run_tests.py ./
COPY ./config.json ./config.dev.json ./schema.sql ./commands.json ./


FROM builder AS runner

WORKDIR /app/

ENTRYPOINT [ "/app/.venv/bin/python3", "run_tests.py" ]
