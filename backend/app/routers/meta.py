from typing import List

import duckdb
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..deps import get_db
from ..db import get_warehouse_path


class SeasonMeta(BaseModel):
    season: int
    has_races: bool
    has_sprints: bool
    min_round: int
    max_round: int


class SeasonsResponse(BaseModel):
    seasons: List[SeasonMeta]


class RaceMeta(BaseModel):
    season: int
    round: int
    grand_prix_slug: str


router = APIRouter(tags=["meta"])


def _table_exists(con: duckdb.DuckDBPyConnection, schema: str, table: str) -> bool:
    sql = """
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = ? AND table_name = ?
    """
    return con.execute(sql, [schema, table]).fetchone() is not None


@router.get("/health")
def health(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    warehouse = get_warehouse_path()
    ok = True
    try:
        db.execute("SELECT 1").fetchone()
    except Exception:
        ok = False

    tables = {
        "silver.laps": _table_exists(db, "silver", "laps"),
        "silver.drivers": _table_exists(db, "silver", "drivers"),
        "silver.session_results": _table_exists(db, "silver", "session_results"),
        "gold.driver_session_summary": _table_exists(db, "gold", "driver_session_summary"),
        "gold.team_session_summary": _table_exists(db, "gold", "team_session_summary"),
    }

    return {"warehouse": warehouse, "db_ok": ok, "tables": tables}


@router.get("/tables")
def list_tables(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    sql = """
    SELECT table_schema, table_name
    FROM information_schema.tables
    ORDER BY table_schema, table_name
    LIMIT 200
    """
    df = db.execute(sql).fetchdf()
    return df.to_dict(orient="records")


@router.get("/seasons", response_model=SeasonsResponse)
def seasons(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """
    Return available seasons with basic metadata derived from gold.race_winner_top3.
    """
    if not _table_exists(db, "gold", "race_winner_top3"):
        raise HTTPException(
            status_code=500,
            detail="gold.race_winner_top3 not found; rebuild gold tables first.",
        )

    sql = """
    WITH base AS (
      SELECT season, round
      FROM gold.race_winner_top3
    ),
    agg AS (
      SELECT
        season,
        MIN(round) AS min_round,
        MAX(round) AS max_round,
        1 AS has_races,
        0 AS has_sprints
      FROM base
      GROUP BY season
    )
    SELECT season, min_round, max_round, has_races, has_sprints
    FROM agg
    ORDER BY season
    """
    try:
        df = db.execute(sql).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load seasons metadata: {exc}") from exc

    if df.empty:
        return SeasonsResponse(seasons=[])

    seasons = [
        SeasonMeta(
            season=int(row["season"]),
            has_races=bool(row["has_races"]),
            has_sprints=bool(row["has_sprints"]),
            min_round=int(row["min_round"]),
            max_round=int(row["max_round"]),
        )
        for _, row in df.iterrows()
    ]
    return SeasonsResponse(seasons=seasons)


@router.get("/races", response_model=List[RaceMeta])
def races(season: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    """
    Return ordered races for a given season derived from gold.race_winner_top3.
    """
    if not _table_exists(db, "gold", "race_winner_top3"):
        raise HTTPException(
            status_code=500,
            detail="gold.race_winner_top3 not found; rebuild gold tables first.",
        )

    sql = """
    SELECT DISTINCT season, round, grand_prix_slug
    FROM gold.race_winner_top3
    WHERE season = ?
    ORDER BY round
    """
    try:
        df = db.execute(sql, [season]).fetchdf()
    except duckdb.Error as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load races: {exc}") from exc

    return [
        RaceMeta(season=int(row["season"]), round=int(row["round"]), grand_prix_slug=str(row["grand_prix_slug"]))
        for _, row in df.iterrows()
    ]
