import logging

import duckdb
import pandas as pd

WAREHOUSE_PATH = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("build_fastf1_metadata")

    logger.info("Connecting to DuckDB warehouse at %s", WAREHOUSE_PATH)
    con = duckdb.connect(WAREHOUSE_PATH)

    # Check for fastf1.laps existence
    exists = (
        con.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema='fastf1' AND table_name='laps' LIMIT 1"
        ).fetchone()
        is not None
    )
    if not exists:
        logger.warning("[warn] fastf1.laps not found; run scripts/build_fastf1_views.py first.")
        return

    try:
        con.execute(
            """
            CREATE OR REPLACE TABLE fastf1.sessions AS
            SELECT
              CAST(season AS INTEGER) AS season,
              CAST(grand_prix AS VARCHAR) AS grand_prix,
              CAST(grand_prix_slug AS VARCHAR) AS grand_prix_slug,
              CAST(session AS VARCHAR) AS session,
              CAST(session_code AS VARCHAR) AS session_code,
              COUNT(*) AS lap_count,
              MIN(TRY_CAST(date_start AS TIMESTAMP)) AS first_lap_start,
              MAX(TRY_CAST(date_start AS TIMESTAMP)) AS last_lap_start
            FROM fastf1.laps
            GROUP BY season, grand_prix, grand_prix_slug, session, session_code;
            """
        )
    except duckdb.Error as exc:  # pragma: no cover - runtime safety
        logger.error("Failed to create fastf1.sessions: %s", exc)
        return

    try:
        row_count = con.execute("SELECT COUNT(*) FROM fastf1.sessions").fetchone()[0]
        logger.info("fastf1.sessions row count: %s", row_count)

        preview_df: pd.DataFrame = con.execute(
            """
            SELECT *
            FROM fastf1.sessions
            ORDER BY season, grand_prix_slug, session_code
            LIMIT 10
            """
        ).fetchdf()
        if preview_df.empty:
            logger.warning("fastf1.sessions is empty.")
        else:
            logger.info("fastf1.sessions preview:\n%s", preview_df)
    except duckdb.Error as exc:
        logger.error("Diagnostics failed: %s", exc)
        return


if __name__ == "__main__":
    main()
