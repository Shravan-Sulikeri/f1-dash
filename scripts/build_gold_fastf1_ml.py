#!/usr/bin/env python3
"""
Build gold_fastf1 ML training dataset layer.

This script creates the final feature-engineered training dataset by combining:
- Driver historical performance at each venue
- Weather-specific performance patterns
- Current season form (rolling averages)
- Team capability indicators
- Venue characteristics

Outputs gold_fastf1.race_prediction_features for ML training (2018-2025).
"""

import logging
from pathlib import Path

import duckdb

WAREHOUSE_PATH = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_gold_fastf1_ml")


def main() -> None:
    logger.info("Connecting to DuckDB warehouse at %s", WAREHOUSE_PATH)
    con = duckdb.connect(WAREHOUSE_PATH)

    # Ensure schema exists
    con.execute("CREATE SCHEMA IF NOT EXISTS gold_fastf1;")

    # Build comprehensive training features
    logger.info("Building gold_fastf1.race_prediction_features...")
    con.execute("""
        CREATE OR REPLACE TABLE gold_fastf1.race_prediction_features AS
        WITH base_race AS (
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
                dnf,
                race_date,
                avg_air_temp_c,
                avg_track_temp_c,
                avg_humidity_pct,
                avg_wind_speed_kmh,
                max_rainfall_mm,
                avg_pressure_mbar,
                is_wet_race,
                is_high_humidity,
                target_win,
                target_podium,
                target_finish
            FROM silver_fastf1.race_data
        ),
        with_career_stats AS (
            SELECT
                b.*,
                COALESCE(cs.career_wins, 0) AS driver_career_wins,
                COALESCE(cs.career_podiums, 0) AS driver_career_podiums,
                COALESCE(cs.total_races, 0) AS driver_career_races,
                COALESCE(cs.avg_finish_position, 999) AS driver_avg_finish_position,
                COALESCE(cs.finish_rate, 0) AS driver_finish_rate,
                COALESCE(cs.avg_position_gain, 0) AS driver_avg_position_gain
            FROM base_race b
            LEFT JOIN silver_fastf1.driver_career_stats cs
                ON b.driver_code = cs.driver_code
        ),
        with_venue_stats AS (
            SELECT
                w.*,
                COALESCE(vs.races_at_venue, 0) AS driver_races_at_venue,
                COALESCE(vs.wins_at_venue, 0) AS driver_wins_at_venue,
                COALESCE(vs.podiums_at_venue, 0) AS driver_podiums_at_venue,
                COALESCE(vs.avg_finish_at_venue, 999) AS driver_avg_finish_at_venue,
                COALESCE(vs.avg_grid_at_venue, 999) AS driver_avg_grid_at_venue,
                COALESCE(vs.avg_points_at_venue, 0) AS driver_avg_points_at_venue,
                COALESCE(vs.ever_raced_wet_at_venue, 0) AS driver_ever_wet_at_venue
            FROM with_career_stats w
            LEFT JOIN silver_fastf1.driver_venue_stats vs
                ON w.driver_code = vs.driver_code 
                AND w.grand_prix_slug = vs.grand_prix_slug
        ),
        with_season_form AS (
            SELECT
                w.*,
                COALESCE(f.avg_finish_last_5, 999) AS driver_avg_finish_last_5,
                COALESCE(f.points_last_5, 0) AS driver_points_last_5,
                COALESCE(f.avg_grid_last_5, 999) AS driver_avg_grid_last_5
            FROM with_venue_stats w
            LEFT JOIN silver_fastf1.driver_season_form f
                ON w.season = f.season 
                AND w.driver_code = f.driver_code 
                AND w.round = f.round
        ),
        with_team_stats AS (
            SELECT
                w.*,
                COALESCE(ts.team_wins, 0) AS team_wins_history,
                COALESCE(ts.team_podiums, 0) AS team_podiums_history,
                COALESCE(ts.team_points, 0) AS team_points_history,
                COALESCE(ts.avg_team_finish, 999) AS team_avg_finish
            FROM with_season_form w
            LEFT JOIN silver_fastf1.team_stats ts
                ON w.team_name = ts.team_name
        ),
        with_weather_performance AS (
            SELECT
                w.*,
                COALESCE(dry.races_in_condition, 0) AS driver_dry_races,
                COALESCE(dry.wins_in_condition, 0) AS driver_dry_wins,
                COALESCE(dry.avg_finish_in_condition, 999) AS driver_avg_finish_dry,
                COALESCE(wet.races_in_condition, 0) AS driver_wet_races,
                COALESCE(wet.wins_in_condition, 0) AS driver_wet_wins,
                COALESCE(wet.avg_finish_in_condition, 999) AS driver_avg_finish_wet,
                COALESCE(humid.races_in_condition, 0) AS driver_humid_races,
                COALESCE(humid.avg_finish_in_condition, 999) AS driver_avg_finish_humid
            FROM with_team_stats w
            LEFT JOIN silver_fastf1.driver_weather_stats dry
                ON w.driver_code = dry.driver_code AND dry.weather_condition = 'dry'
            LEFT JOIN silver_fastf1.driver_weather_stats wet
                ON w.driver_code = wet.driver_code AND wet.weather_condition = 'wet'
            LEFT JOIN silver_fastf1.driver_weather_stats humid
                ON w.driver_code = humid.driver_code AND humid.weather_condition = 'humid'
        ),
        final_features AS (
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
                dnf,
                race_date,
                
                -- Weather features
                avg_air_temp_c,
                avg_track_temp_c,
                avg_humidity_pct,
                avg_wind_speed_kmh,
                max_rainfall_mm,
                avg_pressure_mbar,
                is_wet_race,
                is_high_humidity,
                
                -- Career statistics
                driver_career_wins,
                driver_career_podiums,
                driver_career_races,
                driver_avg_finish_position,
                driver_finish_rate,
                driver_avg_position_gain,
                
                -- Venue-specific performance
                driver_races_at_venue,
                driver_wins_at_venue,
                driver_podiums_at_venue,
                driver_avg_finish_at_venue,
                driver_avg_grid_at_venue,
                driver_avg_points_at_venue,
                driver_ever_wet_at_venue,
                
                -- Current season form
                driver_avg_finish_last_5,
                driver_points_last_5,
                driver_avg_grid_last_5,
                
                -- Team performance
                team_wins_history,
                team_podiums_history,
                team_points_history,
                team_avg_finish,
                
                -- Weather-condition specific performance
                driver_dry_races,
                driver_dry_wins,
                driver_avg_finish_dry,
                driver_wet_races,
                driver_wet_wins,
                driver_avg_finish_wet,
                driver_humid_races,
                driver_avg_finish_humid,
                
                -- Targets
                target_win,
                target_podium,
                target_finish,
                
                -- Feature engineering: computed indicators
                CASE 
                    WHEN driver_races_at_venue > 0 THEN driver_wins_at_venue / CAST(driver_races_at_venue AS DOUBLE)
                    ELSE 0
                END AS driver_win_pct_at_venue,
                
                CASE 
                    WHEN driver_races_at_venue > 0 THEN driver_podiums_at_venue / CAST(driver_races_at_venue AS DOUBLE)
                    ELSE 0
                END AS driver_podium_pct_at_venue,
                
                CASE 
                    WHEN driver_career_races > 0 THEN driver_career_wins / CAST(driver_career_races AS DOUBLE)
                    ELSE 0
                END AS driver_career_win_pct,
                
                CASE 
                    WHEN driver_career_races > 0 THEN driver_career_podiums / CAST(driver_career_races AS DOUBLE)
                    ELSE 0
                END AS driver_career_podium_pct,
                
                CASE 
                    WHEN driver_wet_races > 0 THEN driver_wet_wins / CAST(driver_wet_races AS DOUBLE)
                    ELSE 0
                END AS driver_wet_win_pct,
                
                CASE 
                    WHEN driver_dry_races > 0 THEN driver_dry_wins / CAST(driver_dry_races AS DOUBLE)
                    ELSE 0
                END AS driver_dry_win_pct,
                
                ABS(grid_position - COALESCE(driver_avg_grid_at_venue, grid_position)) AS grid_deviation_from_venue_avg,
                
                (avg_track_temp_c - 20) / 10.0 AS normalized_track_temp,
                avg_humidity_pct / 100.0 AS normalized_humidity,
                avg_wind_speed_kmh / 20.0 AS normalized_wind_speed
            FROM with_weather_performance
            WHERE season BETWEEN 2018 AND 2025
        )
        SELECT * FROM final_features;
    """)
    
    count = con.execute("SELECT COUNT(*) FROM gold_fastf1.race_prediction_features").fetchone()[0]
    logger.info("✓ gold_fastf1.race_prediction_features created with %d rows", count)

    # Create alternative tables for different prediction tasks
    logger.info("Building gold_fastf1.win_prediction_dataset...")
    con.execute("""
        CREATE OR REPLACE TABLE gold_fastf1.win_prediction_dataset AS
        SELECT * FROM gold_fastf1.race_prediction_features
        WHERE target_finish = 1;
    """)
    
    count = con.execute("SELECT COUNT(*) FROM gold_fastf1.win_prediction_dataset").fetchone()[0]
    logger.info("✓ gold_fastf1.win_prediction_dataset created with %d rows", count)

    logger.info("Building gold_fastf1.podium_prediction_dataset...")
    con.execute("""
        CREATE OR REPLACE TABLE gold_fastf1.podium_prediction_dataset AS
        SELECT * FROM gold_fastf1.race_prediction_features
        WHERE target_finish = 1;
    """)
    
    count = con.execute("SELECT COUNT(*) FROM gold_fastf1.podium_prediction_dataset").fetchone()[0]
    logger.info("✓ gold_fastf1.podium_prediction_dataset created with %d rows", count)

    # Summary statistics
    logger.info("\n=== Gold_FastF1 Summary ===")
    
    summary = con.execute("""
        SELECT 
            COUNT(*) as total_features,
            COUNT(DISTINCT season) as seasons,
            COUNT(DISTINCT driver_code) as drivers,
            COUNT(DISTINCT team_name) as teams,
            COUNT(DISTINCT grand_prix_slug) as venues,
            SUM(target_win) as total_wins,
            SUM(target_podium) as total_podiums,
            ROUND(SUM(target_win) / CAST(COUNT(*) AS DOUBLE) * 100, 2) as win_rate_pct,
            ROUND(SUM(target_podium) / CAST(COUNT(*) AS DOUBLE) * 100, 2) as podium_rate_pct
        FROM gold_fastf1.race_prediction_features
    """).fetchone()
    
    logger.info("Total Features: %d records", summary[0])
    logger.info("Coverage: %d seasons, %d drivers, %d teams, %d venues", 
                summary[1], summary[2], summary[3], summary[4])
    logger.info("Targets: %d wins (%.2f%%), %d podiums (%.2f%%)",
                summary[5], summary[7], summary[6], summary[8])

    # Show feature columns
    feature_cols = con.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'gold_fastf1' 
            AND table_name = 'race_prediction_features'
        ORDER BY ordinal_position
    """).fetchdf()
    
    logger.info("\nFeature Columns (%d total):", len(feature_cols))
    for i, col in enumerate(feature_cols['column_name'].tolist(), 1):
        logger.info("  %d. %s", i, col)

    con.close()
    logger.info("✓ gold_fastf1 ML layer complete")


if __name__ == "__main__":
    main()
