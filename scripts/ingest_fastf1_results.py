import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import fastf1
import pandas as pd

# Paths
CACHE_DIR = Path("/Volumes/SAMSUNG/apps/f1-dash/fastf1_cache")
BRONZE_BASE = Path(__file__).resolve().parents[1] / "bronze_fastf1" / "session_result"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ingest_fastf1_results")


def slugify_grand_prix(name: str) -> str:
    """Simple slugify: lowercase, non-alnum to hyphen, collapse hyphens."""
    import re

    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name or "unknown"


def normalize_results_df(
    season: int,
    round_num: int,
    event_name: str,
    session_code: str,
    session_name: str,
    session,
) -> Optional[pd.DataFrame]:
    results = session.results
    if results is None or results.empty:
        return None

    # Reset index to avoid alignment issues
    results = results.reset_index(drop=True)

    gp_slug = slugify_grand_prix(event_name)
    cols = results.columns

    def pick(col: str, alt: Optional[str] = None):
        if col in cols:
            return results[col].values  # Use .values to get numpy array
        if alt and alt in cols:
            return results[alt].values
        return [pd.NA] * len(results)

    # Build DataFrame with proper length from the start
    n_rows = len(results)
    norm = pd.DataFrame({
        "season": [season] * n_rows,
        "round": [round_num] * n_rows,
        "grand_prix": [event_name] * n_rows,
        "grand_prix_slug": [gp_slug] * n_rows,
        "session": [session_name or session_code] * n_rows,
        "session_code": [session_code] * n_rows,
        "source": ["fastf1"] * n_rows,
        "ingested_at": [datetime.utcnow().isoformat()] * n_rows,
    })

    norm["driver_number"] = pick("DriverNumber")
    norm["driver_code"] = pick("Abbreviation", "DriverId")
    norm["driver_name"] = pick("Driver")
    norm["team_name"] = pick("TeamName")
    norm["grid_position"] = pd.to_numeric(pick("GridPosition"), errors="coerce")
    norm["classified_position"] = pd.to_numeric(pick("ClassifiedPosition"), errors="coerce")
    norm["finish_position"] = pd.to_numeric(pick("Position"), errors="coerce")
    norm["status"] = pick("Status")
    norm["points"] = pd.to_numeric(pick("Points"), errors="coerce")

    # Drop rows without a driver_code (e.g., SC or invalid entries)
    norm = norm[norm["driver_code"].notna() & (norm["driver_code"] != "")]

    # Ensure column order
    norm = norm[
        [
            "season",
            "round",
            "grand_prix",
            "grand_prix_slug",
            "session",
            "session_code",
            "source",
            "ingested_at",
            "driver_number",
            "driver_code",
            "driver_name",
            "team_name",
            "grid_position",
            "classified_position",
            "finish_position",
            "status",
            "points",
        ]
    ]
    return norm


def ingest_season(season: int, session_codes: Iterable[str], delay: float = 0.5) -> None:
    logger.info("[info] Ingesting FastF1 results for season=%s, sessions=%s", season, list(session_codes))
    fastf1.Cache.enable_cache(str(CACHE_DIR))
    try:
        schedule = fastf1.get_event_schedule(season, include_testing=False)
    except Exception as exc:  # pragma: no cover - runtime safety
        logger.warning("[warning] Failed to fetch schedule for season=%s: %s", season, exc)
        return

    if schedule is None or schedule.empty:
        logger.warning("[warning] Empty schedule for season=%s; skipping.", season)
        return

    for _, row in schedule.iterrows():
        try:
            event_name = row.get("EventName")
            round_num = int(row.get("RoundNumber")) if row.get("RoundNumber") is not None else None
            if not event_name or round_num is None:
                continue
            for code in session_codes:
                session = fastf1.get_session(season, round_num, code)
                session.load()
                norm = normalize_results_df(season, round_num, event_name, code, session.name, session)
                if norm is None or norm.empty:
                    logger.info("[info] No results for season=%s round=%s event='%s' session=%s; skipping.", season, round_num, event_name, code)
                    continue
                out_dir = (
                    BRONZE_BASE
                    / f"season={season}"
                    / f"grand_prix_slug={slugify_grand_prix(event_name)}"
                    / f"session_code={code}"
                )
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / "part-00000.parquet"
                if out_path.exists():
                    logger.info(
                        "[info] Skipping season=%s round=%s session=%s (file already exists): %s",
                        season,
                        round_num,
                        code,
                        out_path,
                    )
                    continue
                norm.to_parquet(out_path, index=False)
                logger.info(
                    "[info] Wrote %s rows to %s",
                    len(norm),
                    out_path,
                )
                if delay > 0:
                    time.sleep(delay)
        except Exception as exc:  # pragma: no cover - runtime safety
            logger.warning(
                "[warning] Failed to ingest season=%s round=%s event='%s': %s",
                season,
                row.get("RoundNumber"),
                row.get("EventName"),
                exc,
            )
            continue


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest FastF1 race results into bronze_fastf1/session_result.")
    parser.add_argument("--season-start", type=int, default=2023, help="Start season (inclusive).")
    parser.add_argument("--season-end", type=int, default=2025, help="End season (inclusive).")
    parser.add_argument(
        "--sessions",
        type=str,
        default="R,Q,SPR,SQ,FP1,FP2,FP3",
        help="Comma-separated session codes to ingest (default: R,Q,SPR,SQ,FP1,FP2,FP3)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Seconds to sleep between session fetches to reduce rate-limit risk (default: 0.5s)",
    )
    args = parser.parse_args()

    start = args.season_start if args.season_start is not None else args.season_end
    end = args.season_end if args.season_end is not None else args.season_start
    if start is None:
        start = end = 2018
    if end is None:
        end = start

    session_codes = [s.strip().upper() for s in args.sessions.split(",") if s.strip()]
    if not session_codes:
        session_codes = ["R"]

    for yr in range(start, end + 1):
        ingest_season(yr, session_codes=session_codes, delay=args.delay)


if __name__ == "__main__":
    main()
