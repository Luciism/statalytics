FROM python:3.11.7-slim-bullseye AS base

ENV PYTHONPATH /app/


FROM base AS deps

WORKDIR /app

COPY ./apps/trackers/requirements.txt trackers/requirements.txt
RUN pip install -r trackers/requirements.txt

COPY ./statalib/requirements.txt statalib/requirements.txt
RUN pip install -r statalib/requirements.txt


FROM deps AS builder

COPY ./assets/ assets/
COPY ./statalib/ statalib/
COPY ./config.json ./config.dev.json ./schema.sql ./

COPY ./apps/trackers/main.py trackers/main.py


FROM builder AS runner

WORKDIR /app/trackers/
ENTRYPOINT [ "python3", "main.py" ]
