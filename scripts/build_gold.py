"""
Build gold.driver_session_summary and gold.team_session_summary in DuckDB.

Environment:
- F1_WAREHOUSE (optional): path to DuckDB file. Default:
      /Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb
- EXTERNAL_DATA_ROOT (optional, unused here unless you want consistency checks).

Guardrails:
- Reads silver tables only; writes to gold schema only.
- Fails fast with clear messages if required tables/columns are missing.
"""

import os
import sys

import duckdb


DEFAULT_WAREHOUSE = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"


def fail(msg: str) -> None:
    print(f"[error] {msg}")
    sys.exit(1)


def ensure_table_exists(con: duckdb.DuckDBPyConnection, table: str) -> None:
    try:
        con.execute(f"SELECT * FROM {table} LIMIT 0")
    except Exception as exc:
        fail(f"Missing required table {table}: {exc}")


def print_sample(con: duckdb.DuckDBPyConnection, table: str, limit: int = 3) -> list[str]:
    try:
        df = con.execute(f"SELECT * FROM {table} LIMIT {limit}").fetchdf()
        cols = list(df.columns)
        print(f"[info] {table} columns: {cols}")
        print(f"[info] {table} sample (first {limit} rows):")
        print(df)
        return cols
    except Exception as exc:
        fail(f"Failed to sample {table}: {exc}")


def assert_keys(cols: list[str], required: list[str], context: str) -> None:
    missing = [c for c in required if c not in cols]
    if missing:
        print(f"[error] In {context}, missing required columns: {missing}")
        print(f"[error] Actual columns: {cols}")
        sys.exit(1)


def build_driver_session_summary(con: duckdb.DuckDBPyConnection) -> None:
    ensure_table_exists(con, "silver.laps")
    ensure_table_exists(con, "silver.session_results")
    ensure_table_exists(con, "silver.drivers")

    laps_cols = print_sample(con, "silver.laps")
    sr_cols = print_sample(con, "silver.session_results")
    drv_cols = print_sample(con, "silver.drivers")

    required_keys = [
        "season",
        "round",
        "grand_prix_slug",
        "session_code",
        "meeting_key",
        "session_key",
        "driver_number",
    ]
    for cols, ctx in [
        (laps_cols, "silver.laps"),
        (sr_cols, "silver.session_results"),
        (drv_cols, "silver.drivers"),
    ]:
        assert_keys(cols, required_keys, ctx)

    # Optional fields in drivers
    def col_or_null(name: str, cols: list[str]) -> str:
        return name if name in cols else "NULL"

    driver_fields = {
        "driver_name": "driver_name" if "driver_name" in drv_cols else "NULL",
        "driver_code": "driver_code" if "driver_code" in drv_cols else "NULL",
        "broadcast_name": col_or_null("broadcast_name", drv_cols),
        "first_name": col_or_null("first_name", drv_cols),
        "last_name": col_or_null("last_name", drv_cols),
        "team_name": col_or_null("team_name", drv_cols),
        "team_colour": col_or_null("team_colour", drv_cols),
        "country_code": col_or_null("country_code", drv_cols),
        "headshot_url": col_or_null("headshot_url", drv_cols),
    }

    # Optional fields in session_results
    sr_fields = {
        "finish_position": "position" if "position" in sr_cols else "NULL",
        "grid_position": "grid_position" if "grid_position" in sr_cols else "NULL",
        "status": "status" if "status" in sr_cols else "NULL",
        "points": "points" if "points" in sr_cols else "NULL",
    }

    sql = f"""
    DROP TABLE IF EXISTS gold.driver_session_summary;
    CREATE TABLE gold.driver_session_summary AS
    WITH base AS (
      SELECT
        l.season,
        l.round,
        l.grand_prix_slug,
        l.session_code,
        l.meeting_key,
        l.session_key,
        l.driver_number,
        {driver_fields['driver_name']}    AS driver_name,
        {driver_fields['driver_code']}    AS driver_code,
        {driver_fields['broadcast_name']} AS broadcast_name,
        {driver_fields['first_name']}     AS first_name,
        {driver_fields['last_name']}      AS last_name,
        CASE
          WHEN {driver_fields['team_name']} = 'RB' THEN 'Visa Cash App Racing Bulls'
          ELSE {driver_fields['team_name']}
        END                              AS team_name,
        {driver_fields['team_colour']}    AS team_colour,
        {driver_fields['country_code']}   AS country_code,
        {driver_fields['headshot_url']}   AS headshot_url,
        {sr_fields['finish_position']}    AS finish_position,
        {sr_fields['grid_position']}      AS grid_position,
        {sr_fields['status']}             AS status,
        {sr_fields['points']}             AS points,
        l.lap_duration,
        l.date_start
      FROM silver.laps l
      LEFT JOIN silver.drivers d
        USING (season, round, grand_prix_slug, session_code,
               meeting_key, session_key, driver_number)
      LEFT JOIN silver.session_results sr
        USING (season, round, grand_prix_slug, session_code,
               meeting_key, session_key, driver_number)
    )
    SELECT
      season,
      round,
      grand_prix_slug,
      session_code,
      meeting_key,
      session_key,
      driver_number,
      driver_name,
      driver_code,
      broadcast_name,
      first_name,
      last_name,
      team_name,
      team_colour,
      country_code,
      headshot_url,
      finish_position,
      grid_position,
      status,
      points,
      COUNT(*) AS total_laps,
      COUNT(*) FILTER (WHERE lap_duration IS NOT NULL) AS laps_with_time,
      MIN(lap_duration) AS best_lap_duration,
      MEDIAN(lap_duration) AS median_lap_duration,
      AVG(lap_duration) AS avg_lap_duration,
      MIN(date_start) AS first_lap_start_time,
      MAX(date_start) AS last_lap_start_time
    FROM base
    GROUP BY
      season,
      round,
      grand_prix_slug,
      session_code,
      meeting_key,
      session_key,
      driver_number,
      driver_name,
      driver_code,
      broadcast_name,
      first_name,
      last_name,
      team_name,
      team_colour,
      country_code,
      headshot_url,
      finish_position,
      grid_position,
      status,
      points;
    """
    print("[sql] gold.driver_session_summary DDL:")
    print(sql)
    con.execute(sql)


def build_team_session_summary(con: duckdb.DuckDBPyConnection) -> None:
    ensure_table_exists(con, "gold.driver_session_summary")
    use_mode = True
    mode_expr = "mode() WITHIN GROUP (ORDER BY country_code)"
    try:
        con.execute(f"SELECT {mode_expr} FROM gold.driver_session_summary LIMIT 1").fetchone()
    except Exception as exc:
        print(f"[warn] mode() not available or failed ({exc}); will set team_country=NULL")
        use_mode = False
    team_country_expr = mode_expr if use_mode else "NULL"

    sql = f"""
    DROP TABLE IF EXISTS gold.team_session_summary;
    CREATE TABLE gold.team_session_summary AS
    SELECT
      season,
      round,
      grand_prix_slug,
      session_code,
      team_name,
      {team_country_expr} AS team_country,
      COUNT(DISTINCT driver_number) AS drivers_count,
      SUM(total_laps) AS total_laps_team,
      MIN(best_lap_duration) AS best_lap_duration_team,
      AVG(best_lap_duration) AS avg_best_lap_duration_team,
      AVG(CAST(finish_position AS DOUBLE)) FILTER (WHERE finish_position IS NOT NULL) AS avg_finish_position,
      SUM(points) AS points_team
    FROM gold.driver_session_summary
    GROUP BY
      season,
      round,
      grand_prix_slug,
      session_code,
      team_name;
    """
    print("[sql] gold.team_session_summary DDL:")
    print(sql)
    con.execute(sql)


def build_driver_sprint_standings(con: duckdb.DuckDBPyConnection) -> None:
    ensure_table_exists(con, "gold.driver_session_summary")
    cols = [r[1] for r in con.execute("PRAGMA table_info('gold.driver_session_summary')").fetchall()]
    required = [
        "season",
        "round",
        "grand_prix_slug",
        "session_code",
        "driver_number",
        "driver_name",
        "driver_code",
        "team_name",
        "points",
    ]
    missing = [c for c in required if c not in cols]
    if missing:
        raise RuntimeError(
            f"Schema mismatch – missing columns in gold.driver_session_summary: {missing}. Actual: {cols}"
        )

    sql = """
    CREATE OR REPLACE TABLE gold.driver_sprint_standings AS
    WITH per_round AS (
      SELECT
        season,
        round,
        MIN(grand_prix_slug) AS grand_prix_slug,
        driver_number,
        MIN(driver_name) AS driver_name,
        MIN(driver_code) AS driver_code,
        MIN(team_name) AS team_name,
        SUM(points) AS sprint_points_round
      FROM gold.driver_session_summary
      WHERE session_code IN ('S','SQ')
        AND points IS NOT NULL
      GROUP BY season, round, driver_number
    ),
    cumulative AS (
      SELECT
        season,
        round,
        grand_prix_slug,
        driver_number,
        driver_name,
        driver_code,
        team_name,
        sprint_points_round,
        SUM(sprint_points_round) OVER (
          PARTITION BY season, driver_number
          ORDER BY round
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS sprint_points_cumulative
      FROM per_round
    )
    SELECT
      season,
      round,
      grand_prix_slug,
      driver_number,
      driver_name,
      driver_code,
      team_name,
      sprint_points_round,
      sprint_points_cumulative,
      DENSE_RANK() OVER (
        PARTITION BY season, round
        ORDER BY sprint_points_cumulative DESC
      ) AS sprint_championship_position
    FROM cumulative;
    """
    con.execute(sql)
    cnt = con.execute("SELECT count(*) FROM gold.driver_sprint_standings").fetchone()[0]
    print(f"[gold] built gold.driver_sprint_standings ({cnt} rows)")


def build_team_sprint_standings(con: duckdb.DuckDBPyConnection) -> None:
    ensure_table_exists(con, "gold.team_session_summary")
    cols = [r[1] for r in con.execute("PRAGMA table_info('gold.team_session_summary')").fetchall()]
    required = [
        "season",
        "round",
        "grand_prix_slug",
        "session_code",
        "team_name",
        "points_team",
    ]
    missing = [c for c in required if c not in cols]
    if missing:
        raise RuntimeError(
            f"Schema mismatch – missing columns in gold.team_session_summary: {missing}. Actual: {cols}"
        )

    sql = """
    CREATE OR REPLACE TABLE gold.team_sprint_standings AS
    WITH per_round AS (
      SELECT
        season,
        round,
        MIN(grand_prix_slug) AS grand_prix_slug,
        team_name,
        SUM(points_team) AS sprint_points_round_team
      FROM gold.team_session_summary
      WHERE session_code IN ('S','SQ')
        AND points_team IS NOT NULL
      GROUP BY season, round, team_name
    ),
    cumulative AS (
      SELECT
        season,
        round,
        grand_prix_slug,
        team_name,
        sprint_points_round_team,
        SUM(sprint_points_round_team) OVER (
          PARTITION BY season, team_name
          ORDER BY round
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS sprint_points_cumulative_team
      FROM per_round
    )
    SELECT
      season,
      round,
      grand_prix_slug,
      team_name,
      sprint_points_round_team,
      sprint_points_cumulative_team,
      DENSE_RANK() OVER (
        PARTITION BY season, round
        ORDER BY sprint_points_cumulative_team DESC
      ) AS sprint_championship_position_team
    FROM cumulative;
    """
    con.execute(sql)
    cnt = con.execute("SELECT count(*) FROM gold.team_sprint_standings").fetchone()[0]
    print(f"[gold] built gold.team_sprint_standings ({cnt} rows)")


def build_driver_season_standings(con: duckdb.DuckDBPyConnection) -> None:
    ensure_table_exists(con, "gold.driver_session_summary")
    cols = [r[1] for r in con.execute("PRAGMA table_info('gold.driver_session_summary')").fetchall()]
    required = [
        "season",
        "round",
        "grand_prix_slug",
        "session_code",
        "driver_number",
        "driver_name",
        "driver_code",
        "team_name",
        "points",
        "finish_position",
    ]
    missing = [c for c in required if c not in cols]
    if missing:
        raise RuntimeError(
            f"Schema mismatch – missing columns in gold.driver_session_summary: {missing}. Actual: {cols}"
        )

    sql = """
    CREATE OR REPLACE TABLE gold.driver_season_standings AS
    WITH per_round AS (
      SELECT
        season,
        round,
        MIN(grand_prix_slug) AS grand_prix_slug,
        driver_number,
        MIN(driver_name) AS driver_name,
        MIN(driver_code) AS driver_code,
        MIN(team_name) AS team_name,
        SUM(points) AS points_round,
        AVG(CAST(finish_position AS DOUBLE)) AS avg_finish_round,
        COUNT(DISTINCT grand_prix_slug) AS races_entered_round
      FROM gold.driver_session_summary
      WHERE points IS NOT NULL
      GROUP BY season, round, driver_number
    ),
    cumulative AS (
      SELECT
        season,
        round,
        grand_prix_slug,
        driver_number,
        driver_name,
        driver_code,
        team_name,
        points_round,
        avg_finish_round,
        races_entered_round,
        SUM(points_round) OVER (
          PARTITION BY season, driver_number
          ORDER BY round
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS points_cumulative
      FROM per_round
    )
    SELECT
      season,
      round,
      grand_prix_slug,
      driver_number,
      driver_name,
      driver_code,
      team_name,
      points_round,
      points_cumulative,
      avg_finish_round,
      races_entered_round,
      RANK() OVER (
        PARTITION BY season, round
        ORDER BY points_cumulative DESC
      ) AS championship_position
    FROM cumulative;
    """
    con.execute(sql)
    cnt = con.execute("SELECT count(*) FROM gold.driver_season_standings").fetchone()[0]
    print(f"[gold] built gold.driver_season_standings ({cnt} rows)")


def build_team_season_standings(con: duckdb.DuckDBPyConnection) -> None:
    ensure_table_exists(con, "gold.team_session_summary")
    cols = [r[1] for r in con.execute("PRAGMA table_info('gold.team_session_summary')").fetchall()]
    required = [
        "season",
        "round",
        "grand_prix_slug",
        "session_code",
        "team_name",
        "points_team",
    ]
    missing = [c for c in required if c not in cols]
    if missing:
        raise RuntimeError(
            f"Schema mismatch – missing columns in gold.team_session_summary: {missing}. Actual: {cols}"
        )

    sql = """
    CREATE OR REPLACE TABLE gold.team_season_standings AS
    WITH per_round AS (
      SELECT
        season,
        round,
        MIN(grand_prix_slug) AS grand_prix_slug,
        team_name,
        SUM(points_team) AS points_round_team,
        COUNT(DISTINCT grand_prix_slug) AS races_entered_round
      FROM gold.team_session_summary
      WHERE points_team IS NOT NULL
      GROUP BY season, round, team_name
    ),
    cumulative AS (
      SELECT
        season,
        round,
        grand_prix_slug,
        team_name,
        points_round_team,
        races_entered_round,
        SUM(points_round_team) OVER (
          PARTITION BY season, team_name
          ORDER BY round
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS points_cumulative_team
      FROM per_round
    )
    SELECT
      season,
      round,
      grand_prix_slug,
      team_name,
      points_round_team,
      points_cumulative_team,
      races_entered_round,
      RANK() OVER (
        PARTITION BY season, round
        ORDER BY points_cumulative_team DESC
      ) AS championship_position_team
    FROM cumulative;
    """
    con.execute(sql)
    cnt = con.execute("SELECT count(*) FROM gold.team_season_standings").fetchone()[0]
    print(f"[gold] built gold.team_season_standings ({cnt} rows)")


def main() -> None:
    warehouse_path = os.getenv("F1_WAREHOUSE", DEFAULT_WAREHOUSE)
    print(f"[info] warehouse_path={warehouse_path}")
    con = duckdb.connect(warehouse_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS gold;")

    build_driver_session_summary(con)
    build_team_session_summary(con)
    build_driver_season_standings(con)
    build_team_season_standings(con)
    build_driver_sprint_standings(con)
    build_team_sprint_standings(con)

    drv_cnt = con.execute("SELECT count(*) FROM gold.driver_session_summary").fetchone()[0]
    team_cnt = con.execute("SELECT count(*) FROM gold.team_session_summary").fetchone()[0]
    drv_season_cnt = con.execute("SELECT count(*) FROM gold.driver_season_standings").fetchone()[0]
    team_season_cnt = con.execute("SELECT count(*) FROM gold.team_season_standings").fetchone()[0]
    drv_sprint_cnt = con.execute("SELECT count(*) FROM gold.driver_sprint_standings").fetchone()[0]
    team_sprint_cnt = con.execute("SELECT count(*) FROM gold.team_sprint_standings").fetchone()[0]
    print(f"[info] gold.driver_session_summary row count: {drv_cnt}")
    print(f"[info] gold.team_session_summary row count: {team_cnt}")
    print(f"[info] gold.driver_season_standings row count: {drv_season_cnt}")
    print(f"[info] gold.team_season_standings row count: {team_season_cnt}")
    print(f"[info] gold.driver_sprint_standings row count: {drv_sprint_cnt}")
    print(f"[info] gold.team_sprint_standings row count: {team_sprint_cnt}")

    print("[info] gold.driver_session_summary preview:")
    print(
        con.execute(
            """
            SELECT
              season, round, grand_prix_slug, session_code,
              driver_number, driver_name, driver_code,
              team_name, finish_position, grid_position,
              best_lap_duration, total_laps
            FROM gold.driver_session_summary
            ORDER BY season, round, session_code, driver_number
            LIMIT 20
            """
        ).fetchdf()
    )

    print("[info] gold.team_session_summary preview:")
    print(
        con.execute(
            """
            SELECT
              season, round, grand_prix_slug, session_code,
              team_name, drivers_count, total_laps_team,
              best_lap_duration_team, points_team
            FROM gold.team_session_summary
            ORDER BY season, round, session_code, team_name
            LIMIT 20
            """
        ).fetchdf()
    )

    print("[info] gold.driver_season_standings preview:")
    print(
        con.execute(
            """
            SELECT
              season, round, grand_prix_slug,
              driver_number, driver_name, driver_code,
              team_name, points_round, points_cumulative,
              championship_position
            FROM gold.driver_season_standings
            ORDER BY season, round, championship_position
            LIMIT 20
            """
        ).fetchdf()
    )

    print("[info] gold.team_season_standings preview:")
    print(
        con.execute(
            """
            SELECT
              season, round, grand_prix_slug,
              team_name, points_round_team, points_cumulative_team,
              championship_position_team
            FROM gold.team_season_standings
            ORDER BY season, round, championship_position_team
            LIMIT 20
            """
        ).fetchdf()
    )

    print("[info] gold.driver_sprint_standings preview (latest season):")
    print(
        con.execute(
            """
            WITH latest AS (
              SELECT MAX(season) AS s FROM gold.driver_sprint_standings
            )
            SELECT
              season, round, grand_prix_slug,
              driver_number, driver_name, driver_code,
              team_name, sprint_points_round, sprint_points_cumulative,
              sprint_championship_position
            FROM gold.driver_sprint_standings
            WHERE season = (SELECT s FROM latest)
            ORDER BY season, round, sprint_championship_position
            LIMIT 5
            """
        ).fetchdf()
    )

    print("[info] gold.team_sprint_standings preview (latest season):")
    print(
        con.execute(
            """
            WITH latest AS (
              SELECT MAX(season) AS s FROM gold.team_sprint_standings
            )
            SELECT
              season, round, grand_prix_slug,
              team_name, sprint_points_round_team, sprint_points_cumulative_team,
              sprint_championship_position_team
            FROM gold.team_sprint_standings
            WHERE season = (SELECT s FROM latest)
            ORDER BY season, round, sprint_championship_position_team
            LIMIT 5
            """
        ).fetchdf()
    )

    print(f"[success] gold tables built at {warehouse_path}")


if __name__ == "__main__":
    main()
