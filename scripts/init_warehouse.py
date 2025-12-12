import os
from pathlib import Path

import duckdb


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    warehouse_path = repo_root / "warehouse" / "f1_openf1.duckdb"
    bronze_laps = "/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/laps/**/*.parquet"
    bronze_results = "/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/session_result/**/*.parquet"

    os.makedirs(warehouse_path.parent, exist_ok=True)
    con = duckdb.connect(str(warehouse_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
    con.execute(
        f"""
        CREATE OR REPLACE VIEW bronze.laps AS
        SELECT *
        FROM read_parquet('{bronze_laps}', union_by_name=true);
        """
    )
    con.execute(
        f"""
        CREATE OR REPLACE VIEW bronze.session_result AS
        SELECT *
        FROM read_parquet('{bronze_results}', union_by_name=true);
        """
    )

    tables = con.execute("PRAGMA show_tables;").fetchdf()
    print("[init] warehouse:", warehouse_path)
    print("[init] tables/views:")
    print(tables)


if __name__ == "__main__":
    main()
