from fastapi import APIRouter, Depends, HTTPException, Query
import duckdb

from ..deps import get_db

router = APIRouter(tags=["analytics:pace"])


def _ensure_gold_exists(db: duckdb.DuckDBPyConnection):
    exists = (
        db.execute(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'gold' AND table_name = 'driver_session_summary'
            """
        ).fetchone()
        is not None
    )
    if not exists:
        raise HTTPException(
            status_code=500,
            detail="gold.driver_session_summary does not exist; run gold build first.",
        )


@router.get("/session")
def pace_session(
    season: int = Query(..., description="Season (year)"),
    round: int = Query(..., description="Round number"),
    session_code: str = Query(..., description="Session code, e.g., Q, R, FP1"),
    db: duckdb.DuckDBPyConnection = Depends(get_db),
):
    _ensure_gold_exists(db)
    # TODO: If median_lap_duration/avg_lap_duration are absent, return them as NULL.
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
    df = db.execute(sql, [season, round, session_code]).fetchdf()
    return df.to_dict(orient="records")
