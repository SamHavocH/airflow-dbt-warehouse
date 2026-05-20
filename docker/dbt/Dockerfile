FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY docker/dbt/requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

ENV DBT_PROFILES_DIR=/app/dbt
