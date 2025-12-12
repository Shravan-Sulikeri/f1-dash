import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import fastf1
import pandas as pd

# If running as a script, ensure we can import the session exporter
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.fastf1_export_to_parquet import (
    DEFAULT_OUTPUT_ROOT,
    export_fastf1_session_to_parquet,
    enable_fastf1_cache,
    log_missing,
)

SESSION_NAME_MAP = {
    "FP1": "Practice 1",
    "FP2": "Practice 2",
    "FP3": "Practice 3",
    "Q": "Qualifying",
    "SQ": "Sprint Qualifying",
    "S": "Sprint",
    "R": "Race",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a full season of FastF1 sessions to Parquet.")
    parser.add_argument("--year", type=int, required=True, help="Season year, e.g. 2018")
    parser.add_argument(
        "--sessions",
        type=str,
        default="FP1,FP2,FP3,Q,R",
        help="Comma-separated session codes, e.g. FP1,FP2,FP3,Q,R",
    )
    parser.add_argument(
        "--auto-format",
        action="store_true",
        help="If set, derive sessions per event using EventFormat (sprint vs. standard).",
    )
    parser.add_argument(
        "--include-testing",
        action="store_true",
        help="Include pre-season testing sessions if present in the schedule.",
    )
    parser.add_argument(
        "--out-root",
        type=str,
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Output root for partitioned Parquet",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If set, do not write any Parquet; just log what would happen.",
    )
    return parser.parse_args()


def confirm_long_run(session_count: int) -> bool:
    if session_count <= 25:
        return True
    print(f"About to download data for {session_count} sessions. This could take a while. Continue? [y/N]")
    ans = sys.stdin.readline().strip().lower()
    return ans == "y"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("fastf1_export_season")

    args = parse_args()
    year = args.year
    session_codes: List[str] = [s.strip() for s in args.sessions.split(",") if s.strip()]
    out_root = Path(args.out_root)
    dry_run = args.dry_run
    auto_format = args.auto_format
    include_testing = args.include_testing

    logger.info(
        "[plan] year=%s sessions=%s out_root=%s dry_run=%s auto_format=%s include_testing=%s",
        year,
        session_codes,
        out_root,
        dry_run,
        auto_format,
        include_testing,
    )

    if year < 2018:
        logger.warning("[warn] FastF1 data coverage before 2018 may be incomplete.")

    # Validate session codes
    for code in session_codes:
        if code not in SESSION_NAME_MAP:
            logger.error("Unknown session code '%s'. Valid codes: %s", code, list(SESSION_NAME_MAP.keys()))
            sys.exit(1)

    # Enable cache via shared helper
    enable_fastf1_cache()

    try:
        schedule = fastf1.get_event_schedule(year=year, include_testing=include_testing)
    except Exception as exc:  # pragma: no cover - runtime safety
        logger.error("Failed to fetch event schedule for year %s: %s", year, exc)
        sys.exit(1)

    if schedule is None or schedule.empty:
        logger.error("No events found for season %s", year)
        sys.exit(1)

    # Sort events by RoundNumber or EventDate fallback
    if "RoundNumber" in schedule.columns:
        schedule = schedule.sort_values("RoundNumber")
    elif "EventDate" in schedule.columns:
        schedule = schedule.sort_values("EventDate")

    events = []
    for _, row in schedule.iterrows():
        event_name = row.get("EventName")
        official_name = row.get("OfficialEventName")
        country = row.get("Country")
        location = row.get("Location")
        round_num = row.get("RoundNumber")
        event_format = (row.get("EventFormat") or row.get("EventFormatName") or "").lower()
        if not event_name:
            continue
        events.append(
            {
                "event_name": event_name,
                "official_name": official_name,
                "country": country,
                "location": location,
                "round": round_num,
                "format": event_format,
            }
        )

    logger.info("[info] Found %s events for season %s", len(events), year)
    if events:
        first_names = [e["event_name"] for e in events[:5]]
        logger.info("[info] First events: %s", first_names)

    total_sessions = len(events) * len(session_codes)
    if not dry_run and not confirm_long_run(total_sessions):
        logger.info("Aborting at user request.")
        sys.exit(0)

    sessions_attempted = 0
    sessions_successful = 0
    total_rows_exported = 0

    for ev in events:
        if auto_format:
            if ev.get("format") == "sprint":
                event_sessions = ["FP1", "SQ", "S", "Q", "R"]
            else:
                event_sessions = ["FP1", "FP2", "FP3", "Q", "R"]
        else:
            event_sessions = session_codes

        logger.info(
            "[event] year=%s round=%s event='%s' (%s, %s)",
            year,
            ev.get("round"),
            ev["event_name"],
            ev.get("country"),
            ev.get("location"),
        )
        for code in event_sessions:
            sessions_attempted += 1
            logger.info("[session] exporting session_type='%s' for event='%s'", code, ev["event_name"])
            if dry_run:
                logger.info(
                    "[dry-run] Would export session year=%s event='%s' code=%s to %s",
                    year,
                    ev["event_name"],
                    code,
                    out_root,
                )
                sessions_successful += 1
                continue
            try:
                rows_written = export_fastf1_session_to_parquet(
                    year=year,
                    event_name=ev["event_name"],
                    session_type=code,
                    output_root=str(out_root),
                    logger=logger,
                )
                total_rows_exported += rows_written
                sessions_successful += 1
                logger.info("[session] wrote %s rows for %s %s %s", rows_written, year, ev["event_name"], code)
            except Exception as exc:  # pragma: no cover - runtime safety
                reason = f"export failed: {exc}"
                log_missing(year, ev.get("event_name", ""), code, reason)
                logger.warning(
                    "[skip] Failed export for year=%s event='%s' session_type='%s': %s", year, ev["event_name"], code, exc
                )
                continue

    logger.info(
        "[summary] year=%s sessions_attempted=%s sessions_successful=%s total_rows_exported=%s",
        year,
        sessions_attempted,
        sessions_successful,
        total_rows_exported,
    )
    if sessions_successful == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
