from __future__ import annotations

import argparse
import logging
from datetime import datetime
from typing import Iterable

import psycopg2
from psycopg2.extras import execute_values

from scripts.config import WarehouseConfig
from scripts.sample_data import build_customers, build_events, build_orders, build_products

LOGGER = logging.getLogger(__name__)


DDL = {
    "raw_customers": """
        CREATE TABLE IF NOT EXISTS raw.raw_customers (
            customer_id TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            country TEXT NOT NULL,
            city TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (customer_id, updated_at)
        );
    """,
    "raw_products": """
        CREATE TABLE IF NOT EXISTS raw.raw_products (
            product_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price NUMERIC(12,2) NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (product_id, updated_at)
        );
    """,
    "raw_orders": """
        CREATE TABLE IF NOT EXISTS raw.raw_orders (
            order_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            ordered_at TIMESTAMPTZ NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price NUMERIC(12,2) NOT NULL,
            discount_amount NUMERIC(12,2) NOT NULL,
            status TEXT NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL,
            ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (order_id, updated_at)
        );
    """,
    "raw_events": """
        CREATE TABLE IF NOT EXISTS raw.raw_events (
            event_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            event_name TEXT NOT NULL,
            occurred_at TIMESTAMPTZ NOT NULL,
            utm_source TEXT NOT NULL,
            loaded_at TIMESTAMPTZ NOT NULL
        );
    """,
}


def _load_rows(
    cursor: psycopg2.extensions.cursor,
    table: str,
    columns: list[str],
    rows: Iterable[dict[str, object]],
) -> int:
    row_list = list(rows)
    if not row_list:
        return 0

    values = [tuple(row[column] for column in columns) for row in row_list]
    sql = f"""
        INSERT INTO raw.{table} ({", ".join(columns)})
        VALUES %s
        ON CONFLICT DO NOTHING;
    """
    execute_values(cursor, sql, values)
    return cursor.rowcount


def ingest(run_id: str, data_interval_start: datetime, data_interval_end: datetime) -> int:
    config = WarehouseConfig()
    loaded_rows = 0

    with psycopg2.connect(config.dsn) as conn, conn.cursor() as cursor:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {config.raw_schema};")
        for ddl in DDL.values():
            cursor.execute(ddl)

        loaded_rows += _load_rows(
            cursor,
            "raw_customers",
            ["customer_id", "full_name", "email", "country", "city", "created_at", "updated_at"],
            build_customers(),
        )
        loaded_rows += _load_rows(
            cursor,
            "raw_products",
            ["product_id", "product_name", "category", "unit_price", "updated_at"],
            build_products(),
        )
        loaded_rows += _load_rows(
            cursor,
            "raw_orders",
            [
                "order_id",
                "customer_id",
                "product_id",
                "ordered_at",
                "quantity",
                "unit_price",
                "discount_amount",
                "status",
                "updated_at",
            ],
            build_orders(),
        )
        loaded_rows += _load_rows(
            cursor,
            "raw_events",
            [
                "event_id",
                "customer_id",
                "session_id",
                "event_name",
                "occurred_at",
                "utm_source",
                "loaded_at",
            ],
            build_events(),
        )
        cursor.execute(
            """
            INSERT INTO raw.pipeline_runs (
                run_id, dag_id, data_interval_start, data_interval_end, status, rows_loaded
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE
            SET status = EXCLUDED.status,
                rows_loaded = EXCLUDED.rows_loaded,
                created_at = now();
            """,
            (
                run_id,
                "ecommerce_warehouse_elt",
                data_interval_start,
                data_interval_end,
                "raw_loaded",
                loaded_rows,
            ),
        )

    LOGGER.info("Raw ingestion complete", extra={"run_id": run_id, "rows_loaded": loaded_rows})
    return loaded_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load deterministic source data into raw PostgreSQL tables."
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--data-interval-start", required=True)
    parser.add_argument("--data-interval-end", required=True)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()
    ingest(
        run_id=args.run_id,
        data_interval_start=datetime.fromisoformat(args.data_interval_start),
        data_interval_end=datetime.fromisoformat(args.data_interval_end),
    )


if __name__ == "__main__":
    main()
