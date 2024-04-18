FROM python:3.11.7-slim-bullseye

WORKDIR /app

COPY ./bot/requirements.txt bot/requirements.txt
RUN pip install -r bot/requirements.txt

COPY ./bot/statalib/requirements.txt bot/statalib/requirements.txt
RUN pip install -r bot/statalib/requirements.txt

COPY ./bot/assets/ bot/assets/
COPY ./bot/calc/ bot/calc/
COPY ./bot/cogs/ bot/cogs/
COPY ./bot/render/ bot/render/
COPY ./bot/config.json bot/config.json
COPY ./bot/main.py bot/main.py
COPY ./bot/statalib bot/statalib/
COPY ./schema.sql bot/schema.sql

ENV PYTHONPATH /app/bot/
WORKDIR /app/bot/

ENTRYPOINT [ "python3", "main.py" ]
