FROM python:3.11.7-slim-bullseye

WORKDIR /app

COPY ./trackers/requirements.txt trackers/requirements.txt
RUN pip install -r trackers/requirements.txt

COPY ./bot/statalib/requirements.txt bot/statalib/requirements.txt
RUN pip install -r bot/statalib/requirements.txt

COPY ./bot/assets/ bot/assets/
COPY ./bot/config.json bot/config.json
COPY ./bot/statalib bot/statalib/
COPY ./trackers/main.py trackers/main.py
COPY ./schema.sql trackers/schema.sql

ENV PYTHONPATH /app/bot/
WORKDIR /app/trackers/

ENTRYPOINT [ "python3", "main.py" ]
