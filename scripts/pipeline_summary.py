from __future__ import annotations

import argparse
import logging

import psycopg2

from scripts.config import WarehouseConfig

LOGGER = logging.getLogger(__name__)


def summarize(run_id: str) -> dict[str, int | str]:
    config = WarehouseConfig()
    query = """
        SELECT
            (SELECT count(*) FROM raw.raw_orders) AS raw_orders,
            (SELECT count(*) FROM silver.fct_orders) AS fact_orders,
            (SELECT count(*) FROM gold.customer_revenue_mart) AS mart_customers
    """
    with psycopg2.connect(config.dsn) as conn, conn.cursor() as cursor:
        cursor.execute(query)
        raw_orders, fact_orders, mart_customers = cursor.fetchone()
        cursor.execute(
            """
            UPDATE raw.pipeline_runs
            SET status = 'completed',
                rows_loaded = %s
            WHERE run_id = %s;
            """,
            (raw_orders, run_id),
        )

    summary = {
        "run_id": run_id,
        "raw_orders": raw_orders,
        "fact_orders": fact_orders,
        "mart_customers": mart_customers,
    }
    LOGGER.info("Pipeline summary: %s", summary)
    return summary


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(
        description="Log final warehouse row counts for observability."
    )
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    summarize(args.run_id)


if __name__ == "__main__":
    main()
