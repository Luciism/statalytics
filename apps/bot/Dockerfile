FROM python:3.11.7-slim-bullseye

WORKDIR /app

COPY ./apps/bot/requirements.txt bot/requirements.txt
RUN pip install -r bot/requirements.txt

COPY ./statalib/requirements.txt statalib/requirements.txt
RUN pip install -r statalib/requirements.txt

COPY ./apps/bot/helper/ bot/helper/
COPY ./apps/bot/calc/ bot/calc/
COPY ./apps/bot/cogs/ bot/cogs/
COPY ./apps/bot/render/ bot/render/
COPY ./apps/bot/main.py bot/main.py

# Optional
COPY ./apps/bot/tips.json* bot/tips.json

COPY ./assets/ assets/
COPY ./statalib/ statalib/
COPY ./config.json config.json
COPY ./config.dev.json config.dev.json
COPY ./schema.sql schema.sql

ENV PYTHONPATH /app/
WORKDIR /app/bot/

ENTRYPOINT [ "python3", "main.py" ]
