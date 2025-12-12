#!/usr/bin/env python3
"""
Export race control messages from FastF1 sessions to parquet files.
Includes flags, safety car, DRS zones, penalties, and other race control events.
"""

import argparse
import logging
from pathlib import Path
from time import sleep

import fastf1
import pandas as pd

CACHE_PATH = Path("/Volumes/SAMSUNG/apps/f1-dash/fastf1_cache")
RACE_CONTROL_OUTPUT_ROOT = Path("/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/race_control")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("export_race_control")


def export_session_race_control(year: int, round_num: int, session_code: str) -> bool:
    """Export race control messages for a single session."""
    try:
        fastf1.Cache.enable_cache(str(CACHE_PATH))
        
        logger.info(f"Loading {year} Round {round_num} {session_code}...")
        session = fastf1.get_session(year, round_num, session_code)
        session.load(telemetry=False, weather=False)
        
        if session.race_control_messages is None or len(session.race_control_messages) == 0:
            logger.warning(f"No race control messages for {year} R{round_num} {session_code}")
            return False
        
        # Get event slug for partitioning
        event_name = session.event['EventName']
        slug = event_name.lower().replace(' ', '-')
        
        # Add metadata columns
        messages = session.race_control_messages.copy()
        messages['season'] = year
        messages['round'] = round_num
        messages['grand_prix_slug'] = slug
        messages['session_code'] = session_code
        
        # Convert datetime to string for parquet compatibility
        if 'Time' in messages.columns:
            messages['time_str'] = messages['Time'].astype(str)
        
        # Output path with partitioning
        output_dir = RACE_CONTROL_OUTPUT_ROOT / f"season={year}" / f"grand_prix_slug={slug}" / f"session_code={session_code}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "part-00000.parquet"
        messages.to_parquet(output_file, index=False)
        
        logger.info(f"  ✓ Exported {len(messages)} race control messages to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Failed to export {year} R{round_num} {session_code}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Export race control messages from FastF1")
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
    
    logger.info(f"Exporting race control messages for {args.year} rounds {args.start_round}-{end_round}")
    logger.info(f"Sessions: {sessions}")
    logger.info(f"Delay between requests: {args.delay}s")
    
    success_count = 0
    fail_count = 0
    
    for round_num in range(args.start_round, end_round + 1):
        for session_code in sessions:
            if export_session_race_control(args.year, round_num, session_code):
                success_count += 1
            else:
                fail_count += 1
            
            # Rate limiting
            sleep(args.delay)
    
    logger.info(f"\nCompleted: {success_count} successful, {fail_count} failed")


if __name__ == "__main__":
    main()
