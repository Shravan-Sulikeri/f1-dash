import math
from typing import List, Optional

import duckdb
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..deps import get_db

router = APIRouter(tags=["results"])


def _table_exists(db: duckdb.DuckDBPyConnection, schema: str, table: str) -> bool:
    return (
        db.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = ? AND table_name = ?",
            [schema, table],
        ).fetchone()
        is not None
    )


class SessionResultEntry(BaseModel):
    driver_number: int
    driver_name: str
    driver_code: Optional[str] = None
    team_name: str
    team_colour: Optional[str] = None
    country_code: Optional[str] = None
    finish_position: Optional[int] = None
    grid_position: Optional[int] = None
    status: Optional[str] = None
    points: Optional[float] = None
    best_lap_duration: Optional[float] = None
    total_laps: int
    is_classified: bool


class SessionResultsResponse(BaseModel):
    season: int
    round: int
    grand_prix_slug: str
    grand_prix: Optional[str] = None
    session_code: str
    session_name: Optional[str] = None
    entries: List[SessionResultEntry]


class DriverRoundResult(BaseModel):
    round: int
    grand_prix_slug: str
    grand_prix: Optional[str] = None
    session_code: str
    finish_position: Optional[int] = None
    grid_position: Optional[int] = None
    status: Optional[str] = None
    points_round: float
    points_cumulative: float
    delta_championship_position: Optional[int] = None


class DriverSeasonResultsResponse(BaseModel):
    season: int
    driver_number: int
    driver_name: str
    driver_code: Optional[str] = None
    team_name: str
    entries: List[DriverRoundResult]


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


@router.get("/session", response_model=SessionResultsResponse)
def get_session_results(
    season: int = Query(..., ge=1950),
    round: int = Query(..., ge=1),
    session_code: str = Query(..., description="FP1, FP2, FP3, SQ, S, Q, R"),
    top_n: int = Query(20, ge=1, le=100),
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
      team_colour,
      country_code,
      finish_position,
      grid_position,
      status,
      points,
      total_laps,
      best_lap_duration
    FROM gold.driver_session_summary
    WHERE
      season = ?
      AND round = ?
      AND session_code = ?
    ORDER BY
      CASE WHEN finish_position IS NULL THEN 999 ELSE finish_position END ASC,
      points DESC,
      driver_name ASC
    LIMIT ?
    """
    try:
        df = db.execute(sql, [season, round, session_code, top_n]).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load session results: {exc}") from exc

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No results found for season={season}, round={round}, session_code={session_code}.",
        )

    first = df.iloc[0]
    gp_slug = str(first["grand_prix_slug"])
    gp_name = None
    sess_name = None

    def _compute_is_classified(finish_position, status):
        if finish_position is None:
            return False
        if status is None:
            return True
        status_up = str(status).upper()
        bad_tokens = ["DNF", "DSQ", "DNS", "DNQ", "RET"]
        return not any(tok in status_up for tok in bad_tokens)

    entries: List[SessionResultEntry] = []
    for _, row in df.iterrows():
        finish_position = _opt_int(row.get("finish_position"))
        status = _opt_str(row.get("status"))
        entries.append(
            SessionResultEntry(
                driver_number=int(row["driver_number"]),
                driver_name=str(row["driver_name"]),
                driver_code=_opt_str(row.get("driver_code")),
                team_name=str(row["team_name"]),
                team_colour=_opt_str(row.get("team_colour")),
                country_code=_opt_str(row.get("country_code")),
                finish_position=finish_position,
                grid_position=_opt_int(row.get("grid_position")),
                status=status,
                points=_opt_float(row.get("points")),
                best_lap_duration=_opt_float(row.get("best_lap_duration")),
                total_laps=int(row["total_laps"]),
                is_classified=_compute_is_classified(finish_position, status),
            )
        )

    return SessionResultsResponse(
        season=season,
        round=round,
        grand_prix_slug=gp_slug,
        grand_prix=gp_name,
        session_code=session_code,
        session_name=sess_name,
        entries=entries,
    )


@router.get("/driver-season", response_model=DriverSeasonResultsResponse)
def get_driver_season_results(
    season: int = Query(..., ge=1950),
    driver_number: int = Query(..., ge=1),
    session_code: str = Query("R", description="Target session type for season results, default R"),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    if not _table_exists(db, "gold", "driver_season_standings"):
        raise HTTPException(
            status_code=500,
            detail="gold.driver_season_standings not found; rebuild gold tables first.",
        )
    if not _table_exists(db, "gold", "driver_session_summary"):
        raise HTTPException(
            status_code=500,
            detail="gold.driver_session_summary not found; rebuild gold tables first.",
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
      points_round,
      points_cumulative,
      championship_position
    FROM gold.driver_season_standings
    WHERE season = ?
      AND driver_number = ?
    ORDER BY round ASC
    """
    try:
        standings_df = db.execute(standings_sql, [season, driver_number]).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load driver season standings: {exc}") from exc

    if standings_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No season results found for driver={driver_number}, season={season}.",
        )

    standings_df = standings_df.sort_values("round")

    # Pull session-level finish/grid/status for the given session_code
    sess_sql = """
    SELECT
      season,
      round,
      grand_prix_slug,
      session_code,
      finish_position,
      grid_position,
      status
    FROM gold.driver_session_summary
    WHERE season = ?
      AND driver_number = ?
      AND session_code = ?
    """
    try:
        sess_df = db.execute(sess_sql, [season, driver_number, session_code]).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load driver session details: {exc}") from exc

    sess_map = {}
    for _, r in sess_df.iterrows():
        key = (int(r["round"]), str(r["grand_prix_slug"]))
        sess_map[key] = {
            "finish_position": _opt_int(r.get("finish_position")),
            "grid_position": _opt_int(r.get("grid_position")),
            "status": _opt_str(r.get("status")),
        }

    first = standings_df.iloc[0]
    entries: List[DriverRoundResult] = []
    prev_pos = None
    for _, row in standings_df.iterrows():
        key = (int(row["round"]), str(row["grand_prix_slug"]))
        sess_info = sess_map.get(key, {})
        current_pos = _opt_int(row.get("championship_position"))
        delta = None
        if prev_pos is not None and current_pos is not None:
            delta = prev_pos - current_pos
        prev_pos = current_pos
        entries.append(
            DriverRoundResult(
                round=int(row["round"]),
                grand_prix_slug=str(row["grand_prix_slug"]),
                grand_prix=sess_info.get("grand_prix"),
                session_code=session_code,
                finish_position=sess_info.get("finish_position"),
                grid_position=sess_info.get("grid_position"),
                status=sess_info.get("status"),
                points_round=float(row["points_round"]),
                points_cumulative=float(row["points_cumulative"]),
                delta_championship_position=delta,
            )
        )

    return DriverSeasonResultsResponse(
        season=season,
        driver_number=driver_number,
        driver_name=str(first["driver_name"]),
        driver_code=None if first.get("driver_code") is None else str(first["driver_code"]),
        team_name=str(first["team_name"]),
        entries=entries,
    )
