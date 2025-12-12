#!/usr/bin/env python3
"""
Export weather data from FastF1 sessions to parquet files.
Weather includes: air temp, track temp, humidity, wind speed/direction, pressure, rainfall.
"""

import argparse
import logging
import sys
from pathlib import Path
from time import sleep

import fastf1
import pandas as pd

CACHE_PATH = Path("/Volumes/SAMSUNG/apps/f1-dash/fastf1_cache")
WEATHER_OUTPUT_ROOT = Path("/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/weather")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("export_weather")


def export_session_weather(year: int, round_num: int, session_code: str) -> bool:
    """Export weather data for a single session."""
    try:
        fastf1.Cache.enable_cache(str(CACHE_PATH))
        
        logger.info(f"Loading {year} Round {round_num} {session_code}...")
        session = fastf1.get_session(year, round_num, session_code)
        session.load(telemetry=False, weather=True)
        
        if session.weather_data is None or len(session.weather_data) == 0:
            logger.warning(f"No weather data for {year} R{round_num} {session_code}")
            return False
        
        # Get event slug for partitioning
        event_name = session.event['EventName']
        slug = event_name.lower().replace(' ', '-')
        
        # Add metadata columns
        weather = session.weather_data.copy()
        weather['season'] = year
        weather['round'] = round_num
        weather['grand_prix_slug'] = slug
        weather['session_code'] = session_code
        
        # Convert timedelta to seconds for easier querying
        if 'Time' in weather.columns:
            weather['time_seconds'] = weather['Time'].dt.total_seconds()
        
        # Output path with partitioning
        output_dir = WEATHER_OUTPUT_ROOT / f"season={year}" / f"grand_prix_slug={slug}" / f"session_code={session_code}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "part-00000.parquet"
        weather.to_parquet(output_file, index=False)
        
        logger.info(f"  ✓ Exported {len(weather)} weather records to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Failed to export {year} R{round_num} {session_code}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Export weather data from FastF1")
    parser.add_argument("--year", type=int, required=True, help="Season year")
    parser.add_argument("--start-round", type=int, default=1, help="Starting round number")
    parser.add_argument("--end-round", type=int, help="Ending round number (inclusive)")
    parser.add_argument("--sessions", type=str, default="FP1,FP2,FP3,Q,R", help="Comma-separated session codes")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between requests (seconds)")
    
    args = parser.parse_args()
    
    sessions = args.sessions.split(',')
    
    # Get schedule to determine end round
    fastf1.Cache.enable_cache(str(CACHE_PATH))
    schedule = fastf1.get_event_schedule(args.year, include_testing=False)
    max_round = int(schedule['RoundNumber'].max())
    
    end_round = args.end_round if args.end_round else max_round
    
    logger.info(f"Exporting weather data for {args.year} rounds {args.start_round}-{end_round}")
    logger.info(f"Sessions: {sessions}")
    logger.info(f"Delay between requests: {args.delay}s")
    
    success_count = 0
    fail_count = 0
    
    for round_num in range(args.start_round, end_round + 1):
        for session_code in sessions:
            if export_session_weather(args.year, round_num, session_code):
                success_count += 1
            else:
                fail_count += 1
            
            # Rate limiting
            sleep(args.delay)
    
    logger.info(f"\nCompleted: {success_count} successful, {fail_count} failed")


if __name__ == "__main__":
    main()
