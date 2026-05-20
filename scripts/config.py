from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class WarehouseConfig:
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    database: str = os.getenv("POSTGRES_DB", "warehouse")
    user: str = os.getenv("POSTGRES_USER", "warehouse")
    password: str = os.getenv("POSTGRES_PASSWORD", "warehouse")
    raw_schema: str = os.getenv("WAREHOUSE_SCHEMA_RAW", "raw")

    @property
    def dsn(self) -> str:
        return (
            f"host={self.host} port={self.port} dbname={self.database} "
            f"user={self.user} password={self.password}"
        )
