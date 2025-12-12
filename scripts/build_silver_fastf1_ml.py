#!/usr/bin/env python3
"""
Build silver_fastf1 ML dataset layer.

This script creates aggregated, cleaned, and enriched race data from bronze_fastf1.
Integrates weather data and creates historical driver/team performance features.
Covers seasons 2018-2025 with comprehensive feature engineering.
"""

import logging
from pathlib import Path

import duckdb

WAREHOUSE_PATH = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_silver_fastf1_ml")


def main() -> None:
    logger.info("Connecting to DuckDB warehouse at %s", WAREHOUSE_PATH)
    con = duckdb.connect(WAREHOUSE_PATH)

    # Ensure schema exists
    con.execute("CREATE SCHEMA IF NOT EXISTS silver_fastf1;")

    # 1. Create base race data with weather aggregates
    logger.info("Building silver_fastf1.race_data with weather integration...")
    con.execute("""
        CREATE OR REPLACE TABLE silver_fastf1.race_data AS
        WITH race_base AS (
            SELECT
                season,
                round,
                grand_prix_slug,
                driver_code,
                driver_number,
                driver_name,
                team_name,
                grid_position,
                finish_position,
                points,
                CASE WHEN finish_position IS NULL OR finish_position > 20 THEN 1 ELSE 0 END AS dnf,
                session_code,
                CAST(ingested_at AS DATE) as race_date
            FROM bronze_fastf1.session_result
            WHERE session_code = 'R'
                AND season BETWEEN 2018 AND 2025
                AND driver_code IS NOT NULL
                AND grid_position IS NOT NULL
        ),
        weather_agg AS (
            SELECT
                season,
                round,
                grand_prix_slug,
                'R' as session_code,
                COALESCE(AVG(CAST(AirTemp AS DOUBLE)), 0) AS avg_air_temp_c,
                COALESCE(AVG(CAST(TrackTemp AS DOUBLE)), 0) AS avg_track_temp_c,
                COALESCE(AVG(CAST(Humidity AS DOUBLE)), 0) AS avg_humidity_pct,
                COALESCE(AVG(CAST(WindSpeed AS DOUBLE)), 0) AS avg_wind_speed_kmh,
                COALESCE(MAX(CAST(Rainfall AS DOUBLE)), 0) AS max_rainfall_mm,
                COALESCE(AVG(CAST(Pressure AS DOUBLE)), 0) AS avg_pressure_mbar,
                CASE 
                    WHEN MAX(CAST(Rainfall AS DOUBLE)) > 0.5 THEN 1 
                    ELSE 0 
                END AS is_wet_race,
                CASE 
                    WHEN AVG(CAST(Humidity AS DOUBLE)) > 70 THEN 1 
                    ELSE 0 
                END AS is_high_humidity
            FROM bronze_fastf1.weather
            WHERE season BETWEEN 2018 AND 2025
                AND session_code = 'R'
            GROUP BY season, round, grand_prix_slug, session_code
        ),
        enriched AS (
            SELECT
                r.season,
                r.round,
                r.grand_prix_slug,
                r.driver_code,
                r.driver_number,
                r.driver_name,
                r.team_name,
                r.grid_position,
                r.finish_position,
                r.points,
                r.dnf,
                r.race_date,
                COALESCE(w.avg_air_temp_c, 0) AS avg_air_temp_c,
                COALESCE(w.avg_track_temp_c, 0) AS avg_track_temp_c,
                COALESCE(w.avg_humidity_pct, 0) AS avg_humidity_pct,
                COALESCE(w.avg_wind_speed_kmh, 0) AS avg_wind_speed_kmh,
                COALESCE(w.max_rainfall_mm, 0) AS max_rainfall_mm,
                COALESCE(w.avg_pressure_mbar, 0) AS avg_pressure_mbar,
                COALESCE(w.is_wet_race, 0) AS is_wet_race,
                COALESCE(w.is_high_humidity, 0) AS is_high_humidity,
                CASE WHEN r.finish_position = 1 THEN 1 ELSE 0 END AS target_win,
                CASE WHEN r.finish_position <= 3 THEN 1 ELSE 0 END AS target_podium,
                CASE WHEN r.dnf = 0 AND r.finish_position IS NOT NULL THEN 1 ELSE 0 END AS target_finish
            FROM race_base r
            LEFT JOIN weather_agg w 
                ON r.season = w.season 
                AND r.round = w.round 
                AND r.grand_prix_slug = w.grand_prix_slug
        )
        SELECT * FROM enriched;
    """)
    
    count = con.execute("SELECT COUNT(*) FROM silver_fastf1.race_data").fetchone()[0]
    logger.info("✓ silver_fastf1.race_data created with %d rows", count)

    # 2. Create driver career stats
    logger.info("Building silver_fastf1.driver_career_stats...")
    con.execute("""
        CREATE OR REPLACE TABLE silver_fastf1.driver_career_stats AS
        WITH driver_stats AS (
            SELECT
                driver_code,
                driver_name,
                MIN(season) AS career_start_season,
                MAX(season) AS career_end_season,
                COUNT(DISTINCT season) AS seasons_competed,
                COUNT(*) AS total_races,
                SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) AS career_wins,
                SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) AS career_podiums,
                SUM(CASE WHEN dnf = 0 AND finish_position IS NOT NULL THEN 1 ELSE 0 END) AS races_finished,
                SUM(points) AS career_points,
                AVG(CASE WHEN grid_position IS NOT NULL AND finish_position IS NOT NULL THEN 
                    CAST(grid_position AS DOUBLE) - CAST(finish_position AS DOUBLE) ELSE 0 END) AS avg_position_gain,
                AVG(CASE WHEN dnf = 0 AND finish_position IS NOT NULL THEN 
                    CAST(finish_position AS DOUBLE) ELSE NULL END) AS avg_finish_position,
                AVG(CASE WHEN dnf = 0 THEN 1.0 ELSE 0.0 END) AS finish_rate
            FROM silver_fastf1.race_data
            GROUP BY driver_code, driver_name
        )
        SELECT * FROM driver_stats;
    """)
    
    count = con.execute("SELECT COUNT(*) FROM silver_fastf1.driver_career_stats").fetchone()[0]
    logger.info("✓ silver_fastf1.driver_career_stats created with %d drivers", count)

    # 3. Create driver performance at specific venues
    logger.info("Building silver_fastf1.driver_venue_stats...")
    con.execute("""
        CREATE OR REPLACE TABLE silver_fastf1.driver_venue_stats AS
        WITH venue_stats AS (
            SELECT
                driver_code,
                driver_name,
                grand_prix_slug,
                COUNT(*) AS races_at_venue,
                SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) AS wins_at_venue,
                SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) AS podiums_at_venue,
                AVG(CASE WHEN dnf = 0 AND finish_position IS NOT NULL THEN 
                    CAST(finish_position AS DOUBLE) ELSE NULL END) AS avg_finish_at_venue,
                AVG(grid_position) AS avg_grid_at_venue,
                AVG(points) AS avg_points_at_venue,
                MAX(is_wet_race) AS ever_raced_wet_at_venue
            FROM silver_fastf1.race_data
            GROUP BY driver_code, driver_name, grand_prix_slug
        )
        SELECT * FROM venue_stats;
    """)
    
    count = con.execute("SELECT COUNT(*) FROM silver_fastf1.driver_venue_stats").fetchone()[0]
    logger.info("✓ silver_fastf1.driver_venue_stats created with %d records", count)

    # 4. Create driver weather-specific performance
    logger.info("Building silver_fastf1.driver_weather_stats...")
    con.execute("""
        CREATE OR REPLACE TABLE silver_fastf1.driver_weather_stats AS
        WITH weather_stats AS (
            SELECT
                driver_code,
                driver_name,
                CASE 
                    WHEN is_wet_race = 1 THEN 'wet'
                    WHEN is_high_humidity = 1 THEN 'humid'
                    ELSE 'dry'
                END AS weather_condition,
                COUNT(*) AS races_in_condition,
                SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) AS wins_in_condition,
                SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) AS podiums_in_condition,
                AVG(CASE WHEN dnf = 0 AND finish_position IS NOT NULL THEN 
                    CAST(finish_position AS DOUBLE) ELSE NULL END) AS avg_finish_in_condition,
                AVG(CASE WHEN dnf = 0 THEN 1.0 ELSE 0.0 END) AS finish_rate_in_condition
            FROM silver_fastf1.race_data
            GROUP BY driver_code, driver_name, 
                CASE 
                    WHEN is_wet_race = 1 THEN 'wet'
                    WHEN is_high_humidity = 1 THEN 'humid'
                    ELSE 'dry'
                END
        )
        SELECT * FROM weather_stats;
    """)
    
    count = con.execute("SELECT COUNT(*) FROM silver_fastf1.driver_weather_stats").fetchone()[0]
    logger.info("✓ silver_fastf1.driver_weather_stats created with %d records", count)

    # 5. Create team performance stats
    logger.info("Building silver_fastf1.team_stats...")
    con.execute("""
        CREATE OR REPLACE TABLE silver_fastf1.team_stats AS
        WITH team_stats AS (
            SELECT
                team_name,
                MIN(season) AS team_start_season,
                MAX(season) AS team_end_season,
                COUNT(*) AS total_races,
                SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) AS team_wins,
                SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) AS team_podiums,
                SUM(points) AS team_points,
                AVG(CASE WHEN dnf = 0 AND finish_position IS NOT NULL THEN 
                    CAST(finish_position AS DOUBLE) ELSE NULL END) AS avg_team_finish
            FROM silver_fastf1.race_data
            GROUP BY team_name
        )
        SELECT * FROM team_stats;
    """)
    
    count = con.execute("SELECT COUNT(*) FROM silver_fastf1.team_stats").fetchone()[0]
    logger.info("✓ silver_fastf1.team_stats created with %d teams", count)

    # 6. Create season form tables for rolling averages
    logger.info("Building silver_fastf1.driver_season_form...")
    con.execute("""
        CREATE OR REPLACE TABLE silver_fastf1.driver_season_form AS
        WITH form AS (
            SELECT
                season,
                driver_code,
                driver_name,
                round,
                ROW_NUMBER() OVER (PARTITION BY season, driver_code ORDER BY round) AS race_num_in_season,
                AVG(CASE WHEN finish_position IS NOT NULL AND dnf = 0 THEN 
                    CAST(finish_position AS DOUBLE) ELSE NULL END) OVER (
                    PARTITION BY season, driver_code 
                    ORDER BY round 
                    ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING
                ) AS avg_finish_last_5,
                SUM(points) OVER (
                    PARTITION BY season, driver_code 
                    ORDER BY round 
                    ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING
                ) AS points_last_5,
                AVG(grid_position) OVER (
                    PARTITION BY season, driver_code 
                    ORDER BY round 
                    ROWS BETWEEN 4 PRECEDING AND 1 PRECEDING
                ) AS avg_grid_last_5
            FROM silver_fastf1.race_data
        )
        SELECT * FROM form;
    """)
    
    count = con.execute("SELECT COUNT(*) FROM silver_fastf1.driver_season_form").fetchone()[0]
    logger.info("✓ silver_fastf1.driver_season_form created with %d records", count)

    # Show summary
    logger.info("\n=== Silver_FastF1 Summary ===")
    stats = con.execute("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT season) as seasons,
            COUNT(DISTINCT driver_code) as drivers,
            COUNT(DISTINCT team_name) as teams,
            COUNT(DISTINCT grand_prix_slug) as venues,
            SUM(CASE WHEN is_wet_race = 1 THEN 1 ELSE 0 END) as wet_races,
            SUM(CASE WHEN target_win = 1 THEN 1 ELSE 0 END) as total_wins
        FROM silver_fastf1.race_data
    """).fetchone()
    
    logger.info("Race Data: %d records, %d seasons, %d drivers, %d teams, %d venues",
                stats[0], stats[1], stats[2], stats[3], stats[4])
    logger.info("Weather: %d wet races", stats[5])
    logger.info("Outcomes: %d total wins", stats[6])

    con.close()
    logger.info("✓ silver_fastf1 ML layer complete")


if __name__ == "__main__":
    main()
