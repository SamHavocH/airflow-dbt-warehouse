.DEFAULT_GOAL := help

COMPOSE := docker compose

.PHONY: help up down run test dbt-build dbt-docs airflow-shell logs clean

help:
	@echo "Commands:"
	@echo "  make up          Build and start Postgres, Airflow webserver, and scheduler"
	@echo "  make run         Trigger the Airflow ELT DAG once"
	@echo "  make test        Run Python tests, dbt deps/parse/build, and pre-commit checks"
	@echo "  make dbt-build   Run dbt build in the dbt container"
	@echo "  make dbt-docs    Generate dbt docs"
	@echo "  make down        Stop local services"

up:
	$(COMPOSE) up --build -d postgres airflow-init airflow-webserver airflow-scheduler

down:
	$(COMPOSE) down

run:
	$(COMPOSE) exec airflow-scheduler airflow dags trigger ecommerce_warehouse_elt

dbt-build:
	$(COMPOSE) run --rm dbt dbt deps
	$(COMPOSE) run --rm dbt dbt build --target $${DBT_TARGET:-dev}

dbt-docs:
	$(COMPOSE) run --rm dbt dbt docs generate --target $${DBT_TARGET:-dev}

test:
	python -m pytest
	$(COMPOSE) run --rm dbt dbt deps
	$(COMPOSE) run --rm dbt dbt parse --target $${DBT_TARGET:-dev}
	pre-commit run --all-files

airflow-shell:
	$(COMPOSE) exec airflow-scheduler bash

logs:
	$(COMPOSE) logs -f airflow-scheduler airflow-webserver

clean:
	$(COMPOSE) down -v
