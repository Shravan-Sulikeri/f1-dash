"""
Build DuckDB views for new telemetry data: weather, race control, position data.
"""

import logging
from pathlib import Path

import duckdb

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

WAREHOUSE_PATH = Path("/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb")


def main():
    con = duckdb.connect(str(WAREHOUSE_PATH))
    
    # ============================================================================
    # WEATHER DATA VIEW
    # ============================================================================
    logger.info("Building fastf1.weather view...")
    
    con.execute("""
        CREATE OR REPLACE VIEW fastf1.weather AS
        SELECT 
            season,
            round,
            grand_prix_slug,
            session_code,
            "Time",
            "AirTemp",
            "TrackTemp",
            "Humidity",
            "Pressure",
            "Rainfall",
            "WindSpeed",
            "WindDirection"
        FROM read_parquet('/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/weather/**/*.parquet')
        WHERE season >= 2020
        ORDER BY season, round, session_code, "Time"
    """)
    
    weather_count = con.execute("SELECT COUNT(*) as count FROM fastf1.weather").fetchdf()
    logger.info(f"fastf1.weather: {weather_count['count'].values[0]:,} records")
    
    # ============================================================================
    # RACE CONTROL MESSAGES VIEW
    # ============================================================================
    logger.info("Building fastf1.race_control_messages view...")
    
    con.execute("""
        CREATE OR REPLACE VIEW fastf1.race_control_messages AS
        SELECT 
            season,
            round,
            grand_prix_slug,
            session_code,
            "Time",
            "Category",
            "Message",
            "Flag",
            "Sector",
            "RacingNumber"
        FROM read_parquet('/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/race_control/**/*.parquet')
        WHERE season >= 2020
        ORDER BY season, round, session_code, "Time"
    """)
    
    rc_count = con.execute("SELECT COUNT(*) as count FROM fastf1.race_control_messages").fetchdf()
    logger.info(f"fastf1.race_control_messages: {rc_count['count'].values[0]:,} records")
    
    # ============================================================================
    # POSITION DATA VIEW
    # ============================================================================
    logger.info("Building fastf1.position_data view...")
    
    con.execute("""
        CREATE OR REPLACE VIEW fastf1.position_data AS
        SELECT 
            season,
            round,
            grand_prix_slug,
            session_code,
            driver_number,
            "Date",
            "Status",
            "X",
            "Y",
            "Z",
            "Time",
            "SessionTime"
        FROM read_parquet('/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/position/**/*.parquet')
        WHERE season >= 2020
        ORDER BY season, round, session_code, driver_number, "SessionTime"
    """)
    
    pos_count = con.execute("SELECT COUNT(*) as count FROM fastf1.position_data").fetchdf()
    logger.info(f"fastf1.position_data: {pos_count['count'].values[0]:,} records (sampled)")
    
    # ============================================================================
    # ENRICHED RACE DATA VIEW (for visualization)
    # ============================================================================
    logger.info("Building fastf1.race_visualization_data view...")
    
    con.execute("""
        CREATE OR REPLACE VIEW fastf1.race_visualization_data AS
        SELECT 
            sr.season,
            sr.round_inferred as round,
            sr.grand_prix_slug,
            sr."FullName" as driver_name,
            sr."DriverNumber" as driver_number,
            sr."TeamName" as team_name,
            sr."Position" as final_position,
            sr."GridPosition" as grid_position,
            sr."Points" as points,
            sr."Status" as finish_status,
            AVG(w."AirTemp") as avg_air_temp,
            AVG(w."TrackTemp") as avg_track_temp,
            AVG(w."Humidity") as avg_humidity,
            AVG(w."WindSpeed") as avg_wind_speed
        FROM fastf1.session_result_enriched sr
        LEFT JOIN fastf1.weather w 
            ON sr.season = w.season 
            AND sr.round_inferred = w.round 
            AND sr.grand_prix_slug = w.grand_prix_slug
            AND w.session_code = 'R'
        WHERE sr.session_code = 'R' AND sr.season >= 2020
        GROUP BY sr.season, sr.round_inferred, sr.grand_prix_slug, sr."FullName", 
                 sr."DriverNumber", sr."TeamName", sr."Position", sr."GridPosition", 
                 sr."Points", sr."Status"
        ORDER BY sr.season DESC, sr.round_inferred DESC, sr."Position"
    """)
    
    vis_count = con.execute("SELECT COUNT(*) as count FROM fastf1.race_visualization_data").fetchdf()
    logger.info(f"fastf1.race_visualization_data: {vis_count['count'].values[0]:,} records")
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    logger.info("\n" + "="*80)
    logger.info("All views created successfully!")
    logger.info("="*80)
    logger.info("\nAvailable views:")
    logger.info("  - fastf1.weather (temperature, humidity, wind data)")
    logger.info("  - fastf1.race_control_messages (flags, safety car, incidents)")
    logger.info("  - fastf1.position_data (GPS coordinates, sampled)")
    logger.info("  - fastf1.race_visualization_data (enriched race data with weather)")
    
    con.close()


if __name__ == "__main__":
    main()
