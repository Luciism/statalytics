FROM python:3.11.11-slim-bullseye AS base

ENV PYTHONPATH /app/


FROM base AS deps

WORKDIR /app

COPY ./statalib/requirements.txt statalib/requirements.txt
RUN pip install -r statalib/requirements.txt


FROM deps AS builder

COPY ./assets/ assets/
COPY ./statalib/ statalib/
COPY ./tests/ tests/
COPY ./run_tests.py ./
COPY ./config.json ./config.dev.json ./schema.sql ./


FROM builder AS runner

WORKDIR /app/

ENTRYPOINT [ "python3", "run_tests.py" ]
