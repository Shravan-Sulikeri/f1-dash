from typing import List, Optional

import duckdb
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..deps import get_db

router = APIRouter(prefix="/standings", tags=["standings"])


class DriverStandingEntry(BaseModel):
    position: int
    driver_number: int
    driver_name: str
    driver_code: Optional[str] = None
    team_name: str
    points_round: float
    points_cumulative: float


class DriverStandingsResponse(BaseModel):
    season: int
    round: int
    grand_prix_slug: str
    entries: List[DriverStandingEntry]


class TeamStandingEntry(BaseModel):
    position: int
    team_name: str
    points_round: float
    points_cumulative: float


class TeamStandingsResponse(BaseModel):
    season: int
    round: int
    grand_prix_slug: str
    entries: List[TeamStandingEntry]


def _table_exists(db: duckdb.DuckDBPyConnection, schema: str, table: str) -> bool:
    sql = """
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = ? AND table_name = ?
    """
    return db.execute(sql, [schema, table]).fetchone() is not None


def _resolve_round(
    db: duckdb.DuckDBPyConnection, season: int, round_param: Optional[int], table: str
) -> int:
    if round_param is not None:
        exists = (
            db.execute(
                f"SELECT 1 FROM {table} WHERE season = ? AND round = ? LIMIT 1", [season, round_param]
            ).fetchone()
            is not None
        )
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"No standings found for season={season}, round={round_param}.",
            )
        return round_param

    res = db.execute(f"SELECT MAX(round) FROM {table} WHERE season = ?", [season]).fetchone()
    if res is None or res[0] is None:
        raise HTTPException(
            status_code=404,
            detail=f"No standings found for season={season}.",
        )
    return int(res[0])


@router.get("/drivers", response_model=DriverStandingsResponse)
def driver_standings(
    season: int = Query(..., description="Season (year)"),
    round: Optional[int] = Query(None, description="Round number; if omitted uses latest round for season"),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    if not _table_exists(db, "gold", "driver_season_standings"):
        raise HTTPException(
            status_code=500,
            detail="gold.driver_season_standings not found; rebuild gold tables first.",
        )

    use_round = _resolve_round(db, season, round, "gold.driver_season_standings")

    sql = """
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
      AND round = ?
    ORDER BY championship_position ASC, points_cumulative DESC
    LIMIT 100
    """
    try:
        df = db.execute(sql, [season, use_round]).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load driver standings: {exc}") from exc

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No standings found for season={season}, round={use_round}.",
        )

    gp_slug = str(df.iloc[0]["grand_prix_slug"])
    entries = [
        DriverStandingEntry(
            position=int(row["championship_position"]),
            driver_number=int(row["driver_number"]),
            driver_name=str(row["driver_name"]),
            driver_code=(None if row.get("driver_code") is None else str(row["driver_code"])),
            team_name=str(row["team_name"]),
            points_round=float(row["points_round"]),
            points_cumulative=float(row["points_cumulative"]),
        )
        for _, row in df.iterrows()
    ]
    return DriverStandingsResponse(
        season=season,
        round=use_round,
        grand_prix_slug=gp_slug,
        entries=entries,
    )


@router.get("/teams", response_model=TeamStandingsResponse)
def team_standings(
    season: int = Query(..., description="Season (year)"),
    round: Optional[int] = Query(None, description="Round number; if omitted uses latest round for season"),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    if not _table_exists(db, "gold", "team_season_standings"):
        raise HTTPException(
            status_code=500,
            detail="gold.team_season_standings not found; rebuild gold tables first.",
        )

    use_round = _resolve_round(db, season, round, "gold.team_season_standings")

    sql = """
    SELECT
      season,
      round,
      grand_prix_slug,
      team_name,
      points_round_team,
      points_cumulative_team,
      championship_position_team
    FROM gold.team_season_standings
    WHERE season = ?
      AND round = ?
    ORDER BY championship_position_team ASC, points_cumulative_team DESC
    LIMIT 100
    """
    try:
        df = db.execute(sql, [season, use_round]).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load team standings: {exc}") from exc

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No standings found for season={season}, round={use_round}.",
        )

    gp_slug = str(df.iloc[0]["grand_prix_slug"])
    entries = [
        TeamStandingEntry(
            position=int(row["championship_position_team"]),
            team_name=str(row["team_name"]),
            points_round=float(row["points_round_team"]),
            points_cumulative=float(row["points_cumulative_team"]),
        )
        for _, row in df.iterrows()
    ]
    return TeamStandingsResponse(
        season=season,
        round=use_round,
        grand_prix_slug=gp_slug,
        entries=entries,
    )
