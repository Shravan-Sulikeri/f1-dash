#!/usr/bin/env python3
"""
Export GPS position data from FastF1 sessions to parquet files.
Position data is SAMPLED to reduce storage (700K rows/race × 20 drivers = 14M rows).
We sample every Nth position to get ~50K rows per race while preserving race shape.
"""

import argparse
import logging
from pathlib import Path
from time import sleep

import fastf1
import pandas as pd

CACHE_PATH = Path("/Volumes/SAMSUNG/apps/f1-dash/fastf1_cache")
POSITION_OUTPUT_ROOT = Path("/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/position")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("export_position")


def export_session_position_data(year: int, round_num: int, session_code: str, sample_rate: int = 10) -> bool:
    """
    Export GPS position data for a single session.
    
    Args:
        sample_rate: Keep every Nth position (10 = keep 10%, reduces from ~700K to ~70K per race)
    """
    try:
        fastf1.Cache.enable_cache(str(CACHE_PATH))
        
        logger.info(f"Loading {year} Round {round_num} {session_code} with position data...")
        session = fastf1.get_session(year, round_num, session_code)
        session.load(telemetry=False, weather=False, messages=False)
        
        if not session.pos_data or len(session.pos_data) == 0:
            logger.warning(f"No position data for {year} R{round_num} {session_code}")
            return False
        
        # Get event slug for partitioning
        event_name = session.event['EventName']
        slug = event_name.lower().replace(' ', '-')
        
        # Combine all driver position data
        all_positions = []
        
        for driver_num in session.pos_data.keys():
            driver_pos = session.pos_data[driver_num].copy()
            
            if len(driver_pos) == 0:
                continue
            
            # Sample every Nth row to reduce size
            driver_pos_sampled = driver_pos.iloc[::sample_rate].copy()
            
            # Add metadata
            driver_pos_sampled['season'] = year
            driver_pos_sampled['round'] = round_num
            driver_pos_sampled['grand_prix_slug'] = slug
            driver_pos_sampled['session_code'] = session_code
            driver_pos_sampled['driver_number'] = driver_num
            
            # Convert timedelta to seconds
            if 'Time' in driver_pos_sampled.columns:
                driver_pos_sampled['time_seconds'] = driver_pos_sampled['Time'].dt.total_seconds()
            if 'SessionTime' in driver_pos_sampled.columns:
                driver_pos_sampled['session_time_seconds'] = driver_pos_sampled['SessionTime'].dt.total_seconds()
            
            all_positions.append(driver_pos_sampled)
        
        if not all_positions:
            logger.warning(f"No valid position data after sampling for {year} R{round_num} {session_code}")
            return False
        
        # Combine all drivers
        combined_positions = pd.concat(all_positions, ignore_index=True)
        
        # Output path with partitioning
        output_dir = POSITION_OUTPUT_ROOT / f"season={year}" / f"grand_prix_slug={slug}" / f"session_code={session_code}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "part-00000.parquet"
        combined_positions.to_parquet(output_file, index=False)
        
        original_count = sum(len(session.pos_data[d]) for d in session.pos_data.keys())
        logger.info(f"  ✓ Exported {len(combined_positions):,} position records (sampled from {original_count:,}) to {output_file}")
        logger.info(f"    Reduction: {100 - (len(combined_positions)/original_count*100):.1f}%")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ Failed to export {year} R{round_num} {session_code}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Export GPS position data from FastF1 (sampled)")
    parser.add_argument("--year", type=int, required=True, help="Season year")
    parser.add_argument("--start-round", type=int, default=1, help="Starting round number")
    parser.add_argument("--end-round", type=int, help="Ending round number (inclusive)")
    parser.add_argument("--sessions", type=str, default="R", help="Comma-separated session codes (default: R only)")
    parser.add_argument("--sample-rate", type=int, default=10, help="Keep every Nth position (default: 10 = 10%)")
    parser.add_argument("--delay", type=float, default=3.0, help="Delay between requests (seconds)")
    
    args = parser.parse_args()
    
    sessions = args.sessions.split(',')
    
    # Get schedule to determine end round
    fastf1.Cache.enable_cache(str(CACHE_PATH))
    schedule = fastf1.get_event_schedule(args.year, include_testing=False)
    max_round = int(schedule['RoundNumber'].max())
    
    end_round = args.end_round if args.end_round else max_round
    
    logger.info(f"Exporting GPS position data for {args.year} rounds {args.start_round}-{end_round}")
    logger.info(f"Sessions: {sessions}")
    logger.info(f"Sample rate: 1 in {args.sample_rate} positions (~{100/args.sample_rate:.1f}% of data)")
    logger.info(f"Delay between requests: {args.delay}s")
    
    success_count = 0
    fail_count = 0
    
    for round_num in range(args.start_round, end_round + 1):
        for session_code in sessions:
            if export_session_position_data(args.year, round_num, session_code, args.sample_rate):
                success_count += 1
            else:
                fail_count += 1
            
            # Rate limiting - position data is heavier
            sleep(args.delay)
    
    logger.info(f"\nCompleted: {success_count} successful, {fail_count} failed")


if __name__ == "__main__":
    main()
