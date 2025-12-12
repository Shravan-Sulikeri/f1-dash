import argparse
import sys
from pathlib import Path
from datetime import datetime
import re

import fastf1
import pandas as pd

CACHE_PATH = Path("/Volumes/SAMSUNG/apps/f1-dash/fastf1_cache")
SESSION_RESULT_ROOT = Path("/Volumes/SAMSUNG/apps/f1-dash/bronze_fastf1/session_result")
MISSING_LOG = Path("/Volumes/SAMSUNG/apps/f1-dash/Missing Data FastF1.txt")


def slugify(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name or "unknown"


def log_missing(year: int, event: str, session_code: str, reason: str) -> None:
    try:
        MISSING_LOG.parent.mkdir(parents=True, exist_ok=True)
        with MISSING_LOG.open("a") as f:
            f.write(f"year={year}, event={event}, session={session_code}: {reason}\n")
    except Exception:
        pass


def load_session(year: int, event: str, session_type: str):
    fastf1.Cache.enable_cache(str(CACHE_PATH))
    print(f"[info] FastF1 cache enabled at: {CACHE_PATH}")
    print(f"[info] Requesting session year={year}, event='{event}', session_type='{session_type}'")
    session = fastf1.get_session(year, event, session_type)
    try:
        print("[info] Loading session data (telemetry=False, weather=False)...")
        session.load(telemetry=False, weather=False)
    except Exception as exc:
        print(f"[error] Failed to load session: {exc}")
        sys.exit(1)

    drivers = getattr(session, "drivers", []) or []
    if len(drivers) < 20:
        reason = f"only {len(drivers)} drivers loaded"
        log_missing(year, event, session_type, reason)
        print(f"[error] {reason}; aborting export")
        sys.exit(1)
    return session


def _normalize_results_df(session, results: pd.DataFrame, session_code: str, season_arg: int) -> pd.DataFrame:
    ev = session.event if isinstance(session.event, pd.Series) else pd.Series()
    season = ev.get("Year") or ev.get("year") or season_arg
    round_num = ev.get("RoundNumber") if isinstance(ev, pd.Series) else None
    gp_name = ev.get("EventName") if isinstance(ev, pd.Series) else getattr(session, "eventName", "unknown")
    gp_name = gp_name or "unknown"
    gp_slug = slugify(str(gp_name))
    session_name = getattr(session, "name", session_code)

    length = len(results)
    norm = pd.DataFrame()
    norm["season"] = pd.Series(season, index=results.index, dtype="Int64")
    norm["round"] = pd.Series(round_num, index=results.index)
    norm["round"] = pd.to_numeric(norm["round"], errors="coerce").astype("Int64")
    norm["grand_prix"] = gp_name
    norm["grand_prix_slug"] = gp_slug
    norm["session"] = session_name
    norm["session_code"] = session_code
    norm["source"] = "fastf1"
    norm["ingested_at"] = datetime.utcnow().isoformat()

    # Driver/team info
    norm["driver_number"] = (results.get("DriverNumber") if "DriverNumber" in results.columns else pd.Series([pd.NA] * length)).astype("string")
    norm["driver_code"] = (results.get("Abbreviation") if "Abbreviation" in results.columns else pd.Series([pd.NA] * length)).astype("string")
    norm["team_name"] = results.get("TeamName") if "TeamName" in results.columns else pd.Series([pd.NA] * length)

    # Positions
    def _int_col(col):
        if col in results.columns:
            return pd.to_numeric(results[col], errors="coerce").astype("Int64")
        return pd.Series([pd.NA] * length, dtype="Int64")

    norm["grid_position"] = _int_col("GridPosition")
    norm["classified_position"] = _int_col("ClassifiedPosition")
    norm["finish_position"] = _int_col("Position")

    # Status/points
    norm["status"] = results["Status"] if "Status" in results.columns else pd.Series([""] * length)
    points_series = pd.to_numeric(results["Points"], errors="coerce") if "Points" in results.columns else pd.Series([0] * length)
    norm["points"] = points_series.fillna(0)

    # Ensure columns exist even if empty
    required_cols = [
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
        "team_name",
        "grid_position",
        "classified_position",
        "finish_position",
        "status",
        "points",
    ]
    for col in required_cols:
        if col not in norm.columns:
            norm[col] = pd.NA

    return norm


def summarize_session(session) -> None:
    event_name = session.event.get("EventName", "unknown")
    session_name = getattr(session, "name", "unknown")
    drivers = getattr(session, "drivers", [])
    driver_numbers = list(drivers)[:10]
    print(f"[info] Session resolved: event='{event_name}', session_name='{session_name}'")
    print(f"[info] Drivers: count={len(drivers)}, first_10={driver_numbers}")

    try:
        ev = session.event
        if ev is None or not isinstance(ev, pd.Series):
            print("[warn] Event metadata not available or not a pandas Series.")
        else:
            keys = [
                "EventName",
                "EventDate",
                "EventFormat",
                "EventNumber",
                "Country",
                "Location",
                "OfficialEventName",
            ]
            print("[info] Event metadata:")
            for key in keys:
                val = ev.get(key) if isinstance(ev, pd.Series) else None
                print(f"  - {key}: {val}")
    except Exception as exc:
        print(f"[warn] Failed to read event metadata: {exc}")


def summarize_laps(laps: pd.DataFrame) -> None:
    try:
        print(f"[info] laps shape: {laps.shape}")
        if laps.empty:
            print("[warn] laps DataFrame is empty.")
            return
        desired_cols = ["DriverNumber", "Driver", "LapNumber", "LapTime", "PitOutLap", "IsAccurate"]
        cols_present = [c for c in desired_cols if c in laps.columns]
        if not cols_present:
            print("[info] None of the preview columns are present in laps DataFrame.")
        else:
            print(f"[info] laps preview columns present: {cols_present}")
            print(laps[cols_present].head(5))

        cols_sorted = sorted(laps.columns.tolist())
        print(f"[info] laps columns ({len(cols_sorted)}): {cols_sorted}")
        print("[info] laps dtypes:")
        for col, dtype in laps.dtypes.items():
            print(f"  {col}: {dtype}")
    except Exception as exc:
        print(f"[warn] Failed to summarize laps: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="FastF1 session export (preview only).")
    parser.add_argument("--year", type=int, required=True, help="Season year, e.g. 2023")
    parser.add_argument("--event", type=str, required=True, help="Event name, e.g. Bahrain, Monaco")
    parser.add_argument(
        "--session-type",
        type=str,
        required=True,
        help="Session code, e.g. R, Q, FP1, FP2, FP3, S, SQ",
    )
    args = parser.parse_args()

    session = load_session(args.year, args.event, args.session_type)
    summarize_session(session)

    laps = session.laps
    if laps is None or laps.empty:
        reason = "laps empty"
        log_missing(session.event.get("Year", args.year), session.event.get("EventName", args.event), args.session_type, reason)
        print("[error] Session laps are empty; nothing to preview.")
        sys.exit(1)
    summarize_laps(laps)

    # Export session results
    try:
        results_df = session.results
        if results_df is None or len(results_df) == 0:
            reason = "results empty"
            log_missing(args.year, args.event, args.session_type, reason)
            print("[info] No results data available for this session; skipping results export")
        else:
            norm_results = _normalize_results_df(session, results_df, args.session_type, args.year)
            unique_drivers = norm_results["driver_number"].dropna().nunique()
            if unique_drivers < 20:
                reason = f"only {unique_drivers} driver results present"
                log_missing(args.year, args.event, args.session_type, reason)
                print(f"[warn] Incomplete results ({unique_drivers} drivers); logging and continuing")
            print(f"[info] Normalized results shape: {norm_results.shape}, columns: {list(norm_results.columns)}")
            print(norm_results.head(5))
            season_val = norm_results["season"].dropna().iloc[0] if not norm_results["season"].dropna().empty else args.year
            gp_slug = norm_results["grand_prix_slug"].iloc[0]
            out_dir = SESSION_RESULT_ROOT / f"season={season_val}" / f"grand_prix_slug={gp_slug}" / f"session_code={args.session_type}"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / "part-00000.parquet"
            norm_results.to_parquet(out_file, index=False)
            print(f"[info] Wrote {len(norm_results)} result rows to {out_file}")
    except Exception as exc:
        print(f"[WARNING] [results-skip] Failed export for year={args.year} event='{args.event}' session_type='{args.session_type}': {exc}")


if __name__ == "__main__":
    main()
