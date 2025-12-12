"""
Build silver.laps, silver.session_results, and silver.drivers in DuckDB from bronze Parquet.

Environment:
- EXTERNAL_DATA_ROOT (required): host path containing bronze (e.g., /Volumes/SAMSUNG/apps/f1-dash).
- F1_WAREHOUSE (optional): override warehouse path. Default:
      /Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb

Guardrails:
- Only touches silver.laps, silver.session_results, silver.drivers (drops/recreates).
- Stops with clear messages if required env vars or columns are missing.
- Avoids reading unused problematic columns (e.g., duration DOUBLE vs DOUBLE[] in session_result).
"""

import glob
import os
import sys
from pathlib import Path
from typing import Iterable, Set

import duckdb
import pyarrow.parquet as pq


def fail(msg: str) -> None:
    print(f"[error] {msg}")
    sys.exit(1)


def get_env_paths() -> tuple[Path, Path]:
    external_root = os.getenv("EXTERNAL_DATA_ROOT")
    if not external_root:
        fail("EXTERNAL_DATA_ROOT is not set. Please export it before running this script.")
    bronze_root = Path(external_root) / "bronze"
    if not bronze_root.exists():
        fail(f"Bronze root does not exist: {bronze_root}")
    warehouse_path = Path(
        os.getenv("F1_WAREHOUSE", "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb")
    )
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    return bronze_root, warehouse_path


def fetch_sample(con: duckdb.DuckDBPyConnection, sql: str, label: str):
    try:
        df = con.execute(sql).fetchdf()
        print(f"[info] Sample for {label}: {len(df)} rows")
        print(f"[info] Columns for {label}: {list(df.columns)}")
        return df
    except Exception as exc:
        print(f"[warn] Sample failed for {label}: {exc}")
        return None


def assert_columns(actual: Iterable[str], required: list[str], context: str):
    actual_list = list(actual)
    missing = [c for c in required if c not in actual_list]
    if missing:
        print(f"[error] In {context}, missing required columns: {missing}")
        print(f"[error] Actual columns: {actual_list}")
        sys.exit(1)


def get_columns_from_parquet_files(glob_path: str) -> Set[str]:
    files = glob.glob(glob_path, recursive=True)
    if not files:
        fail(f"No Parquet files found for pattern: {glob_path}")
    cols: Set[str] = set()
    for fp in files:
        try:
            schema = pq.ParquetFile(fp).schema
            cols.update(schema.names)
        except Exception as exc:
            print(f"[warn] Could not read schema from {fp}: {exc}")
            continue
    if not cols:
        fail(f"Could not determine columns from any Parquet file matching {glob_path}")
    return cols


def build_silver_laps(con: duckdb.DuckDBPyConnection, bronze_root: Path):
    src = f"{bronze_root}/laps/**/*.parquet"
    scan = f"read_parquet('{src}', hive_partitioning=1, union_by_name=true)"

    sample_df = fetch_sample(con, f"select * from {scan} limit 5", "bronze.laps")
    if sample_df is None:
        fail("Unable to read sample from bronze.laps; cannot proceed.")

    required_cols = [
        "season",
        "round",
        "grand_prix_slug",
        "session_code",
        "meeting_key",
        "session_key",
        "driver_number",
        "lap_number",
        "date_start",
        "lap_duration",
        "duration_sector_1",
        "duration_sector_2",
        "duration_sector_3",
        "ingested_at",
    ]
    assert_columns(sample_df.columns, required_cols, "bronze.laps")

    sql = f"""
    DROP TABLE IF EXISTS silver.laps;
    CREATE TABLE silver.laps AS
    SELECT
      CAST(season AS INTEGER)          AS season,
      CAST(round AS INTEGER)           AS round,
      CAST(grand_prix_slug AS VARCHAR) AS grand_prix_slug,
      CAST(session_code AS VARCHAR)    AS session_code,
      CAST(meeting_key AS INTEGER)     AS meeting_key,
      CAST(session_key AS INTEGER)     AS session_key,
      CAST(driver_number AS INTEGER)   AS driver_number,
      CAST(lap_number AS INTEGER)      AS lap_number,
      TRY_CAST(date_start AS TIMESTAMP)        AS date_start,
      TRY_CAST(lap_duration AS DOUBLE)         AS lap_duration,
      TRY_CAST(duration_sector_1 AS DOUBLE)    AS duration_sector_1,
      TRY_CAST(duration_sector_2 AS DOUBLE)    AS duration_sector_2,
      TRY_CAST(duration_sector_3 AS DOUBLE)    AS duration_sector_3,
      TRY_CAST(ingested_at AS TIMESTAMP)       AS ingested_at,
      * EXCLUDE (
        season, round, grand_prix_slug, session_code,
        meeting_key, session_key,
        driver_number, lap_number,
        date_start, lap_duration,
        duration_sector_1, duration_sector_2, duration_sector_3,
        ingested_at
      )
    FROM {scan};
    """
    print("[sql] silver.laps DDL:")
    print(sql)
    con.execute(sql)


def build_silver_session_results(con: duckdb.DuckDBPyConnection, bronze_root: Path):
    src = f"{bronze_root}/session_result/**/*.parquet"
    scan = f"read_parquet('{src}', hive_partitioning=1, union_by_name=true)"

    sample_df = fetch_sample(con, f"select * from {scan} limit 5", "bronze.session_result")
    if sample_df is not None:
        columns_set = set(sample_df.columns)
    else:
        print("[info] Falling back to schema inspection for session_result due to sample failure.")
        columns_set = get_columns_from_parquet_files(src)
        print(f"[info] Columns from schema inspection: {sorted(columns_set)}")

    required_cols = [
        "season",
        "round",
        "grand_prix_slug",
        "session_code",
        "meeting_key",
        "session_key",
        "driver_number",
    ]
    assert_columns(columns_set, required_cols, "bronze.session_result")

    has_position = "position" in columns_set
    has_grid = "grid_position" in columns_set
    has_status = "status" in columns_set
    has_points = "points" in columns_set

    select_parts = [
        "CAST(season AS INTEGER)          AS season",
        "CAST(round AS INTEGER)           AS round",
        "CAST(grand_prix_slug AS VARCHAR) AS grand_prix_slug",
        "CAST(session_code AS VARCHAR)    AS session_code",
        "CAST(meeting_key AS INTEGER)     AS meeting_key",
        "CAST(session_key AS INTEGER)     AS session_key",
        "CAST(driver_number AS INTEGER)   AS driver_number",
        f"{'TRY_CAST(position AS INTEGER)' if has_position else 'NULL'} AS position",
        f"{'TRY_CAST(grid_position AS INTEGER)' if has_grid else 'NULL'} AS grid_position",
        f"{'status' if has_status else 'NULL'} AS status",
        f"{'TRY_CAST(points AS DOUBLE)' if has_points else 'NULL'} AS points",
    ]

    sql = f"""
    DROP TABLE IF EXISTS silver.session_results;
    CREATE TABLE silver.session_results AS
    SELECT
      {', '.join(select_parts)}
    FROM {scan};
    """
    print("[sql] silver.session_results DDL:")
    print(sql)
    con.execute(sql)


def build_silver_drivers(con: duckdb.DuckDBPyConnection, bronze_root: Path):
    src = f"{bronze_root}/drivers/**/*.parquet"
    scan = f"read_parquet('{src}', hive_partitioning=1, union_by_name=true)"

    sample_df = fetch_sample(con, f"select * from {scan} limit 5", "bronze.drivers")
    if sample_df is not None:
        columns_set = set(sample_df.columns)
    else:
        print("[info] Falling back to schema inspection for drivers due to sample failure.")
        columns_set = get_columns_from_parquet_files(src)
        print(f"[info] Columns from schema inspection: {sorted(columns_set)}")

    required_cols = [
        "season",
        "round",
        "grand_prix_slug",
        "session_code",
        "meeting_key",
        "session_key",
        "driver_number",
        "full_name",
        "name_acronym",
        "team_name",
        "team_colour",
        "country_code",
        "ingested_at",
    ]
    assert_columns(columns_set, required_cols, "bronze.drivers")

    # Soft/optional attributes
    broadcast_name_expr = "CAST(broadcast_name AS VARCHAR)" if "broadcast_name" in columns_set else "NULL"
    headshot_url_expr = "CAST(headshot_url AS VARCHAR)" if "headshot_url" in columns_set else "NULL"
    first_name_expr = "CAST(first_name AS VARCHAR)" if "first_name" in columns_set else "NULL"
    last_name_expr = "CAST(last_name AS VARCHAR)" if "last_name" in columns_set else "NULL"

    select_parts = [
        "CAST(season AS INTEGER)          AS season",
        "CAST(round AS INTEGER)           AS round",
        "CAST(grand_prix_slug AS VARCHAR) AS grand_prix_slug",
        "CAST(session_code AS VARCHAR)    AS session_code",
        "CAST(meeting_key AS INTEGER)     AS meeting_key",
        "CAST(session_key AS INTEGER)     AS session_key",
        "CAST(driver_number AS INTEGER)   AS driver_number",
        "CAST(full_name AS VARCHAR)       AS driver_name",
        "CAST(name_acronym AS VARCHAR)    AS driver_code",
        "CASE WHEN team_name = 'RB' THEN 'Visa Cash App Racing Bulls' ELSE CAST(team_name AS VARCHAR) END AS team_name",
        "CAST(team_colour AS VARCHAR)     AS team_colour",
        "CAST(country_code AS VARCHAR)    AS country_code",
        "TRY_CAST(ingested_at AS TIMESTAMP) AS ingested_at",
        f"{broadcast_name_expr}           AS broadcast_name",
        f"{headshot_url_expr}             AS headshot_url",
        f"{first_name_expr}               AS first_name",
        f"{last_name_expr}                AS last_name",
    ]

    sql = f"""
    DROP TABLE IF EXISTS silver.drivers;
    CREATE TABLE silver.drivers AS
    SELECT
      {', '.join(select_parts)}
    FROM {scan};
    """
    print("[sql] silver.drivers DDL:")
    print(sql)
    con.execute(sql)


def main() -> None:
    bronze_root, warehouse_path = get_env_paths()
    print(f"[info] bronze_root={bronze_root}")
    print(f"[info] warehouse_path={warehouse_path}")

    con = duckdb.connect(str(warehouse_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS silver;")

    build_silver_laps(con, bronze_root)
    build_silver_session_results(con, bronze_root)

    try:
        build_silver_drivers(con, bronze_root)
    except Exception as exc:
        print(f"[error] failed to build silver.drivers: {exc}")
        raise

    laps_cnt = con.execute("select count(*) from silver.laps").fetchone()[0]
    sess_cnt = con.execute("select count(*) from silver.session_results").fetchone()[0]
    drv_cnt = con.execute("select count(*) from silver.drivers").fetchone()[0]
    print(f"[info] silver.laps row count: {laps_cnt}")
    print(f"[info] silver.session_results row count: {sess_cnt}")
    print(f"[info] silver.drivers row count: {drv_cnt}")

    print("[info] silver.laps preview:")
    print(con.execute("select * from silver.laps limit 5").fetchdf())
    print("[info] silver.session_results preview:")
    print(con.execute("select * from silver.session_results limit 5").fetchdf())
    print("[info] silver.drivers preview:")
    print(con.execute("select * from silver.drivers limit 5").fetchdf())

    print(f"[success] silver.laps, silver.session_results, silver.drivers built successfully at {warehouse_path}")


if __name__ == "__main__":
    main()
