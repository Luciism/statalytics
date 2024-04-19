FROM python:3.11.7-slim-bullseye

WORKDIR /app

COPY ./apps/trackers/requirements.txt trackers/requirements.txt
RUN pip install -r trackers/requirements.txt

COPY ./statalib/requirements.txt statalib/requirements.txt
RUN pip install -r statalib/requirements.txt

COPY ./apps/trackers/main.py trackers/main.py

COPY ./assets/ assets/
COPY ./statalib/ statalib/
COPY ./config.json config.json
COPY ./config.dev.json config.dev.json
COPY ./schema.sql schema.sql

ENV PYTHONPATH /app/
WORKDIR /app/trackers/

ENTRYPOINT [ "python3", "main.py" ]
