#!/usr/bin/env python3
"""
Batch export orchestrator for FastF1 data.
Exports weather, race control messages, and GPS position data in controlled batches
to avoid hitting FastF1 rate limits.
"""

import argparse
import subprocess
import logging
from pathlib import Path
from time import sleep

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("batch_export")

SCRIPTS_DIR = Path(__file__).parent
PYTHON_VENV = Path("/Volumes/SAMSUNG/apps/f1-dash/.venv/bin/python")


def run_export_script(script_name: str, **kwargs) -> bool:
    """Run an export script with arguments."""
    cmd = [str(PYTHON_VENV), str(SCRIPTS_DIR / script_name)]
    
    for key, value in kwargs.items():
        cmd.append(f"--{key.replace('_', '-')}")
        if value is not None and value is not True:
            cmd.append(str(value))
    
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"Export failed with code {e.returncode}")
        return False


def export_year_batch(year: int, data_types: list, delay_between_types: float = 30.0):
    """Export all data types for a single year."""
    logger.info(f"\n{'='*80}")
    logger.info(f"EXPORTING {year} DATA")
    logger.info(f"{'='*80}\n")
    
    results = {}
    
    if 'weather' in data_types:
        logger.info(f"\n>>> Exporting WEATHER data for {year}")
        results['weather'] = run_export_script(
            "export_weather_data.py",
            year=year,
            sessions="FP1,FP2,FP3,Q,R",
            delay=2.0
        )
        if delay_between_types > 0:
            logger.info(f"Waiting {delay_between_types}s before next data type...")
            sleep(delay_between_types)
    
    if 'race_control' in data_types:
        logger.info(f"\n>>> Exporting RACE CONTROL messages for {year}")
        results['race_control'] = run_export_script(
            "export_race_control.py",
            year=year,
            sessions="FP1,FP2,FP3,Q,R",
            delay=2.0
        )
        if delay_between_types > 0:
            logger.info(f"Waiting {delay_between_types}s before next data type...")
            sleep(delay_between_types)
    
    if 'position' in data_types:
        logger.info(f"\n>>> Exporting GPS POSITION data for {year} (RACE sessions only, sampled)")
        results['position'] = run_export_script(
            "export_position_data.py",
            year=year,
            sessions="R",
            sample_rate=10,
            delay=3.0
        )
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Batch export FastF1 data with rate limiting")
    parser.add_argument("--years", type=str, required=True, help="Comma-separated years (e.g., 2025,2024,2023)")
    parser.add_argument("--data-types", type=str, default="weather,race_control,position", 
                       help="Comma-separated data types to export")
    parser.add_argument("--delay-between-years", type=float, default=60.0, 
                       help="Delay between years (seconds)")
    parser.add_argument("--delay-between-types", type=float, default=30.0,
                       help="Delay between data types (seconds)")
    
    args = parser.parse_args()
    
    years = [int(y.strip()) for y in args.years.split(',')]
    data_types = [dt.strip() for dt in args.data_types.split(',')]
    
    logger.info(f"Batch export configuration:")
    logger.info(f"  Years: {years}")
    logger.info(f"  Data types: {data_types}")
    logger.info(f"  Delay between years: {args.delay_between_years}s")
    logger.info(f"  Delay between data types: {args.delay_between_types}s")
    
    total_results = {}
    
    for i, year in enumerate(years):
        year_results = export_year_batch(year, data_types, args.delay_between_types)
        total_results[year] = year_results
        
        # Delay between years (except after last year)
        if i < len(years) - 1 and args.delay_between_years > 0:
            logger.info(f"\n{'='*80}")
            logger.info(f"Waiting {args.delay_between_years}s before next year...")
            logger.info(f"{'='*80}\n")
            sleep(args.delay_between_years)
    
    # Summary
    logger.info(f"\n{'='*80}")
    logger.info("BATCH EXPORT SUMMARY")
    logger.info(f"{'='*80}")
    
    for year, results in total_results.items():
        logger.info(f"\n{year}:")
        for dtype, success in results.items():
            status = "✓" if success else "✗"
            logger.info(f"  {status} {dtype}")


if __name__ == "__main__":
    main()
