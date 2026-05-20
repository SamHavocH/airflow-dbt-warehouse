from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt")
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR", DBT_PROJECT_DIR)
DBT_TARGET = os.getenv("DBT_TARGET", "dev")

default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="ecommerce_warehouse_elt",
    description=(
        "Local production-style ELT pipeline: ingest raw data, run dbt, "
        "test marts, and log summary."
    ),
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=30),
    tags=["portfolio", "elt", "dbt", "postgres"],
) as dag:
    start = EmptyOperator(task_id="start")

    ingest_raw_data = BashOperator(
        task_id="ingest_raw_data",
        bash_command=(
            "python /opt/airflow/scripts/ingest_raw_data.py "
            "--run-id '{{ run_id }}' "
            "--data-interval-start '{{ data_interval_start.isoformat() }}' "
            "--data-interval-end '{{ data_interval_end.isoformat() }}'"
        ),
        env={
            **os.environ,
            "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "postgres"),
            "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "5432"),
            "POSTGRES_DB": os.getenv("POSTGRES_DB", "warehouse"),
            "POSTGRES_USER": os.getenv("POSTGRES_USER", "warehouse"),
            "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "warehouse"),
        },
        append_env=True,
    )

    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt deps --profiles-dir {DBT_PROFILES_DIR}",
        append_env=True,
    )

    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && dbt seed "
            f"--profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
        append_env=True,
    )

    dbt_run_bronze_silver = BashOperator(
        task_id="dbt_run_bronze_silver",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && dbt run --select bronze silver "
            f"--profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
        append_env=True,
    )

    dbt_test_bronze_silver = BashOperator(
        task_id="dbt_test_bronze_silver",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && dbt test --select bronze silver "
            f"--profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
        append_env=True,
    )

    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && dbt run --select gold "
            f"--profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
        append_env=True,
    )

    dbt_test_gold = BashOperator(
        task_id="dbt_test_gold",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && dbt test --select gold "
            f"--profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
        append_env=True,
    )

    dbt_docs_generate = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && dbt docs generate "
            f"--profiles-dir {DBT_PROFILES_DIR} --target {DBT_TARGET}"
        ),
        append_env=True,
    )

    pipeline_summary = BashOperator(
        task_id="pipeline_summary",
        bash_command="python /opt/airflow/scripts/pipeline_summary.py --run-id '{{ run_id }}'",
        append_env=True,
    )

    end = EmptyOperator(task_id="end")

    (
        start
        >> ingest_raw_data
        >> dbt_deps
        >> dbt_seed
        >> dbt_run_bronze_silver
        >> dbt_test_bronze_silver
        >> dbt_run_gold
        >> dbt_test_gold
        >> dbt_docs_generate
        >> pipeline_summary
        >> end
    )
