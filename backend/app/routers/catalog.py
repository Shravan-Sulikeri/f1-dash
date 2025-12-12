from fastapi import APIRouter, Depends, HTTPException
import duckdb

from ..deps import get_db

router = APIRouter()


def _table_exists(con: duckdb.DuckDBPyConnection, schema: str, table: str) -> bool:
    sql = """
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = ? AND table_name = ?
    """
    return con.execute(sql, [schema, table]).fetchone() is not None


@router.get("/seasons")
def get_seasons(db: duckdb.DuckDBPyConnection = Depends(get_db)):
    # Prefer gold.driver_session_summary if available
    if _table_exists(db, "gold", "driver_session_summary"):
        sql = "SELECT DISTINCT season FROM gold.driver_session_summary ORDER BY season ASC LIMIT 200"
    elif _table_exists(db, "silver", "laps"):
        sql = "SELECT DISTINCT season FROM silver.laps ORDER BY season ASC LIMIT 200"
    else:
        raise HTTPException(status_code=500, detail="No suitable table to derive seasons.")
    seasons = [row[0] for row in db.execute(sql).fetchall()]
    return seasons


@router.get("/calendar/{season}")
def get_calendar(season: int, db: duckdb.DuckDBPyConnection = Depends(get_db)):
    if not _table_exists(db, "gold", "driver_session_summary"):
        raise HTTPException(
            status_code=500,
            detail="gold.driver_session_summary does not exist; cannot build calendar.",
        )
    sql = """
    SELECT DISTINCT
      season,
      round,
      grand_prix_slug,
      session_code
    FROM gold.driver_session_summary
    WHERE season = ?
    ORDER BY round, session_code
    LIMIT 1000
    """
    rows = db.execute(sql, [season]).fetchdf()
    return rows.to_dict(orient="records")
