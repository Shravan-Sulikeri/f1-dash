import argparse
import logging
import sys
from pathlib import Path
from typing import List

import fastf1

# Ensure local scripts package is importable when running directly
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.fastf1_export_to_parquet import export_fastf1_session_to_parquet


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk export FastF1 sessions to Parquet.")
    parser.add_argument("--year", type=int, required=True, help="Season year, e.g. 2023")
    parser.add_argument(
        "--session-types",
        nargs="+",
        default=["R", "Q", "FP1", "FP2", "FP3"],
        help="Session types to export (space-separated), e.g. R Q FP1 FP2 FP3",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=None,
        help="If provided, process only the first N events in the schedule.",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default="/Volumes/SAMSUNG/apps/f1-dash/fastf1_cache",
        help="FastF1 cache directory.",
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default="/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1",
        help="Output root for partitioned Parquet.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("fastf1_bulk_export")

    year = args.year
    session_types: List[str] = args.session_types
    max_events = args.max_events

    logger.info(
        "[plan] bulk export FastF1 laps for year=%s, session_types=%s, max_events=%s",
        year,
        session_types,
        max_events,
    )

    fastf1.Cache.enable_cache(args.cache_dir)
    logger.info("FastF1 cache enabled at %s", args.cache_dir)

    try:
        schedule = fastf1.get_event_schedule(year)
    except Exception as exc:  # pragma: no cover - runtime safety
        logger.error("Failed to fetch event schedule for year %s: %s", year, exc)
        return

    total_attempted = 0
    total_success = 0
    total_rows = 0

    events_processed = 0
    for _, row in schedule.sort_values("RoundNumber").iterrows():
        if max_events is not None and events_processed >= max_events:
            break
        event_name = row.get("EventName")
        round_number = row.get("RoundNumber")
        if not event_name:
            logger.warning("[skip] Missing EventName for row=%s", row.to_dict())
            continue
        logger.info("[event] year=%s round=%s event='%s'", year, round_number, event_name)
        events_processed += 1

        for stype in session_types:
            total_attempted += 1
            logger.info("[session] exporting session_type='%s' for event='%s'", stype, event_name)
            try:
                rows_written = export_fastf1_session_to_parquet(
                    year=year,
                    event_name=event_name,
                    session_type=stype,
                    cache_dir=args.cache_dir,
                    output_root=args.output_root,
                    logger=logger,
                )
                total_rows += rows_written
                total_success += 1
                logger.info("[session] wrote %s rows for %s %s %s", rows_written, year, event_name, stype)
            except Exception as exc:  # pragma: no cover - runtime safety
                logger.warning("[skip] Failed export for year=%s event='%s' session_type='%s': %s", year, event_name, stype, exc)
                continue

    logger.info(
        "[summary] sessions_attempted=%s sessions_successful=%s total_rows_exported=%s",
        total_attempted,
        total_success,
        total_rows,
    )


if __name__ == "__main__":
    main()
