#!/usr/bin/env python3
"""
FastF1 Export Guide and Helper
Exports F1 data 2018-2024 from FastF1 cache to Bronze Parquet, handling:
- Sprint rounds (FP1, SQ, S, Q, R) vs standard (FP1, FP2, FP3, Q, R)
- Missing/incomplete sessions (logs to Missing Data FastF1.txt)
- Cache-first approach to avoid rate limits

Usage:
  # Export all seasons with automatic sprint handling
  python scripts/fastf1_bulk_export.py --years 2023,2024 --auto-format
  
  # Or individual season
  python scripts/fastf1_export_season.py --year 2024 --auto-format
"""
import logging
import sys
from pathlib import Path
from typing import List, Dict

# Setup
MISSING_LOG = Path(__file__).resolve().parent.parent / "Missing Data FastF1.txt"
logger = logging.getLogger("fastf1_export")

def check_cache_availability() -> Dict[int, int]:
    """Check how many cached sessions are available per year."""
    cache_dir = Path(__file__).resolve().parent.parent / "fastf1_cache"
    availability = {}
    
    if not cache_dir.exists():
        logger.warning(f"Cache directory not found: {cache_dir}")
        return availability
    
    for year_dir in sorted(cache_dir.glob("*")):
        if year_dir.is_dir() and year_dir.name.isdigit():
            year = int(year_dir.name)
            cache_count = len(list(year_dir.glob("*/*/*.pkl")))
            availability[year] = cache_count
            logger.info(f"Year {year}: {cache_count} cached sessions")
    
    return availability

def print_export_instructions():
    """Print user-friendly export instructions."""
    instructions = """
╔════════════════════════════════════════════════════════════════════════════╗
║                  F1 LAKEHOUSE - FastF1 EXPORT GUIDE                       ║
╚════════════════════════════════════════════════════════════════════════════╝

STEP 1: Check Available Cached Data
────────────────────────────────────
"""
    print(instructions)
    
    availability = check_cache_availability()
    if availability:
        for year, count in sorted(availability.items()):
            print(f"  ✓ {year}: {count} sessions cached")
    else:
        print("  ⚠ No cached data found. Run FastF1 fetches first.")
    
    instructions2 = """

STEP 2: Export Sessions with Automatic Sprint Handling
───────────────────────────────────────────────────────
For a single season:
  python scripts/fastf1_export_season.py --year 2024 --auto-format

For multiple seasons:
  python scripts/fastf1_bulk_export.py --years 2023,2024 --auto-format

For pre-season testing (optional):
  python scripts/fastf1_export_season.py --year 2024 --auto-format --include-testing

Key flags:
  --auto-format         : Auto-detect sprint vs standard formats per event
  --dry-run             : Preview what would export without writing files
  --include-testing     : Include pre-season testing sessions
  --sessions FP1,FP2,Q,R: Override default sessions

STEP 3: Verify Export Success
──────────────────────────────
Check: Missing Data FastF1.txt
  - Lists sessions that failed or had incomplete drivers (< 20)
  - Use this to identify gaps

Check: Bronze directory
  - bronze/sessions/season=YYYY/
  - bronze/session_result/season=YYYY/
  - bronze/drivers/season=YYYY/
  - bronze/weather/season=YYYY/
  - etc.

Example query to verify:
  duckdb warehouse/f1_openf1.duckdb 
    "SELECT season, COUNT(*) FROM read_parquet('bronze/sessions/season=*/round=*/grand_prix=*/session=*/part-*.parquet') GROUP BY season;"

STEP 4: Sprint Format Notes
────────────────────────────
The script AUTOMATICALLY detects sprint vs standard weekends:

SPRINT events (FP1, SQ, S, Q, R):
  - 2023: Miami, Shanghai, Baku, Austria, Brazil
  - 2024: Miami, Shanghai, Baku, Austria, Singapore, Brazil

STANDARD events (FP1, FP2, FP3, Q, R):
  - Most other rounds

Running with --auto-format handles this automatically!

STEP 5: Handling Missing Data
──────────────────────────────
If a session has < 20 drivers, it's skipped and logged:
  year=YYYY, event=EventName, session=CODE: only N drivers loaded

This is INTENTIONAL - incomplete sessions are not useful for analysis.

To check what's missing:
  cat Missing Data FastF1.txt | tail -20

STEP 6: Rebuild ML Models
──────────────────────────
After exporting new data:
  python scripts/train_models.py --output-preds

Then rebuild predictions table:
  python scripts/build_predictions_table.py

╔════════════════════════════════════════════════════════════════════════════╗
║  Questions? Check fastf1_export_season.py for full documentation         ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
    print(instructions2)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    print_export_instructions()

if __name__ == "__main__":
    main()
