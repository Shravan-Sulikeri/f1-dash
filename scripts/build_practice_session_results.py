#!/usr/bin/env python3
"""
Build practice session results from laps data.
This extracts driver results from FP1, FP2, FP3 sessions and writes them to parquet files
in the bronze_fastf1/session_result directory structure.
"""

import logging
import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

LAPS_ROOT = "/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/laps"
SESSION_RESULT_ROOT = "/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/session_result"

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("build_practice_session_results")
    
    # Find all FP1, FP2, FP3 parquet files
    for root, dirs, files in os.walk(LAPS_ROOT):
        for file in files:
            if not file.endswith(".parquet"):
                continue
            
            filepath = os.path.join(root, file)
            
            # Extract season, grand_prix_slug, and session_code from path
            # Path format: .../season=YYYY/grand_prix_slug=.../session_code=.../part-*.parquet
            parts = filepath.split(os.sep)
            
            season_idx = next((i for i, p in enumerate(parts) if p.startswith("season=")), None)
            gp_idx = next((i for i, p in enumerate(parts) if p.startswith("grand_prix_slug=")), None)
            session_idx = next((i for i, p in enumerate(parts) if p.startswith("session_code=")), None)
            
            if not all([season_idx, gp_idx, session_idx]):
                continue
            
            season = int(parts[season_idx].split("=")[1])
            grand_prix_slug = parts[gp_idx].split("=", 1)[1]
            session_code = parts[session_idx].split("=")[1]
            
            # Only process practice sessions
            if session_code not in ["FP1", "FP2", "FP3"]:
                continue
            
            logger.info(f"Processing {season} {grand_prix_slug} {session_code}")
            
            try:
                # Read laps data
                df = pd.read_parquet(filepath)
                
                if df.empty:
                    logger.warning(f"  Empty dataframe for {season} {grand_prix_slug} {session_code}")
                    continue
                
                # Extract best lap time for each driver
                driver_results = []
                
                # Filter valid laps (not deleted, has lap_duration)
                valid_laps = df[
                    (df['lap_duration'].notna()) & 
                    (~df['deleted']) &
                    (df['lap_duration'] > 0)
                ].copy()
                
                if valid_laps.empty:
                    logger.warning(f"  No valid laps for {season} {grand_prix_slug} {session_code}")
                    continue
                
                # Get best lap for each driver
                best_laps = valid_laps.loc[valid_laps.groupby('driver_code')['lap_duration'].idxmin()]
                
                # Sort by lap duration to get positions
                best_laps = best_laps.sort_values('lap_duration').reset_index(drop=True)
                best_laps['finish_position'] = range(1, len(best_laps) + 1)
                
                # Calculate gap to leader
                if len(best_laps) > 0:
                    leader_time = best_laps.iloc[0]['lap_duration']
                    best_laps['gap_to_leader'] = (best_laps['lap_duration'] - leader_time).apply(
                        lambda x: f"+{x:.3f}" if x > 0 else None
                    )
                    # Format lap duration for display
                    best_laps['time_retired'] = best_laps['lap_duration'].apply(
                        lambda x: f"{int(x // 60)}:{x % 60:06.3f}" if pd.notna(x) else None
                    )
                else:
                    best_laps['gap_to_leader'] = None
                    best_laps['time_retired'] = None
                
                best_laps['status'] = 'Finished'
                
                results_df = best_laps.copy()
                
                # Keep only necessary columns for session_result
                # Based on the Q/R schema we've seen
                cols_to_keep = [
                    "season",
                    "round",
                    "grand_prix",
                    "grand_prix_slug",
                    "session_code",
                    "source",
                    "ingested_at",
                    "driver_number",
                    "driver_code",
                    "driver_name",
                    "team_name",
                    "finish_position",
                    "gap_to_leader",
                    "time_retired",
                    "status",
                ]
                
                # Filter to columns that exist
                existing_cols = [c for c in cols_to_keep if c in results_df.columns]
                results_df = results_df[existing_cols]
                
                # Create output directory if it doesn't exist
                output_dir = os.path.join(
                    SESSION_RESULT_ROOT,
                    f"season={season}",
                    f"grand_prix_slug={grand_prix_slug}",
                    f"session_code={session_code}"
                )
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                
                # Write to parquet
                output_file = os.path.join(output_dir, "part-00000.parquet")
                pq.write_table(pa.Table.from_pandas(results_df), output_file)
                logger.info(f"  Wrote {len(results_df)} drivers to {output_file}")
            
            except Exception as e:
                logger.error(f"  Error processing {season} {grand_prix_slug} {session_code}: {e}")
                continue
    
    logger.info("Done!")

if __name__ == "__main__":
    main()
