import math
from typing import List, Optional

import duckdb
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..deps import get_db

router = APIRouter(tags=["pace"])


def _table_exists(db: duckdb.DuckDBPyConnection, schema: str, table: str) -> bool:
    return (
        db.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = ? AND table_name = ?",
            [schema, table],
        ).fetchone()
        is not None
    )


def _opt_int(val):
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    return int(val)


def _opt_float(val):
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    return float(val)


def _opt_str(val):
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    return str(val)


class SessionPaceEntry(BaseModel):
    season: int
    round: int
    grand_prix_slug: str
    session_code: str
    driver_number: int
    driver_name: str
    driver_code: Optional[str] = None
    team_name: str
    best_lap_duration: Optional[float] = None
    median_lap_duration: Optional[float] = None
    avg_lap_duration: Optional[float] = None
    total_laps: Optional[int] = None


class SeasonDriverPace(BaseModel):
    driver_number: int
    driver_name: str
    driver_code: Optional[str] = None
    team_name: str

    races_count: int
    best_lap_duration_min: Optional[float] = None
    best_lap_duration_median: Optional[float] = None
    best_lap_duration_avg: Optional[float] = None

    points_cumulative: Optional[float] = None
    championship_position: Optional[int] = None


class SeasonPaceResponse(BaseModel):
    season: int
    session_code: str
    races_total_in_season: int
    drivers: List[SeasonDriverPace]


@router.get("/session", response_model=List[SessionPaceEntry])
def pace_session(
    season: int = Query(..., description="Season (year)"),
    round: int = Query(..., description="Round number"),
    session_code: str = Query(..., description="Session code, e.g., Q, R, FP1"),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    if not _table_exists(db, "gold", "driver_session_summary"):
        raise HTTPException(
            status_code=500,
            detail="gold.driver_session_summary not found; rebuild gold tables first.",
        )

    sql = """
    SELECT
      season,
      round,
      grand_prix_slug,
      session_code,
      driver_number,
      driver_name,
      driver_code,
      team_name,
      best_lap_duration,
      median_lap_duration,
      avg_lap_duration,
      total_laps
    FROM gold.driver_session_summary
    WHERE season = ?
      AND round = ?
      AND session_code = ?
    ORDER BY best_lap_duration ASC
    LIMIT 50
    """
    try:
        df = db.execute(sql, [season, round, session_code]).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load session pace: {exc}") from exc

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No pace data found for season={season}, round={round}, session_code={session_code}.",
        )

    entries: List[SessionPaceEntry] = []
    for _, row in df.iterrows():
        entries.append(
            SessionPaceEntry(
                season=int(row["season"]),
                round=int(row["round"]),
                grand_prix_slug=str(row["grand_prix_slug"]),
                session_code=str(row["session_code"]),
                driver_number=int(row["driver_number"]),
                driver_name=str(row["driver_name"]),
                driver_code=_opt_str(row.get("driver_code")),
                team_name=str(row["team_name"]),
                best_lap_duration=_opt_float(row.get("best_lap_duration")),
                median_lap_duration=_opt_float(row.get("median_lap_duration")),
                avg_lap_duration=_opt_float(row.get("avg_lap_duration")),
                total_laps=_opt_int(row.get("total_laps")),
            )
        )

    return entries


@router.get("/season", response_model=SeasonPaceResponse)
def get_season_pace(
    season: int = Query(..., ge=1950),
    session_code: str = Query("R", description="FP1, FP2, FP3, SQ, S, Q, R"),
    min_rounds: int = Query(2, ge=1),
    top_n: int = Query(20, ge=1, le=100),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    if not _table_exists(db, "gold", "driver_session_summary"):
        raise HTTPException(
            status_code=500,
            detail="gold.driver_session_summary not found; rebuild gold tables first.",
        )
    if not _table_exists(db, "gold", "driver_season_standings"):
        raise HTTPException(
            status_code=500,
            detail="gold.driver_season_standings not found; rebuild gold tables first.",
        )

    pace_sql = """
    SELECT
      season,
      driver_number,
      driver_name,
      driver_code,
      team_name,
      COUNT(DISTINCT round) FILTER (WHERE best_lap_duration IS NOT NULL) AS races_count,
      MIN(best_lap_duration) AS best_lap_duration_min,
      MEDIAN(best_lap_duration) AS best_lap_duration_median,
      AVG(best_lap_duration) AS best_lap_duration_avg
    FROM gold.driver_session_summary
    WHERE
      season = ?
      AND session_code = ?
      AND best_lap_duration IS NOT NULL
    GROUP BY
      season,
      driver_number,
      driver_name,
      driver_code,
      team_name
    """
    try:
        pace_df = db.execute(pace_sql, [season, session_code]).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load season pace: {exc}") from exc

    if pace_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No pace data found for season={season}, session_code={session_code}.",
        )

    pace_df = pace_df[pace_df["races_count"] >= min_rounds]
    if pace_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No drivers meet min_rounds={min_rounds} for season={season}, session_code={session_code}.",
        )

    standings_sql = """
    SELECT
      season,
      round,
      grand_prix_slug,
      driver_number,
      driver_name,
      driver_code,
      team_name,
      points_cumulative,
      championship_position
    FROM gold.driver_season_standings
    WHERE
      season = ?
      AND round = (
        SELECT MAX(round) FROM gold.driver_season_standings WHERE season = ?
      )
    """
    try:
        standings_df = db.execute(standings_sql, [season, season]).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load season pace: {exc}") from exc

    standings_map = {}
    if not standings_df.empty:
        for _, row in standings_df.iterrows():
            standings_map[int(row["driver_number"])] = {
                "points_cumulative": _opt_float(row.get("points_cumulative")),
                "championship_position": _opt_int(row.get("championship_position")),
            }

    try:
        races_total_in_season = db.execute(
            """
            SELECT COUNT(DISTINCT round)
            FROM gold.driver_session_summary
            WHERE season = ?
              AND session_code = ?
              AND best_lap_duration IS NOT NULL
            """,
            [season, session_code],
        ).fetchone()[0]
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load season pace: {exc}") from exc

    sortable_entries = []
    for _, row in pace_df.iterrows():
        driver_number = int(row["driver_number"])
        standings = standings_map.get(driver_number, {})
        best_avg = _opt_float(row.get("best_lap_duration_avg"))
        points_cumulative = standings.get("points_cumulative")
        driver_entry = SeasonDriverPace(
            driver_number=driver_number,
            driver_name=str(row["driver_name"]),
            driver_code=_opt_str(row.get("driver_code")),
            team_name=str(row["team_name"]),
            races_count=int(row["races_count"]),
            best_lap_duration_min=_opt_float(row.get("best_lap_duration_min")),
            best_lap_duration_median=_opt_float(row.get("best_lap_duration_median")),
            best_lap_duration_avg=best_avg,
            points_cumulative=points_cumulative,
            championship_position=standings.get("championship_position"),
        )
        sortable_entries.append(
            (
                float("inf") if best_avg is None else best_avg,
                -points_cumulative if points_cumulative is not None else float("inf"),
                driver_entry.driver_name,
                driver_entry,
            )
        )

    sortable_entries.sort(key=lambda tup: (tup[0], tup[1], tup[2]))
    drivers = [entry[-1] for entry in sortable_entries[:top_n]]

    return SeasonPaceResponse(
        season=season,
        session_code=session_code,
        races_total_in_season=int(races_total_in_season),
        drivers=drivers,
    )
