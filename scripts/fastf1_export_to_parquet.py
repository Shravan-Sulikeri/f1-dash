import argparse
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import fastf1
import pandas as pd

CACHE_DIR = Path("/Volumes/SAMSUNG/apps/f1-dash/fastf1_cache")
DEFAULT_OUTPUT_ROOT = Path("/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1")
MISSING_LOG = Path("/Volumes/SAMSUNG/apps/f1-dash/Missing Data FastF1.txt")

logger = logging.getLogger(__name__)


def enable_fastf1_cache() -> None:
    """Ensure FastF1 cache is configured once per process."""
    fastf1.Cache.enable_cache(str(CACHE_DIR))
    logging.info("FastF1 cache enabled at: %s", CACHE_DIR)


def slugify(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name or "unknown"


def log_missing(year: int, event: str, session_code: str, reason: str) -> None:
    """Append a human-readable entry to the missing-data log."""
    try:
        MISSING_LOG.parent.mkdir(parents=True, exist_ok=True)
        with MISSING_LOG.open("a") as f:
            f.write(f"year={year}, event={event}, session={session_code}: {reason}\n")
    except Exception:
        # Logging failures should not mask the original error
        pass


def to_seconds(series: pd.Series) -> pd.Series:
    if series is None:
        return pd.Series(dtype="float")
    if pd.api.types.is_timedelta64_dtype(series):
        return series.dt.total_seconds()
    return pd.to_numeric(series, errors="coerce")


def load_session(year: int, event: str, session_type: str, log: logging.Logger) -> fastf1.core.Session:
    log.info("Requesting session year=%s event=%s session_type=%s", year, event, session_type)
    sess = fastf1.get_session(year, event, session_type)
    try:
        sess.load(telemetry=False, weather=False)
    except Exception as exc:  # pragma: no cover - runtime safety
        log.error("Failed to load session: %s", exc)
        raise

    drivers = getattr(sess, "drivers", []) or []
    if len(drivers) < 20:
        reason = f"only {len(drivers)} drivers loaded"
        log_missing(year, event, session_type, reason)
        log.error("Missing driver data for %s %s: %s", event, session_type, reason)
        raise ValueError(reason)
    return sess


def normalize_laps(sess: fastf1.core.Session, session_code: str, year: int, log: logging.Logger) -> Optional[pd.DataFrame]:
    laps = sess.laps
    if laps is None or laps.empty:
        log.warning("Session laps are empty; nothing to export.")
        return None

    event = getattr(sess, "event", None)
    event_name = None
    event_number = None
    if isinstance(event, pd.Series):
        event_name = event.get("EventName")
        event_number = event.get("EventNumber")
    gp_name = event_name or getattr(sess, "eventName", None) or "unknown"
    gp_slug = slugify(str(gp_name))
    session_name = getattr(sess, "name", session_code)

    norm = pd.DataFrame()
    norm["season"] = pd.Series(year, index=laps.index)
    if event_number is not None:
        norm["round"] = pd.to_numeric(event_number, errors="coerce").astype("Int64")
    else:
        norm["round"] = pd.Series([pd.NA] * len(laps), dtype="Int64")
    norm["grand_prix"] = gp_name
    norm["grand_prix_slug"] = gp_slug
    norm["session"] = session_name
    norm["session_code"] = session_code
    norm["source"] = "fastf1"
    norm["ingested_at"] = datetime.utcnow().isoformat()

    norm["driver_number"] = pd.to_numeric(laps.get("DriverNumber"), errors="coerce").astype("Int64")
    norm["driver_code"] = laps.get("Driver")
    norm["team_name"] = laps.get("Team")
    norm["compound"] = laps.get("Compound")
    norm["stint"] = pd.to_numeric(laps.get("Stint"), errors="coerce").astype("Int64")
    norm["tyre_life_laps"] = pd.to_numeric(laps.get("TyreLife"), errors="coerce")

    norm["lap_number"] = pd.to_numeric(laps.get("LapNumber"), errors="coerce").astype("Int64")
    norm["lap_duration"] = to_seconds(laps.get("LapTime"))
    norm["duration_sector_1"] = to_seconds(laps.get("Sector1Time"))
    norm["duration_sector_2"] = to_seconds(laps.get("Sector2Time"))
    norm["duration_sector_3"] = to_seconds(laps.get("Sector3Time"))

    if "LapStartDate" in laps.columns:
        norm["date_start"] = laps["LapStartDate"]
    elif "Time" in laps.columns:
        norm["date_start"] = laps["Time"]
    else:
        norm["date_start"] = pd.NaT  # TODO: derive a better lap start timestamp if available

    norm["is_pit_out_lap"] = laps.get("PitOutTime").notna() if "PitOutTime" in laps.columns else False
    norm["position"] = pd.to_numeric(laps.get("Position"), errors="coerce").astype("Int64")

    norm["i1_speed"] = pd.to_numeric(laps.get("SpeedI1"), errors="coerce")
    norm["i2_speed"] = pd.to_numeric(laps.get("SpeedI2"), errors="coerce")
    norm["fl_speed"] = pd.to_numeric(laps.get("SpeedFL"), errors="coerce")
    norm["st_speed"] = pd.to_numeric(laps.get("SpeedST"), errors="coerce")

    norm["is_accurate"] = laps.get("IsAccurate")
    norm["is_personal_best"] = laps.get("IsPersonalBest")
    norm["track_status"] = laps.get("TrackStatus")
    norm["deleted"] = laps.get("Deleted")
    norm["deleted_reason"] = laps.get("DeletedReason")

    return norm


def write_parquet(df: pd.DataFrame, output_root: Path, season: int, gp_slug: str, session_code: str) -> Path:
    out_dir = output_root / "laps" / f"season={season}" / f"grand_prix_slug={gp_slug}" / f"session_code={session_code}"
    os.makedirs(out_dir, exist_ok=True)
    out_file = out_dir / "part-00000.parquet"
    df.to_parquet(out_file, index=False)
    return out_file


def export_fastf1_session_to_parquet(
    year: int,
    event_name: str,
    session_type: str,
    output_root: str,
    logger: logging.Logger,
) -> int:
    log = logger or logging.getLogger(__name__)
    output_path = Path(output_root)

    enable_fastf1_cache()
    sess = load_session(year, event_name, session_type, log)

    event = getattr(sess, "event", None)
    if isinstance(event, pd.Series):
        log.info(
            "Session resolved: EventName=%s, SessionName=%s, Country=%s, Location=%s",
            event.get("EventName"),
            getattr(sess, "name", None),
            event.get("Country"),
            event.get("Location"),
        )
    else:
        log.info("Session resolved: EventName=%s, SessionName=%s", getattr(sess, "eventName", None), getattr(sess, "name", None))

    norm = normalize_laps(sess, session_type, year, log)
    if norm is None or norm.empty:
        reason = "laps empty"
        log_missing(year, event_name, session_type, reason)
        log.warning("No lap data for %s %s (logged missing, skipping write)", event_name, session_type)
        return 0

    # Ensure the lap set covers all drivers for this session. If fewer than 20,
    # log it but continue so we don't block the rest of the season export.
    driver_count = len(norm["driver_number"].dropna().unique())
    if driver_count < 20:
        reason = f"only {driver_count} driver laps present"
        log_missing(year, event_name, session_type, reason)
        log.error("Incomplete lap data for %s %s: %s", event_name, session_type, reason)
        raise ValueError(reason)

    log.info("Normalized laps shape: %s, columns: %s", norm.shape, list(norm.columns))
    log.info("Normalized laps head:\n%s", norm.head(5))

    out_file = write_parquet(norm, output_path, year, norm["grand_prix_slug"].iloc[0], session_type)
    log.info("Wrote %s rows to %s", len(norm), out_file)
    return len(norm)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export FastF1 session laps to partitioned Parquet.")
    parser.add_argument("--year", type=int, required=True, help="Season year, e.g. 2018")
    parser.add_argument("--event", type=str, required=True, help="Event name, e.g. Australian, Bahrain")
    parser.add_argument(
        "--session-type",
        type=str,
        required=True,
        help="Session code, e.g. R, Q, FP1, FP2, FP3, S, SQ",
    )
    parser.add_argument(
        "--output-root",
        type=str,
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Output root for partitioned Parquet",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    log = logging.getLogger("fastf1_export")

    log.info("Args: year=%s event=%s session_type=%s output_root=%s", args.year, args.event, args.session_type, args.output_root)

    try:
        export_fastf1_session_to_parquet(
            year=args.year,
            event_name=args.event,
            session_type=args.session_type,
            output_root=args.output_root,
            logger=log,
        )
    except Exception as exc:  # pragma: no cover - runtime safety
        log.error("Export failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
