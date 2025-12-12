import os
from functools import lru_cache

import duckdb

DEFAULT_WAREHOUSE = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"


@lru_cache(maxsize=1)
def get_warehouse_path() -> str:
    path = os.getenv("F1_WAREHOUSE", DEFAULT_WAREHOUSE)
    if not os.path.exists(path):
        # Do NOT create the file here – this must already exist.
        raise FileNotFoundError(f"DuckDB warehouse not found at {path}")
    return path


def connect_ro() -> duckdb.DuckDBPyConnection:
    path = get_warehouse_path()
    # DuckDB may need write access for temp tables; enforce SELECT-only at API layer.
    return duckdb.connect(path, read_only=False)
