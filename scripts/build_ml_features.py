import argparse
import os
import sys
from textwrap import dedent

import duckdb

DEFAULT_WAREHOUSE = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"
DEFAULT_ROOT = "/Volumes/SAMSUNG/apps/f1-dash"


def bronze_path(relative: str) -> str:
    """
    Build an absolute path for bronze parquet globs.

    Allows EXTERNAL_DATA_ROOT override to point at a different lake root.
    """
    root = os.getenv("EXTERNAL_DATA_ROOT", DEFAULT_ROOT)
    return os.path.join(root, "bronze", relative)


def _table_exists(con: duckdb.DuckDBPyConnection, schema: str, table: str) -> bool:
    res = con.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = ? AND table_name = ?
        """,
        [schema, table],
    ).fetchone()
    return res is not None


def _table_columns(con: duckdb.DuckDBPyConnection, schema: str, table: str):
    try:
        rows = con.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = ? AND table_name = ?
            ORDER BY ordinal_position
            """,
            [schema, table],
        ).fetchall()
        return [r[0] for r in rows]
    except Exception as exc:  # pragma: no cover - diagnostic path
        return [f"<error reading columns: {exc}>"]


def _require_gold_tables(con: duckdb.DuckDBPyConnection):
    required = [
        ("gold", "driver_session_summary"),
        ("gold", "driver_season_standings"),
        ("gold", "team_season_standings"),
    ]
    missing = [(s, t) for s, t in required if not _table_exists(con, s, t)]
    if missing:
        print("Missing required gold tables:", ", ".join([f"{s}.{t}" for s, t in missing]))
        sys.exit(1)


def _print_sample(con: duckdb.DuckDBPyConnection, sql: str, label: str):
    rows = con.execute(sql).fetchall()
    print(f"\n{label}")
    for r in rows:
        print(r)


def build_race_win_training(con: duckdb.DuckDBPyConnection):
    debug_sql = """
    SELECT
      COUNT(*) AS total_race_rows,
      COUNT(*) FILTER (WHERE grid_position IS NOT NULL) AS race_with_grid,
      COUNT(*) FILTER (WHERE finish_position IS NOT NULL) AS race_with_finish
    FROM gold.driver_session_summary
    WHERE session_code = 'R' AND season >= 2020;
    """
    print("[debug] driver_session_summary race row counts:")
    print(con.execute(debug_sql).fetchall())

    sql = dedent(
        f"""
        DROP TABLE IF EXISTS features.race_win_training;
        CREATE TABLE features.race_win_training AS
        WITH driver_points AS (
          SELECT
            season,
            round,
            driver_number,
            points_cumulative,
            LAG(points_cumulative, 1, 0.0) OVER (
              PARTITION BY season, driver_number
              ORDER BY round
            ) AS points_cumulative_pre
          FROM gold.driver_season_standings
          WHERE season >= 2020
        ),
        team_points AS (
          SELECT
            season,
            round,
            team_name,
            points_cumulative_team,
            LAG(points_cumulative_team, 1, 0.0) OVER (
              PARTITION BY season, team_name
              ORDER BY round
            ) AS team_points_cumulative_pre
          FROM gold.team_season_standings
          WHERE season >= 2020
        ),
        race_base AS (
          SELECT
            dss.season,
            dss.round,
            dss.grand_prix_slug,
            dss.driver_number,
            dss.driver_name,
            dss.driver_code,
            dss.team_name,
            dss.grid_position,
            dss.finish_position,
            dss.points
          FROM gold.driver_session_summary dss
          WHERE dss.session_code = 'R'
            AND dss.season >= 2020
            AND dss.finish_position IS NOT NULL
        )
        SELECT
          r.season,
          r.round,
          r.grand_prix_slug,
          r.driver_number,
          r.driver_name,
          r.driver_code,
          r.team_name,
          COALESCE(r.grid_position, ft.grid_position) AS grid_position,
          r.finish_position,
          r.points AS points_race,
          dp.points_cumulative_pre      AS driver_points_pre,
          tp.team_points_cumulative_pre AS team_points_pre,
          CASE WHEN r.finish_position = 1 THEN 1 ELSE 0 END AS target_win_race,
          ft.track_temp_c,
          ft.rain_probability,
          ft.starting_compound_index,
          ft.starting_compound_raw
        FROM race_base r
        LEFT JOIN driver_points dp
          ON r.season = dp.season
         AND r.round  = dp.round
         AND r.driver_number = dp.driver_number
        LEFT JOIN team_points tp
          ON r.season = tp.season
         AND r.round  = tp.round
         AND r.team_name = tp.team_name
        LEFT JOIN features.race_top3_training ft
          ON r.season = ft.season
         AND r.round = ft.round
         AND r.grand_prix_slug = ft.grand_prix_slug
         AND r.driver_code = ft.driver_code
         AND r.team_name = ft.team_name
        WHERE r.finish_position IS NOT NULL; -- Note: grid_position can be NULL in gold
        """
    )
    try:
        con.execute(sql)
    except duckdb.Error as exc:
        print(f"Failed to build features.race_win_training: {exc}")
        for schema, table in [
            ("gold", "driver_session_summary"),
            ("gold", "driver_season_standings"),
            ("gold", "team_season_standings"),
        ]:
            print(f"Columns in {schema}.{table}: {_table_columns(con, schema, table)}")
        sys.exit(1)

    count = con.execute("SELECT COUNT(*) FROM features.race_win_training").fetchone()[0]
    print(f"features.race_win_training rows: {count}")
    if count > 0:
        sample_rows = con.execute(
            """
            SELECT season, round, grand_prix_slug,
                   driver_number, driver_name, driver_code,
                   team_name, grid_position, finish_position,
                   driver_points_pre, team_points_pre, target_win_race,
                   track_temp_c, rain_probability, starting_compound_index, starting_compound_raw
            FROM features.race_win_training
            ORDER BY season, round, grid_position NULLS LAST, driver_number
            LIMIT 5
            """
        ).fetchall()
        print("Sample rows (race_win_training):")
        for r in sample_rows:
            print(r)
    else:
        print("Sample rows (race_win_training): <none>")


def build_quali_top3_training(con: duckdb.DuckDBPyConnection):
    sql = dedent(
        f"""
        DROP TABLE IF EXISTS features.quali_top3_training;
        CREATE TABLE features.quali_top3_training AS
        WITH driver_points AS (
          SELECT
            season,
            round,
            driver_number,
            points_cumulative,
            LAG(points_cumulative, 1, 0.0) OVER (
              PARTITION BY season, driver_number
              ORDER BY round
            ) AS points_cumulative_pre
          FROM gold.driver_season_standings
          WHERE season >= 2020
        ),
        team_points AS (
          SELECT
            season,
            round,
            team_name,
            points_cumulative_team,
            LAG(points_cumulative_team, 1, 0.0) OVER (
              PARTITION BY season, team_name
              ORDER BY round
            ) AS team_points_cumulative_pre
          FROM gold.team_season_standings
          WHERE season >= 2020
        ),
        quali_base AS (
          SELECT
            dss.season,
            dss.round,
            dss.grand_prix_slug,
            dss.session_code,
            dss.meeting_key,
            dss.session_key,
            dss.driver_number,
            dss.driver_name,
            dss.driver_code,
            dss.team_name,
            dss.finish_position,
            dss.grid_position,
            dss.best_lap_duration,
            dss.median_lap_duration,
            dss.total_laps,
            dss.laps_with_time
          FROM gold.driver_session_summary dss
          WHERE dss.session_code = 'Q'
            AND dss.season >= 2020
        ),
        weather_agg AS (
          SELECT
            meeting_key,
            session_key,
            AVG(track_temperature) AS track_temp_c,
            AVG(rainfall) AS rain_probability,
            MAX(rainfall) AS max_rainfall_mm
          FROM read_parquet('{bronze_path("weather/**/*.parquet")}', hive_partitioning=1, union_by_name=true)
          WHERE session_code = 'Q'
            AND season >= 2020
          GROUP BY meeting_key, session_key
        ),
        driver_roll AS (
          SELECT
            season,
            round,
            driver_number,
            AVG(finish_position) OVER (
              PARTITION BY driver_number
              ORDER BY season, round
              ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
            ) AS driver_avg_quali_pos_last_5,
            COUNT(*) FILTER (WHERE finish_position IS NOT NULL) OVER (
              PARTITION BY driver_number
              ORDER BY season, round
              ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
            ) AS driver_quali_starts_last_5
          FROM quali_base
        ),
        team_roll AS (
          SELECT
            season,
            round,
            team_name,
            AVG(finish_position) OVER (
              PARTITION BY team_name
              ORDER BY season, round
              ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
            ) AS team_avg_quali_pos_last_5,
            COUNT(*) FILTER (WHERE finish_position IS NOT NULL) OVER (
              PARTITION BY team_name
              ORDER BY season, round
              ROWS BETWEEN 5 PRECEDING AND 1 PRECEDING
            ) AS team_quali_starts_last_5
          FROM quali_base
        ),
        venue_history AS (
          SELECT
            season,
            round,
            grand_prix_slug,
            driver_number,
            team_name,
            AVG(finish_position) OVER (
              PARTITION BY grand_prix_slug, driver_number
              ORDER BY season, round
              ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ) AS driver_quali_avg_at_venue,
            AVG(finish_position) OVER (
              PARTITION BY grand_prix_slug, team_name
              ORDER BY season, round
              ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ) AS team_quali_avg_at_venue
          FROM quali_base
        ),
        pace AS (
          SELECT
            season,
            round,
            grand_prix_slug,
            MIN(best_lap_duration) AS field_best_lap
          FROM quali_base
          GROUP BY season, round, grand_prix_slug
        )
        SELECT
          q.season,
          q.round,
          q.grand_prix_slug,
          q.driver_number,
          q.driver_name,
          q.driver_code,
          q.team_name,
          q.grid_position,
          q.best_lap_duration,
          q.median_lap_duration,
          q.total_laps,
          q.laps_with_time,
          dp.points_cumulative_pre      AS driver_points_pre,
          tp.team_points_cumulative_pre AS team_points_pre,
          dr.driver_avg_quali_pos_last_5,
          dr.driver_quali_starts_last_5,
          tr.team_avg_quali_pos_last_5,
          tr.team_quali_starts_last_5,
          vh.driver_quali_avg_at_venue,
          vh.team_quali_avg_at_venue,
          wa.track_temp_c,
          wa.rain_probability,
          wa.max_rainfall_mm,
          CASE WHEN wa.max_rainfall_mm >= 0.5 THEN 1 ELSE 0 END AS is_wet_quali,
          CASE
            WHEN p.field_best_lap IS NULL OR q.best_lap_duration IS NULL THEN NULL
            ELSE CAST(q.best_lap_duration AS DOUBLE) - CAST(p.field_best_lap AS DOUBLE)
          END AS best_lap_delta_vs_pole,
          CASE
            WHEN q.median_lap_duration IS NULL OR q.best_lap_duration IS NULL THEN NULL
            ELSE CAST(q.median_lap_duration AS DOUBLE) - CAST(q.best_lap_duration AS DOUBLE)
          END AS lap_time_variance,
          CASE WHEN q.finish_position IS NOT NULL AND q.finish_position <= 3
               THEN 1 ELSE 0 END AS target_quali_top3,
          CASE WHEN q.finish_position = 1 THEN 1 ELSE 0 END AS target_pole
        FROM quali_base q
        LEFT JOIN driver_points dp
          ON q.season = dp.season
         AND q.round  = dp.round
         AND q.driver_number = dp.driver_number
        LEFT JOIN team_points tp
          ON q.season = tp.season
         AND q.round  = tp.round
         AND q.team_name = tp.team_name
        LEFT JOIN driver_roll dr
          ON q.season = dr.season
         AND q.round = dr.round
         AND q.driver_number = dr.driver_number
        LEFT JOIN team_roll tr
          ON q.season = tr.season
         AND q.round = tr.round
         AND q.team_name = tr.team_name
        LEFT JOIN venue_history vh
          ON q.season = vh.season
         AND q.round = vh.round
         AND q.grand_prix_slug = vh.grand_prix_slug
         AND q.driver_number = vh.driver_number
         AND q.team_name = vh.team_name
        LEFT JOIN weather_agg wa
          ON q.meeting_key = wa.meeting_key
         AND q.session_key = wa.session_key
        LEFT JOIN pace p
          ON q.season = p.season
         AND q.round = p.round
         AND q.grand_prix_slug = p.grand_prix_slug
        WHERE q.finish_position IS NOT NULL;
        """
    )
    try:
        con.execute(sql)
    except duckdb.Error as exc:
        print(f"Failed to build features.quali_top3_training: {exc}")
        for schema, table in [
            ("gold", "driver_session_summary"),
            ("gold", "driver_season_standings"),
            ("gold", "team_season_standings"),
        ]:
            print(f"Columns in {schema}.{table}: {_table_columns(con, schema, table)}")
        sys.exit(1)

    count = con.execute("SELECT COUNT(*) FROM features.quali_top3_training").fetchone()[0]
    print(f"features.quali_top3_training rows: {count}")
    _print_sample(
        con,
        """
        SELECT season, round, grand_prix_slug,
               driver_number, driver_name, driver_code, team_name,
               driver_points_pre, team_points_pre,
               driver_avg_quali_pos_last_5, team_avg_quali_pos_last_5,
               driver_quali_avg_at_venue, team_quali_avg_at_venue,
               rain_probability, best_lap_delta_vs_pole,
               target_quali_top3, target_pole
        FROM features.quali_top3_training
        WHERE season > 2020
        ORDER BY season, round, driver_number
        LIMIT 5
        """,
        "Sample rows (quali_top3_training):",
    )


def build_race_top3_training(con: duckdb.DuckDBPyConnection):
    sql = dedent(
        f"""
        DROP TABLE IF EXISTS features.race_top3_training;
        CREATE TABLE features.race_top3_training AS
        WITH driver_points AS (
          SELECT
            season,
            round,
            driver_number,
            points_cumulative,
            LAG(points_cumulative, 1, 0.0) OVER (
              PARTITION BY season, driver_number
              ORDER BY round
            ) AS points_cumulative_pre
          FROM gold.driver_season_standings
          WHERE season >= 2020
        ),
        team_points AS (
          SELECT
            season,
            round,
            team_name,
            points_cumulative_team,
            LAG(points_cumulative_team, 1, 0.0) OVER (
              PARTITION BY season, team_name
              ORDER BY round
            ) AS team_points_cumulative_pre
          FROM gold.team_season_standings
          WHERE season >= 2020
        ),
        race_base AS (
          SELECT
            dss.season,
            dss.round,
            dss.grand_prix_slug,
            dss.session_code,
            dss.meeting_key,
            dss.session_key,
            dss.driver_number,
            dss.driver_name,
            dss.driver_code,
            dss.team_name,
            dss.grid_position,
            dss.finish_position
          FROM gold.driver_session_summary dss
          WHERE dss.session_code = 'R'
            AND dss.season >= 2020
            AND dss.finish_position IS NOT NULL
            AND dss.finish_position <= 99
        ),
        weather_agg AS (
          SELECT
            meeting_key,
            session_key,
            AVG(track_temperature) AS track_temp_c,
            AVG(rainfall) AS rain_probability
          FROM read_parquet('{bronze_path("weather/**/*.parquet")}', hive_partitioning=1, union_by_name=true)
          WHERE session_code = 'R'
            AND season >= 2020
          GROUP BY meeting_key, session_key
        ),
        starting_compounds AS (
          SELECT *
          FROM (
            SELECT
              season,
              round,
              grand_prix_slug,
              session_code,
              meeting_key,
              session_key,
              driver_number,
              compound AS starting_compound_raw,
              ROW_NUMBER() OVER (
                PARTITION BY meeting_key, session_key, driver_number
                ORDER BY lap_start ASC
              ) AS rn
            FROM read_parquet('{bronze_path("stints/**/*.parquet")}', hive_partitioning=1, union_by_name=true)
            WHERE session_code = 'R'
              AND season >= 2020
          ) s
          WHERE rn = 1
        )
        SELECT
          r.season,
          r.round,
          r.grand_prix_slug,
          r.driver_number,
          r.driver_name,
          r.driver_code,
          r.team_name,
          COALESCE(r.grid_position, 99) AS grid_position,
          r.finish_position,
          dp.points_cumulative_pre      AS driver_points_pre,
          tp.team_points_cumulative_pre AS team_points_pre,
          w.track_temp_c,
          w.rain_probability,
          sc.starting_compound_raw,
          CASE
            WHEN sc.starting_compound_raw ILIKE 'HARD' OR sc.starting_compound_raw = 'H' THEN 1
            WHEN sc.starting_compound_raw ILIKE 'MEDIUM' OR sc.starting_compound_raw = 'M' THEN 2
            WHEN sc.starting_compound_raw ILIKE 'SOFT' OR sc.starting_compound_raw = 'S' THEN 3
            WHEN sc.starting_compound_raw ILIKE 'INTERMEDIATE' THEN 4
            WHEN sc.starting_compound_raw ILIKE 'WET' THEN 5
            ELSE 0
          END AS starting_compound_index,
          CASE WHEN r.finish_position <= 3 THEN 1 ELSE 0 END AS target_race_top3
        FROM race_base r
        LEFT JOIN driver_points dp
          ON r.season = dp.season
         AND r.round  = dp.round
         AND r.driver_number = dp.driver_number
        LEFT JOIN team_points tp
          ON r.season = tp.season
         AND r.round  = tp.round
         AND r.team_name = tp.team_name
        LEFT JOIN weather_agg w
          ON r.meeting_key = w.meeting_key
         AND r.session_key = w.session_key
        LEFT JOIN starting_compounds sc
          ON r.meeting_key = sc.meeting_key
         AND r.session_key = sc.session_key
         AND r.driver_number = sc.driver_number;
        """
    )
    try:
        con.execute(sql)
    except duckdb.Error as exc:
        print(f"Failed to build features.race_top3_training: {exc}")
        for src in [
            ("gold", "driver_session_summary"),
            ("gold", "driver_season_standings"),
            ("gold", "team_season_standings"),
        ]:
            name = ".".join(src)
            print(f"Columns for {name}: {_table_columns(con, src[0], src[1])}")
        print("Weather/stints are read from parquet globs; columns not listed here.")
        sys.exit(1)

    count = con.execute("SELECT COUNT(*) FROM features.race_top3_training").fetchone()[0]
    print(f"features.race_top3_training rows: {count}")
    _print_sample(
        con,
        """
        SELECT season, round, grand_prix_slug,
               driver_number, driver_name, team_name,
               driver_points_pre, team_points_pre,
               grid_position, track_temp_c, rain_probability,
               starting_compound_raw, starting_compound_index,
               target_race_top3
        FROM features.race_top3_training
        ORDER BY season, round, grand_prix_slug, grid_position NULLS LAST, driver_number
        LIMIT 5
        """,
        "Sample rows (race_top3_training):",
    )


def main():
    parser = argparse.ArgumentParser(description="Build ML feature tables inside DuckDB warehouse.")
    parser.add_argument(
        "--warehouse",
        default=os.getenv("F1_WAREHOUSE", DEFAULT_WAREHOUSE),
        help="Path to DuckDB warehouse",
    )
    args = parser.parse_args()

    warehouse_path = args.warehouse
    print(f"Using warehouse: {warehouse_path}")
    con = duckdb.connect(warehouse_path)

    con.execute("CREATE SCHEMA IF NOT EXISTS features;")
    _require_gold_tables(con)

    build_race_top3_training(con)
    build_quali_top3_training(con)
    build_race_win_training(con)
    print("\nFeature tables built successfully.")


if __name__ == "__main__":
    main()
