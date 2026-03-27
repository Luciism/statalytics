FROM python:3.11.11-slim-bullseye AS base

ENV PYTHONPATH /app/


FROM base AS deps

WORKDIR /app

RUN pip install uv
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --group=bot --frozen


FROM deps AS builder

COPY ./assets/ assets/
COPY ./statalib/ statalib/
COPY ./config.json ./config.dev.json ./schema.sql ./commands.json ./

COPY ./apps/bot/ bot/


FROM builder AS runner

WORKDIR /app/bot
ENTRYPOINT [ "/app/.venv/bin/python3", "main.py" ]
