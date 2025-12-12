#!/usr/bin/env python3
"""
Build bronze_fastf1 ML dataset layer.

This script ingests race results and weather data from bronze_fastf1 for seasons 2018-2025.
Creates unified bronze layer with all raw race performance and environmental data.
"""

import logging
from pathlib import Path

import duckdb

WAREHOUSE_PATH = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"
BRONZE_FASTF1_ROOT = "/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_bronze_fastf1_ml")


def main() -> None:
    logger.info("Connecting to DuckDB warehouse at %s", WAREHOUSE_PATH)
    con = duckdb.connect(WAREHOUSE_PATH)

    # Ensure schema exists
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze_fastf1;")

    # Build bronze_fastf1.session_result from parquet files
    session_result_glob = f"{BRONZE_FASTF1_ROOT}/session_result/**/*.parquet"
    logger.info("Building bronze_fastf1.session_result from %s", session_result_glob)
    
    try:
        con.execute(
            f"""
            CREATE OR REPLACE TABLE bronze_fastf1.session_result AS
            SELECT *
            FROM read_parquet('{session_result_glob}', union_by_name=true)
            WHERE season >= 2018 AND season <= 2025;
            """
        )
        row_count = con.execute("SELECT COUNT(*) FROM bronze_fastf1.session_result").fetchone()[0]
        logger.info("✓ bronze_fastf1.session_result created with %d rows", row_count)
    except Exception as e:
        logger.error("✗ Failed to create bronze_fastf1.session_result: %s", e)
        return

    # Build bronze_fastf1.weather from parquet files
    weather_glob = f"{BRONZE_FASTF1_ROOT}/weather/**/*.parquet"
    logger.info("Building bronze_fastf1.weather from %s", weather_glob)
    
    try:
        con.execute(
            f"""
            CREATE OR REPLACE TABLE bronze_fastf1.weather AS
            SELECT *
            FROM read_parquet('{weather_glob}', union_by_name=true)
            WHERE season >= 2018 AND season <= 2025;
            """
        )
        row_count = con.execute("SELECT COUNT(*) FROM bronze_fastf1.weather").fetchone()[0]
        logger.info("✓ bronze_fastf1.weather created with %d rows", row_count)
    except Exception as e:
        logger.error("✗ Failed to create bronze_fastf1.weather: %s", e)
        return

    # Build bronze_fastf1.laps from parquet files
    laps_glob = f"{BRONZE_FASTF1_ROOT}/laps/**/*.parquet"
    logger.info("Building bronze_fastf1.laps from %s", laps_glob)
    
    try:
        con.execute(
            f"""
            CREATE OR REPLACE TABLE bronze_fastf1.laps AS
            SELECT *
            FROM read_parquet('{laps_glob}', union_by_name=true)
            WHERE season >= 2018 AND season <= 2025;
            """
        )
        row_count = con.execute("SELECT COUNT(*) FROM bronze_fastf1.laps").fetchone()[0]
        logger.info("✓ bronze_fastf1.laps created with %d rows", row_count)
    except Exception as e:
        logger.error("✗ Failed to create bronze_fastf1.laps: %s", e)
        return

    # Show summary statistics
    logger.info("\n=== Bronze_FastF1 Summary ===")
    
    stats = con.execute("""
        SELECT 
            COUNT(*) as total_races,
            MIN(season) as min_season,
            MAX(season) as max_season,
            COUNT(DISTINCT season) as distinct_seasons,
            COUNT(DISTINCT grand_prix_slug) as distinct_venues
        FROM bronze_fastf1.session_result
        WHERE session_code = 'R'
    """).fetchone()
    
    logger.info("Race Results: %d races from %d-%d (%d seasons, %d venues)",
                stats[0], stats[1], stats[2], stats[3], stats[4])
    
    try:
        weather_count = con.execute("SELECT COUNT(*) FROM bronze_fastf1.weather").fetchone()[0]
        weather_sessions = con.execute(
            "SELECT COUNT(DISTINCT (season, round, grand_prix_slug, session_code)) FROM bronze_fastf1.weather"
        ).fetchone()[0]
        logger.info("Weather Records: %d total records covering %d sessions", weather_count, weather_sessions)
    except:
        logger.warning("Weather data may not be available")

    try:
        laps_count = con.execute("SELECT COUNT(*) FROM bronze_fastf1.laps").fetchone()[0]
        logger.info("Lap Data: %d lap records available", laps_count)
    except:
        logger.warning("Lap data may not be available")

    con.close()
    logger.info("✓ bronze_fastf1 ML layer complete")


if __name__ == "__main__":
    main()
