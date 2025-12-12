import logging
from pathlib import Path

import duckdb
import pandas as pd

WAREHOUSE_PATH = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"
FASTF1_BRONZE_LAPS_ROOT = "/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/laps"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("build_fastf1_views")

    logger.info("Connecting to DuckDB warehouse at %s", WAREHOUSE_PATH)
    con = duckdb.connect(WAREHOUSE_PATH)

    con.execute("CREATE SCHEMA IF NOT EXISTS fastf1;")

    parquet_glob = f"{FASTF1_BRONZE_LAPS_ROOT}/**/*.parquet"
    logger.info("Building fastf1.laps from %s", parquet_glob)
    try:
        con.execute(
            f"""
            CREATE OR REPLACE TABLE fastf1.laps AS
            SELECT *
            FROM read_parquet('{parquet_glob}', hive_partitioning=1, union_by_name=true);
            """
        )
    except duckdb.Error as exc:
        logger.warning("Failed to create fastf1.laps from parquet files: %s", exc)
        return

    try:
        row_count = con.execute("SELECT COUNT(*) FROM fastf1.laps").fetchone()[0]
        logger.info("fastf1.laps row count: %s", row_count)

        preview_cols = [
            "season",
            "round",
            "grand_prix_slug",
            "session_code",
            "driver_number",
            "driver_code",
            "lap_number",
            "lap_duration",
            "compound",
            "is_accurate",
        ]
        preview_sql = "SELECT {} FROM fastf1.laps LIMIT 5".format(", ".join(preview_cols))
        preview_df: pd.DataFrame = con.execute(preview_sql).fetchdf()
        logger.info("fastf1.laps preview:\n%s", preview_df)
    except duckdb.Error as exc:
        logger.warning("Diagnostics failed: %s", exc)
        return


    # Build fastf1.session_result
    session_result_glob = "/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/session_result/**/*.parquet"
    logger.info("Building fastf1.session_result from %s", session_result_glob)
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS fastf1;")
        con.execute(
            f"""
            CREATE OR REPLACE TABLE fastf1.session_result AS
            SELECT *
            FROM read_parquet('{session_result_glob}', union_by_name=true);
            """
        )
        
        # Create a race calendar mapping for seasons with missing round data
        # This handles 2025 which doesn't have proper round numbers in fastf1
        con.execute(
            """
            CREATE OR REPLACE TABLE fastf1.race_calendar AS
            SELECT * FROM (
                VALUES
                (2025, 'australian-grand-prix', 1),
                (2025, 'chinese-grand-prix', 2),
                (2025, 'japanese-grand-prix', 3),
                (2025, 'bahrain-grand-prix', 4),
                (2025, 'saudi-arabian-grand-prix', 5),
                (2025, 'miami-grand-prix', 6),
                (2025, 'emilia-romagna-grand-prix', 7),
                (2025, 'monaco-grand-prix', 8),
                (2025, 'spanish-grand-prix', 9),
                (2025, 'canadian-grand-prix', 10),
                (2025, 'austrian-grand-prix', 11),
                (2025, 'british-grand-prix', 12),
                (2025, 'belgian-grand-prix', 13),
                (2025, 'hungarian-grand-prix', 14),
                (2025, 'dutch-grand-prix', 15),
                (2025, 'italian-grand-prix', 16),
                (2025, 'azerbaijan-grand-prix', 17),
                (2025, 'singapore-grand-prix', 18),
                (2025, 'united-states-grand-prix', 19),
                (2025, 'mexico-city-grand-prix', 20),
                (2025, 's-o-paulo-grand-prix', 21),
                (2025, 'las-vegas-grand-prix', 22),
                (2025, 'qatar-grand-prix', 23),
                (2025, 'abu-dhabi-grand-prix', 24)
            ) AS t(season, grand_prix_slug, calendar_round);
            """
        )
        
        con.execute(
            """
            CREATE OR REPLACE VIEW fastf1.session_result_enriched AS
            SELECT sr.*,
                   COALESCE(sr.round,
                     CASE 
                       WHEN sr.season = 2025 THEN COALESCE(rc.calendar_round, DENSE_RANK() OVER (PARTITION BY sr.season ORDER BY sr.grand_prix_slug))
                       ELSE DENSE_RANK() OVER (PARTITION BY sr.season ORDER BY sr.grand_prix_slug)
                     END
                   ) AS round_inferred
            FROM fastf1.session_result sr
            LEFT JOIN fastf1.race_calendar rc ON sr.season = rc.season AND sr.grand_prix_slug = rc.grand_prix_slug;
            """
        )
        sr_count = con.execute("SELECT COUNT(*) FROM fastf1.session_result").fetchone()[0]
        logger.info("fastf1.session_result row count: %s", sr_count)
        sr_preview = con.execute(
            "SELECT season, round, round_inferred, grand_prix_slug, session_code FROM fastf1.session_result_enriched LIMIT 5"
        ).fetchdf()
        logger.info("fastf1.session_result preview:\n%s", sr_preview)
    except duckdb.Error as exc:
        logger.warning("Failed to build fastf1.session_result from parquet: %s", exc)
        return

    # Build fastf1.race_results view
    logger.info("Building fastf1.race_results view from fastf1.session_result (session_code='R')")
    try:
        con.execute(
            """
            CREATE OR REPLACE VIEW fastf1.race_results AS
            SELECT
              season,
              round_inferred AS round,
              grand_prix_slug,
              session_code,
              driver_code,
              driver_number,
              team_name,
              grid_position,
              classified_position,
              finish_position,
              status,
              points
            FROM fastf1.session_result_enriched
            WHERE session_code = 'R';
            """
        )
        rr_count = con.execute("SELECT COUNT(*) FROM fastf1.race_results").fetchone()[0]
        logger.info("fastf1.race_results row count: %s", rr_count)
        rr_preview = con.execute(
            "SELECT * FROM fastf1.race_results LIMIT 5"
        ).fetchdf()
        logger.info("fastf1.race_results preview:\n%s", rr_preview)
    except duckdb.Error as exc:
        logger.warning("Failed to build fastf1.race_results view: %s", exc)
        return

    # Build fastf1.points_pre view
    logger.info("Building fastf1.points_pre view using cumulative points before each race")
    try:
        con.execute(
            """
            CREATE OR REPLACE VIEW fastf1.points_pre AS
            WITH base AS (
                SELECT
                    season,
                    round,
                    grand_prix_slug,
                    driver_code,
                    driver_number,
                    team_name,
                    grid_position,
                    classified_position,
                    finish_position,
                    status,
                    COALESCE(points, 0) AS points
                FROM fastf1.race_results
                WHERE session_code = 'R'
            )
            SELECT
                season,
                round,
                grand_prix_slug,
                driver_code,
                driver_number,
                team_name,
                grid_position,
                classified_position,
                finish_position,
                status,
                points,
                COALESCE(
                    SUM(points) OVER (
                        PARTITION BY season, driver_code
                        ORDER BY round
                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                    ),
                    0
                ) AS driver_points_pre,
                COALESCE(
                    SUM(points) OVER (
                        PARTITION BY season, team_name
                        ORDER BY round
                        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
                    ),
                    0
                ) AS team_points_pre
            FROM base;
            """
        )
        pp_count = con.execute("SELECT COUNT(*) FROM fastf1.points_pre").fetchone()[0]
        logger.info("fastf1.points_pre row count: %s", pp_count)
        pp_preview = con.execute(
            "SELECT season, round, grand_prix_slug, driver_code, driver_points_pre, team_points_pre FROM fastf1.points_pre LIMIT 5"
        ).fetchdf()
        logger.info("fastf1.points_pre preview:\n%s", pp_preview)
    except duckdb.Error as exc:
        logger.warning("Failed to build fastf1.points_pre view: %s", exc)

    # Build fastf1.ml_race_win view
    logger.info("Building fastf1.ml_race_win view from fastf1.race_results and fastf1.points_pre")
    try:
        con.execute(
            """
            CREATE OR REPLACE VIEW fastf1.ml_race_win AS
            WITH base AS (
                SELECT
                    r.season,
                    r.round,
                    r.grand_prix_slug,
                    r.session_code,
                    r.driver_code,
                    r.driver_number,
                    r.team_name,
                    r.grid_position,
                    r.classified_position,
                    r.finish_position,
                    r.status,
                    COALESCE(r.points, 0) AS points,
                    p.driver_points_pre,
                    p.team_points_pre
                FROM fastf1.race_results r
                LEFT JOIN fastf1.points_pre p
                  ON p.season = r.season
                 AND p.round = r.round
                 AND p.driver_code = r.driver_code
                WHERE r.session_code = 'R'
            )
            SELECT
                season,
                round,
                grand_prix_slug,
                session_code,
                driver_code,
                driver_number,
                team_name,
                grid_position,
                classified_position,
                finish_position,
                status,
                points,
                COALESCE(driver_points_pre, 0) AS driver_points_pre,
                COALESCE(team_points_pre, 0)    AS team_points_pre,
                CASE WHEN finish_position = 1 THEN 1 ELSE 0 END AS target_win_race
            FROM base;
            """
        )
        count_ml = con.execute("SELECT COUNT(*) FROM fastf1.ml_race_win").fetchone()[0]
        logger.info("fastf1.ml_race_win row count: %d", count_ml)
        preview_ml = con.execute(
            "SELECT * FROM fastf1.ml_race_win ORDER BY season, round, driver_code LIMIT 5"
        ).df()
        logger.info("fastf1.ml_race_win preview:\n%s", preview_ml)
    except duckdb.Error as exc:
        logger.warning("Failed to build fastf1.ml_race_win view: %s", exc)


if __name__ == "__main__":
    main()
