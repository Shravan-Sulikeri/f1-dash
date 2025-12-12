from pathlib import Path as PathLib
from typing import Any, Dict, List, Optional, Sequence, Tuple
import re
from datetime import datetime

import duckdb
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import glob

try:
    import fastf1  # type: ignore
except ImportError:
    fastf1 = None

DB_PATH = PathLib(__file__).resolve().parent.parent / "warehouse" / "f1_openf1.duckdb"
FASTF1_CACHE = PathLib(__file__).resolve().parent.parent / ".fastf1cache"
FASTF1_CACHE_DIR = PathLib(__file__).resolve().parent.parent / "fastf1_cache"
BRONZE_DIR = PathLib(__file__).resolve().parent.parent / "bronze"
ML_ARTIFACTS_DIR = PathLib(__file__).resolve().parent.parent / "ml_artifacts"
RACE_WIN_MODEL_PATH = ML_ARTIFACTS_DIR / "race_win_full.joblib"
RACE_WIN_META_PATH = ML_ARTIFACTS_DIR / "race_win_full.json"
RF_POSITION_MODEL_PATH = ML_ARTIFACTS_DIR / "rf_position_model.joblib"
RF_POSITION_META_PATH = ML_ARTIFACTS_DIR / "rf_position_model.json"
RF_POSITION_FEATS_PATH = ML_ARTIFACTS_DIR / "rf_position_features.parquet"


app = FastAPI(
    title="F1 Predictions API",
    version="0.1.0",
    description="Read-only API for OpenF1 race win predictions backed by DuckDB",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def connect_ro() -> duckdb.DuckDBPyConnection:
    """Create a read-only DuckDB connection to the warehouse."""
    if not DB_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Warehouse not found at {DB_PATH}")
    try:
        return duckdb.connect(str(DB_PATH), read_only=True)
    except TypeError:
        # Fallback for duckdb versions without read_only arg
        return duckdb.connect(str(DB_PATH))


def fetch_fastf1(sql: str, params: Sequence[Any] | None = None) -> List[Dict[str, Any]]:
    """Execute a DuckDB query against the warehouse (fastf1 tables)."""
    params = params or []
    con = connect_ro()
    try:
        cur = con.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        con.close()


def fetch_rows(sql: str, params: Sequence[Any] | None = None) -> List[Dict[str, Any]]:
    """Execute a query and return rows as list of dicts."""
    params = params or []
    con = connect_ro()
    try:
        cur = con.execute(sql, params)
        columns = [col[0] for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        con.close()


def read_bronze(sql: str, params: Sequence[Any] | None = None) -> List[Dict[str, Any]]:
    """Run a DuckDB query against Parquet in the bronze folder."""
    params = params or []
    if not BRONZE_DIR.exists():
        raise HTTPException(status_code=500, detail=f"Bronze directory not found at {BRONZE_DIR}")
    con = duckdb.connect(":memory:")
    try:
        cur = con.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]
    except duckdb.Error as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        con.close()


def get_table_columns(con: duckdb.DuckDBPyConnection, table: str) -> set[str]:
    info = con.execute(f"PRAGMA table_info('{table}')").fetchall()
    return {row[1] for row in info}


# Driver code to name mapping
DRIVER_CODE_NAMES = {
    "VER": "Max Verstappen",
    "HAM": "Lewis Hamilton",
    "SAI": "Carlos Sainz",
    "LEC": "Charles Leclerc",
    "NOR": "Lando Norris",
    "PIA": "Oscar Piastri",
    "RUS": "George Russell",
    "ALO": "Fernando Alonso",
    "STR": "Lance Stroll",
    "ALB": "Alexander Albon",
    "BOT": "Valtteri Bottas",
    "OCO": "Esteban Ocon",
    "GAS": "Pierre Gasly",
    "VAN": "Stoffel Vandoorne",
    "RIC": "Daniel Ricciardo",
    "TSU": "Yuki Tsunoda",
    "ZHO": "Guanyu Zhou",
    "HUL": "Nico Hulkenberg",
    "BOR": "Gabriel Bortoleto",
    "MAG": "Kevin Magnussen",
    "DOO": "Jack Doohan",
    "LAW": "Liam Lawson",
    "BEA": "Oliver Bearman",
    "PER": "Sergio Perez",
    "ANT": "Kimi Antonelli",
    "COL": "Franco Colapinto",
    "RAI": "Kimi Räikkönen",
    "GRO": "Romain Grosjean",
    "KVY": "Daniil Kvyat",
    "GIO": "Antonio Giovinazzi",
    "KUB": "Robert Kubica",
    "HAR": "Brendon Hartley",
    "ERI": "Marcus Ericsson",
    "VET": "Sebastian Vettel",
    "MAS": "Max Verstappen",
    "BIS": "Jolyon Palmer",
    "CAR": "José María López",
}


def get_driver_name(driver_code: str | None) -> str:
    """Get full driver name from code, or return code as fallback."""
    if not driver_code:
        return ""
    name = DRIVER_CODE_NAMES.get(driver_code.upper())
    return name or driver_code


_race_win_model: Any | None = None
_race_win_features: List[str] | None = None
_rf_position_model: Any | None = None
_rf_position_features: Optional[pd.DataFrame] = None
_rf_position_feature_cols: List[str] | None = None


def get_race_win_model() -> Tuple[Any, List[str]]:
    """Lazy-load the race_win_logreg pipeline and its feature list."""
    global _race_win_model, _race_win_features
    if _race_win_model is None:
        if not RACE_WIN_MODEL_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"Race win model artefact not found at {RACE_WIN_MODEL_PATH}",
            )
        _race_win_model = joblib.load(RACE_WIN_MODEL_PATH)

    if _race_win_features is None:
        if RACE_WIN_META_PATH.exists():
            import json

            meta = json.loads(RACE_WIN_META_PATH.read_text())
            # Try both 'feature_list' (new format) and 'feature_cols' (old format)
            feats = meta.get("feature_list") or meta.get("feature_cols") or []
            if isinstance(feats, list) and feats:
                _race_win_features = [str(f) for f in feats]
        if _race_win_features is None:
            # Fallback to the minimal scenario feature list
            # (kept in sync with generate_race_predictions.py).
            _race_win_features = ["grid_position", "rain_probability", "starting_compound_index"]
    return _race_win_model, _race_win_features


def get_rf_position_model() -> Tuple[Any, List[str]]:
    """Lazy-load the RF position regressor and its feature column list."""
    global _rf_position_model, _rf_position_feature_cols
    if _rf_position_model is None:
        if not RF_POSITION_MODEL_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"RF position model artefact not found at {RF_POSITION_MODEL_PATH}",
            )
        _rf_position_model = joblib.load(RF_POSITION_MODEL_PATH)

    if _rf_position_feature_cols is None:
        if RF_POSITION_META_PATH.exists():
            import json

            meta = json.loads(RF_POSITION_META_PATH.read_text())
            feats = meta.get("feature_cols") or []
            if isinstance(feats, list) and feats:
                _rf_position_feature_cols = [str(f) for f in feats]
        if _rf_position_feature_cols is None:
            # Fallback to the feature list used in train_fastf1_rf_position.py
            _rf_position_feature_cols = [
                "grid_position",
                "driver_races_so_far",
                "driver_avg_finish_prev",
                "team_races_so_far",
                "team_avg_finish_prev",
                "circuit_avg_finish_prev",
            ]
    return _rf_position_model, _rf_position_feature_cols


def get_rf_position_features() -> pd.DataFrame:
    """Load engineered FastF1 RF features from Parquet."""
    global _rf_position_features
    if _rf_position_features is None:
        if not RF_POSITION_FEATS_PATH.exists():
            raise HTTPException(
                status_code=500,
                detail=f"RF position features parquet not found at {RF_POSITION_FEATS_PATH}",
            )
        _rf_position_features = pd.read_parquet(RF_POSITION_FEATS_PATH)
    return _rf_position_features


def pretty_grand_prix(slug: str) -> str:
    """Convert a slug to a display-friendly GP name."""
    if not slug:
        return ""
    words = slug.replace("-", " ").split()
    pretty_words: List[str] = []
    for w in words:
        if w.lower() in {"gp"}:
            pretty_words.append(w.upper())
        elif w.lower() == "usa":
            pretty_words.append("USA")
        else:
            pretty_words.append(w.capitalize())
    name = " ".join(pretty_words)
    if "grand" in name.lower():
        name = name.replace("grand", "Grand").replace("prix", "Prix")
    return name


def get_cached_seasons() -> List[int]:
    """Get available seasons from FastF1 cache."""
    if not FASTF1_CACHE_DIR.exists():
        return []
    seasons = []
    for year_dir in sorted(FASTF1_CACHE_DIR.iterdir()):
        if year_dir.is_dir() and year_dir.name.isdigit():
            seasons.append(int(year_dir.name))
    return seasons


def get_cached_races(season: int) -> List[Dict[str, Any]]:
    """Extract race data from FastF1 cache directories.
    
    Cache structure: fastf1_cache/YYYY/YYYY-MM-DD_Event_Name/
    """
    season_dir = FASTF1_CACHE_DIR / str(season)
    if not season_dir.exists():
        return []
    
    races: List[Dict[str, Any]] = []
    round_num = 1
    
    # Parse cached event directories
    for event_dir in sorted(season_dir.iterdir()):
        if not event_dir.is_dir():
            continue
        
        # Parse directory name: YYYY-MM-DD_Event_Name
        dir_name = event_dir.name
        parts = dir_name.split("_", 1)
        if len(parts) < 2:
            continue
        
        date_str = parts[0]  # YYYY-MM-DD
        event_name = "_".join(parts[1:])  # Event Name (with underscores)
        
        # Convert to slug
        slug = event_name.lower().replace(" ", "-").replace("_", "-")
        
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        
        races.append({
            "season": season,
            "round": round_num,
            "grand_prix_slug": slug,
            "display_name": event_name.replace("_", " "),
            "date_start": event_date.isoformat(),
            "display_round": round_num,
        })
        round_num += 1
    
    return races


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/meta/seasons")
def list_seasons() -> Dict[str, List[int]]:
    # Try to get from bronze first
    sql = f"""
    SELECT DISTINCT season
    FROM read_parquet('{BRONZE_DIR}/sessions/season=*/round=*/grand_prix=*/session=*/part-*.parquet')
    ORDER BY season
    """
    try:
        rows = read_bronze(sql)
        seasons = sorted(set([int(r["season"]) for r in rows]))
    except Exception:
        seasons = []
    
    # Add cached seasons if available
    cached_seasons = get_cached_seasons()
    all_seasons = sorted(set(seasons + cached_seasons))
    
    # Fallback to fastf1.session_result in warehouse if bronze is empty
    if not all_seasons:
        try:
            fastf1_rows = fetch_fastf1("SELECT DISTINCT season FROM fastf1.session_result ORDER BY season")
            all_seasons = [int(r["season"]) for r in fastf1_rows]
        except Exception:
            all_seasons = []

    if not all_seasons:
        raise HTTPException(status_code=404, detail="Not found")
    return {"seasons": all_seasons}


@app.get("/api/meta/races")
def list_races(season: int = Query(..., description="Season (e.g. 2023, 2024)")) -> List[Dict[str, Any]]:
    # Try to get from bronze first
    sql = f"""
    WITH races AS (
      SELECT DISTINCT
        season,
        round,
        grand_prix_slug,
        circuit_short_name AS circuit_name,
        date_start,
        date_end
      FROM read_parquet('{BRONZE_DIR}/sessions/season=*/round=*/grand_prix=*/session=*/part-*.parquet')
      WHERE session_code = 'R' AND season = {season}
    ),
    ordered AS (
      SELECT
        season,
        round,
        grand_prix_slug,
        circuit_name,
        date_start,
        date_end,
        ROW_NUMBER() OVER (ORDER BY round) AS display_round
      FROM races
    )
    SELECT * FROM ordered ORDER BY round
    """
    
    rows = []
    try:
        rows = read_bronze(sql)
    except Exception:
        pass
    
    # If no bronze data, try cached data
    if not rows:
        # Try warehouse fastf1 view with inferred rounds
        try:
            fastf1_rows = fetch_fastf1(
                """
                SELECT 
                  season, 
                  round_inferred AS round,
                  grand_prix_slug, 
                  MIN(grand_prix) AS circuit_name
                FROM fastf1.session_result_enriched
                WHERE session_code = 'R' AND season = ?
                GROUP BY season, round_inferred, grand_prix_slug
                ORDER BY round
                """,
                [season],
            )
            if fastf1_rows:
                return [
                    {
                        "season": int(r["season"]),
                        "round": int(r["round"]) if r.get("round") is not None else None,
                        "grand_prix_slug": r["grand_prix_slug"],
                        "display_name": pretty_grand_prix(r["grand_prix_slug"]),
                        "circuit_name": r.get("circuit_name"),
                        "date_start": None,
                        "date_end": None,
                        "display_round": int(r["round"]) if r.get("round") is not None else None,
                    }
                    for r in fastf1_rows
                ]
        except Exception:
            pass

        cached_races = get_cached_races(season)
        if cached_races:
            return cached_races
        raise HTTPException(status_code=404, detail="Not found")
    
    return [
        {
            "season": int(r["season"]),
            "round": int(r["round"]),
            "grand_prix_slug": r["grand_prix_slug"],
            "display_name": pretty_grand_prix(r["grand_prix_slug"]),
            "circuit_name": r["circuit_name"],
            "date_start": r["date_start"],
            "date_end": r["date_end"],
            "display_round": int(r["display_round"]),
        }
        for r in rows
    ]


@app.get("/api/races/{season}/{round}/drivers")
def list_drivers_for_race(
    season: int = Path(..., description="Season (e.g. 2024)"),
    round: int = Path(..., description="Round number"),
) -> List[Dict[str, Any]]:
    """Get list of drivers participating in a specific race."""
    sql = f"""
    SELECT DISTINCT
        driver_number
    FROM read_parquet('{BRONZE_DIR}/session_result/season=*/round=*/grand_prix=*/session=R/part-*.parquet')
    WHERE season = {season} AND round = {round}
    ORDER BY driver_number
    """
    
    rows = []
    try:
        rows = read_bronze(sql)
    except Exception:
        pass
    
    if not rows:
        raise HTTPException(status_code=404, detail="No drivers found for this race")
    
    return [
        {
            "driver_number": int(r["driver_number"]) if r["driver_number"] else None,
            "driver_code": f"DRV{int(r['driver_number'])}",  # Placeholder
            "driver_name": f"Driver {int(r['driver_number'])}",  # Placeholder
            "team_name": "TBD",
        }
        for r in rows
    ]


@app.get("/api/predictions/race_win")
def race_win_predictions(
    season: int = Query(..., description="Season (e.g. 2024)"),
    round: Optional[int] = Query(None, description="Round number"),
    driver_code: Optional[str] = Query(None, description="Driver code filter"),
    team_name: Optional[str] = Query(None, description="Team filter"),
    grand_prix_slug: Optional[str] = Query(None, description="Grand Prix slug filter"),
) -> List[Dict[str, Any]]:
    con = connect_ro()
    try:
        columns = get_table_columns(con, "predictions.race_win")

        required_columns = {"pred_win_proba", "season", "round", "grand_prix_slug"}
        if not required_columns.issubset(columns):
            raise HTTPException(status_code=500, detail="predictions.race_win missing required columns")

        desired_columns = [
            "season",
            "round",
            "grand_prix_slug",
            "driver_number",
            "driver_name",
            "driver_code",
            "team_name",
            "grid_position",
            "grid_position_norm",
            "driver_points_pre",
            "team_points_pre",
            "track_temp_c",
            "rain_probability",
            "driver_avg_finish_last_3",
            "driver_points_last_3",
            "team_points_last_3",
            "driver_track_avg_finish_last_3_at_gp",
            "driver_track_points_last_3_at_gp",
            "team_track_points_last_3_at_gp",
            "target_win_race",
            "pred_win_proba",
        ]

        if "pred_win_proba_softmax" in columns:
            desired_columns.append("pred_win_proba_softmax")

        select_cols = [col for col in desired_columns if col in columns]
        where_clauses = ["season = ?"]
        params: List[Any] = [season]

        if round is not None:
            where_clauses.append("round = ?")
            params.append(round)
        if driver_code:
            where_clauses.append("driver_code = ?")
            params.append(driver_code)
        if team_name:
            where_clauses.append("team_name = ?")
            params.append(team_name)
        if grand_prix_slug:
            where_clauses.append("grand_prix_slug = ?")
            params.append(grand_prix_slug)

        where_sql = " AND ".join(where_clauses)
        order_expr = "COALESCE(pred_win_proba_softmax, pred_win_proba)" if "pred_win_proba_softmax" in columns else "pred_win_proba"
        if round is not None:
            order_sql = f"ORDER BY {order_expr} DESC"
        else:
            order_sql = f"ORDER BY round ASC, {order_expr} DESC"

        query = f"SELECT {', '.join(select_cols)} FROM predictions.race_win WHERE {where_sql} {order_sql}"

        cur = con.execute(query, params)
        result_columns = [c[0] for c in cur.description]
        rows = [dict(zip(result_columns, row)) for row in cur.fetchall()]
    except duckdb.Error as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        con.close()

    if not rows:
        raise HTTPException(status_code=404, detail="Not found")

    return rows


@app.get("/api/predictions/race_win/summary")
def race_win_summary(
    season: Optional[int] = Query(None, description="Season for summary (defaults to latest)")
) -> Dict[str, Any]:
    con = connect_ro()
    try:
        if season is None:
            latest = con.execute("SELECT MAX(season) AS season FROM predictions.race_win").fetchone()
            if not latest or latest[0] is None:
                raise HTTPException(status_code=404, detail="Not found")
            season = int(latest[0])

        summary_row = con.execute(
            """
            WITH ranked AS (
              SELECT
                season,
                round,
                grand_prix_slug,
                driver_code,
                target_win_race,
                ROW_NUMBER() OVER (
                  PARTITION BY season, round
                  ORDER BY pred_win_proba DESC
                ) AS rank_in_race
              FROM predictions.race_win
              WHERE season = ?
            )
            SELECT
              COUNT(*) FILTER (WHERE target_win_race = 1) AS n_wins,
              AVG(CASE WHEN target_win_race = 1 AND rank_in_race = 1 THEN 1.0 ELSE 0.0 END) AS hit_at_1,
              AVG(CASE WHEN target_win_race = 1 AND rank_in_race <= 3 THEN 1.0 ELSE 0.0 END) AS hit_at_3
            FROM ranked;
            """,
            [season],
        ).fetchone()

        n_races_row = con.execute(
            "SELECT COUNT(DISTINCT round) AS n_races FROM predictions.race_win WHERE season = ?",
            [season],
        ).fetchone()
    except duckdb.Error as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        con.close()

    if summary_row is None or n_races_row is None:
        raise HTTPException(status_code=404, detail="Not found")

    n_wins, hit_at_1, hit_at_3 = summary_row
    return {
        "season": int(season),
        "n_races": int(n_races_row[0]) if n_races_row[0] is not None else 0,
        "n_wins": int(n_wins) if n_wins is not None else 0,
        "hit_at_1": float(hit_at_1) if hit_at_1 is not None else 0.0,
        "hit_at_3": float(hit_at_3) if hit_at_3 is not None else 0.0,
    }


class RaceWinScenarioRequest(BaseModel):
    season: int
    round: int
    driver_code: str
    grid_position: int
    rain_probability: float
    starting_compound_index: int


class RFPositionScenarioRequest(BaseModel):
    """Scenario inputs for RF position model."""

    season: int
    grand_prix: str
    driver_code: str
    grid_position: int
    team_name: Optional[str] = None


@app.post("/api/predict/race_win_scenario")
def race_win_scenario(body: RaceWinScenarioRequest) -> Dict[str, Any]:
    """Evaluate the race-win model for a single driver with tweaked grid/rain/tyre."""
    # Look up the baseline data from gold_fastf1.win_prediction_dataset
    con = connect_ro()
    try:
        # Try to find the exact race
        cur = con.execute(
            """
            SELECT *
            FROM gold_fastf1.win_prediction_dataset
            WHERE season = ? 
              AND round IS NOT NULL 
              AND CAST(round AS INTEGER) = ? 
              AND UPPER(driver_code) = UPPER(?)
            LIMIT 1
            """,
            [body.season, body.round, body.driver_code],
        )
        desc = cur.description
        if not desc:
            raise HTTPException(status_code=404, detail="Driver not found for this race")
        cols = [c[0] for c in desc]
        row = cur.fetchone()
        
        # If not found, use the most recent non-null round for this driver
        if row is None:
            cur = con.execute(
                """
                SELECT *
                FROM gold_fastf1.win_prediction_dataset
                WHERE season = ? 
                  AND round IS NOT NULL
                  AND UPPER(driver_code) = UPPER(?)
                ORDER BY round DESC
                LIMIT 1
                """,
                [body.season, body.driver_code],
            )
            row = cur.fetchone()
            
        if row is None:
            raise HTTPException(status_code=404, detail=f"No data found for {body.driver_code} in {body.season}")
            
        baseline = dict(zip(cols, row))
    except duckdb.Error as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        con.close()

    model, feature_cols = get_race_win_model()

    # Convert rainfall slider (0-1) to actual rainfall mm (0-10mm represents full range)
    rainfall_mm = float(body.rain_probability) * 10.0
    is_wet = 1.0 if float(body.rain_probability) > 0.5 else 0.0

    # Build feature vector, overriding scenario parameters
    feature_dict: Dict[str, float] = {}
    for col in feature_cols:
        if col == "grid_position":
            feature_dict[col] = float(body.grid_position)
        elif col == "max_rainfall_mm":
            # Map rain_probability (0-1) to rainfall in mm
            feature_dict[col] = rainfall_mm
        elif col == "is_wet_race":
            # Binary: wet if rain_probability > 50%
            feature_dict[col] = is_wet
        elif col == "starting_compound_index":
            feature_dict[col] = float(body.starting_compound_index)
        else:
            # For weather-condition features, swap between dry/wet based on scenario
            if is_wet > 0.5:
                # Scenario is wet: prefer wet-condition features
                if col.startswith("driver_dry_") and col.replace("driver_dry_", "driver_wet_") in feature_cols:
                    col_wet = col.replace("driver_dry_", "driver_wet_")
                    v = baseline.get(col_wet)
                elif col == "driver_avg_finish_dry" and "driver_avg_finish_wet" in feature_cols:
                    v = baseline.get("driver_avg_finish_wet")
                else:
                    v = baseline.get(col)
            else:
                # Scenario is dry: prefer dry-condition features
                if col.startswith("driver_wet_") and col.replace("driver_wet_", "driver_dry_") in feature_cols:
                    col_dry = col.replace("driver_wet_", "driver_dry_")
                    v = baseline.get(col_dry)
                elif col == "driver_avg_finish_wet" and "driver_avg_finish_dry" in feature_cols:
                    v = baseline.get("driver_avg_finish_dry")
                else:
                    v = baseline.get(col)
            feature_dict[col] = 0.0 if v is None else float(v)

    # Convert to DataFrame to preserve feature names for sklearn
    feature_frame = pd.DataFrame([feature_dict])
    feature_frame = feature_frame[feature_cols]  # Ensure correct column order
    
    # Replace inf/nan with 0
    feature_frame = feature_frame.replace([np.inf, -np.inf], 0).fillna(0)
    
    X = feature_frame
    
    try:
        proba = float(model.predict_proba(X)[0, 1])
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}")

    # Apply team capability boost for drivers on top teams
    # Top teams have demonstrated higher win rates; drivers new to top teams should
    # benefit from that team infrastructure
    team_name = baseline.get("team_name") or ""
    team_boost = 1.0
    if "red bull" in team_name.lower():
        team_boost = 1.5  # Red Bull has 22% historical win rate
    elif "mercedes" in team_name.lower():
        team_boost = 1.3  # Mercedes has 15% historical win rate
    elif "mclaren" in team_name.lower():
        team_boost = 1.2  # McLaren has 7.5% historical win rate
    elif "ferrari" in team_name.lower():
        team_boost = 1.1  # Ferrari has 4% historical win rate

    # Apply boost but cap at reasonable probability
    adjusted_proba = min(proba * team_boost, 0.95)

    # Get baseline prediction if it exists
    base_raw = float(baseline.get("pred_win_proba") or 0.0) if "pred_win_proba" in baseline else 0.0

    return {
        "season": body.season,
        "round": body.round,
        "driver_code": baseline.get("driver_code"),
        "driver_name": baseline.get("driver_name"),
        "team_name": baseline.get("team_name"),
        "base_pred_win_proba": base_raw,
        "base_pred_win_proba_softmax": None,
        "scenario_pred_win_proba": adjusted_proba,
    }


@app.post("/api/predict/rf_position_scenario")
def rf_position_scenario(body: RFPositionScenarioRequest) -> Dict[str, Any]:
    """
    Predict expected finishing position for a driver / circuit scenario using
    the FastF1 RandomForestRegressor trained on 2022–2024 races.

    This uses the engineered history features saved in
    ml_artifacts/rf_position_features.parquet and overrides the
    grid_position with the scenario value.
    """
    model, feature_cols = get_rf_position_model()
    feats = get_rf_position_features()

    # Slice driver / team / circuit history from engineered features.
    driver_mask = feats["driver_code"].str.upper() == body.driver_code.upper()
    driver_rows = feats[driver_mask]
    if driver_rows.empty:
        raise HTTPException(status_code=404, detail=f"No RF history found for driver {body.driver_code}")

    # If team_name not specified, use the most recent team in the history.
    team_name = body.team_name
    if not team_name:
        team_name = driver_rows.sort_values(["season", "round"])["team_name"].iloc[-1]

    team_rows = feats[feats["team_name"] == team_name]

    gp_mask = driver_rows["grand_prix"].str.lower() == body.grand_prix.lower()
    circuit_rows = driver_rows[gp_mask]

    # Build history-based aggregates (fallbacks if we have no circuit history yet).
    driver_races = float(driver_rows["driver_races_so_far"].max() or 0.0) if "driver_races_so_far" in driver_rows else float(len(driver_rows))
    driver_avg = float(driver_rows["driver_avg_finish_prev"].dropna().iloc[-1]) if "driver_avg_finish_prev" in driver_rows and driver_rows["driver_avg_finish_prev"].notna().any() else float(driver_rows["finish_position"].mean())

    team_races = float(team_rows["team_races_so_far"].max() or 0.0) if not team_rows.empty and "team_races_so_far" in team_rows else float(len(team_rows))
    team_avg = float(team_rows["team_avg_finish_prev"].dropna().iloc[-1]) if not team_rows.empty and "team_avg_finish_prev" in team_rows and team_rows["team_avg_finish_prev"].notna().any() else (float(team_rows["finish_position"].mean()) if not team_rows.empty else driver_avg)

    if not circuit_rows.empty and "circuit_avg_finish_prev" in circuit_rows and circuit_rows["circuit_avg_finish_prev"].notna().any():
        circuit_avg = float(circuit_rows["circuit_avg_finish_prev"].dropna().iloc[-1])
    elif not circuit_rows.empty:
        circuit_avg = float(circuit_rows["finish_position"].mean())
    else:
        circuit_avg = driver_avg

    # Construct feature vector in the same order as training.
    feature_values: List[float] = []
    for col in feature_cols:
        if col == "grid_position":
            value = float(body.grid_position)
        elif col == "driver_races_so_far":
            value = driver_races
        elif col == "driver_avg_finish_prev":
            value = driver_avg
        elif col == "team_races_so_far":
            value = team_races
        elif col == "team_avg_finish_prev":
            value = team_avg
        elif col == "circuit_avg_finish_prev":
            value = circuit_avg
        else:
            # Unknown feature; default to 0.0 to keep vector aligned.
            value = 0.0
        feature_values.append(float(value))

    X = np.array(feature_values, dtype=float).reshape(1, -1)
    try:
        pred_position = float(model.predict(X)[0])
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"RF position model inference failed: {exc}")

    return {
        "driver_code": body.driver_code,
        "team_name": team_name,
        "grand_prix": body.grand_prix,
        "grid_position": body.grid_position,
        "expected_finish_position": pred_position,
        "expected_finish_position_rounded": int(round(pred_position)),
        "feature_cols": feature_cols,
    }


@app.get("/api/monitor")
def monitor(season: Optional[int] = Query(None, description="Season to summarise for DE monitor")) -> Dict[str, Any]:
    """High-level pipeline/monitoring stats for the DE Monitor dashboard."""
    # Bronze ingestion metrics
    sessions_path = BRONZE_DIR / "sessions" / "season=*" / "round=*" / "grand_prix=*" / "session=*" / "part-*.parquet"
    result_path = BRONZE_DIR / "session_result" / "season=*" / "round=*" / "grand_prix=*" / "session=*" / "part-*.parquet"

    where_clause = "WHERE season IN (2023, 2024)"
    params: List[Any] = []
    if season is not None:
        where_clause = "WHERE season = ?"
        params = [season]

    bronze_sql = f"""
    WITH s AS (
      SELECT
        season,
        round,
        grand_prix_slug,
        session_code,
        session_name,
        date_start
      FROM read_parquet('{sessions_path}')
      {where_clause}
    ),
    agg AS (
      SELECT
        COUNT(DISTINCT season) AS n_seasons,
        COUNT(DISTINCT season || '-' || round::VARCHAR || '-' || grand_prix_slug || '-' || session_code) AS n_sessions
      FROM s
    ),
    latest AS (
      SELECT
        season,
        round,
        grand_prix_slug,
        session_code,
        session_name,
        date_start,
        ROW_NUMBER() OVER (ORDER BY date_start DESC) AS rn
      FROM s
    )
    SELECT
      agg.n_seasons,
      agg.n_sessions,
      l.season        AS latest_season,
      l.round         AS latest_round,
      l.grand_prix_slug AS latest_grand_prix_slug,
      l.session_code  AS latest_session_code,
      l.session_name  AS latest_session_name,
      l.date_start    AS latest_date_start
    FROM agg
    LEFT JOIN latest l ON l.rn = 1
    """

    bronze_rows = read_bronze(bronze_sql, params)
    bronze_info: Dict[str, Any] = {
        "n_sessions": 0,
        "n_seasons": 0,
        "latest_session": None,
        "n_result_rows": 0,
    }
    if bronze_rows:
        br = bronze_rows[0]
        bronze_info["n_sessions"] = int(br["n_sessions"] or 0)
        bronze_info["n_seasons"] = int(br["n_seasons"] or 0)
        if br["latest_season"] is not None:
            bronze_info["latest_session"] = {
                "season": int(br["latest_season"]),
                "round": int(br["latest_round"]) if br["latest_round"] is not None else None,
                "grand_prix_slug": br["latest_grand_prix_slug"],
                "session_code": br["latest_session_code"],
                "session_name": br["latest_session_name"],
                "date_start": br["latest_date_start"],
            }

    # Bronze session_result row count (used as a simple health metric)
    result_where = where_clause
    result_params = params
    result_sql = f"""
    SELECT COUNT(*) AS n_rows
    FROM read_parquet('{result_path}')
    {result_where}
    """
    result_rows = read_bronze(result_sql, result_params)
    if result_rows:
        bronze_info["n_result_rows"] = int(result_rows[0]["n_rows"] or 0)

    # Predictions / model metrics
    predictions_info: Dict[str, Any] = {"n_rows": 0}
    model_summary: Optional[Dict[str, Any]] = None

    try:
        # Base prediction row counts
        con = connect_ro()
        try:
            pred_where = ""
            pred_params: List[Any] = []
            if season is not None:
                pred_where = "WHERE season = ?"
                pred_params = [season]
            pred_row = con.execute(
                f"SELECT COUNT(*) AS n_rows FROM predictions.race_win {pred_where}",
                pred_params,
            ).fetchone()
            if pred_row:
                predictions_info["n_rows"] = int(pred_row[0] or 0)
        finally:
            con.close()
    except duckdb.Error as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=500, detail=str(exc))

    # Model performance summary (reuse the existing endpoint logic)
    try:
        model_summary = race_win_summary(season=season)
    except HTTPException:
        model_summary = None

    if model_summary is not None:
        predictions_info["season"] = model_summary.get("season")
        predictions_info["n_races"] = model_summary.get("n_races")

    return {
        "bronze": bronze_info,
        "predictions": predictions_info,
        "model": model_summary,
    }


@app.get("/")
def root() -> Dict[str, str]:
    return {"service": "f1-dash-api", "status": "ok"}


def _parquet_exists(path_pattern: str) -> bool:
    """Return True if any parquet files match the given glob pattern."""
    return bool(glob.glob(path_pattern))


def _read_weather(season: int, round: int, session_code: str) -> Dict[str, Any]:
    round_dir = f"round={round:02d}"
    path = BRONZE_DIR / "weather" / f"season={season}" / round_dir / "grand_prix=*" / f"session={session_code}" / "part-*.parquet"
    if not _parquet_exists(str(path)):
        return {"track_temp_c": None, "air_temp_c": None, "rain": None, "wind_speed": None, "humidity": None}
    sql = f"""
    SELECT
      AVG(track_temperature) AS track_temp_c,
      AVG(air_temperature) AS air_temp_c,
      MAX(rainfall) AS rain,
      AVG(wind_speed) AS wind_speed,
      AVG(humidity) AS humidity
    FROM read_parquet('{path}')
    """
    rows = read_bronze(sql)
    if not rows:
        return {"track_temp_c": None, "air_temp_c": None, "rain": None, "wind_speed": None, "humidity": None}
    r = rows[0]
    return {
        "track_temp_c": float(r["track_temp_c"]) if r["track_temp_c"] is not None else None,
        "air_temp_c": float(r["air_temp_c"]) if r["air_temp_c"] is not None else None,
        "rain": float(r["rain"]) if r["rain"] is not None else None,
        "wind_speed": float(r["wind_speed"]) if r["wind_speed"] is not None else None,
        "humidity": float(r["humidity"]) if r["humidity"] is not None else None,
    }


@app.get("/api/races/{season}/{round}/weather")
def race_weather(season: int, round: int, session_type: str = Query("R", description="Session code for weather, default R")) -> Dict[str, Any]:
    return _read_weather(season, round, session_type)


@app.get("/api/season/{season}/driver_pace")
def season_driver_pace(season: int) -> Dict[str, Any]:
    result_path = BRONZE_DIR / "session_result" / f"season={season}" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet"
    drivers_path = BRONZE_DIR / "drivers" / f"season={season}" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet"
    sql = f"""
    WITH res AS (
      SELECT round, driver_number, position
      FROM read_parquet('{result_path}')
      WHERE position IS NOT NULL
    ),
    drv AS (
      SELECT DISTINCT driver_number, name_acronym AS driver_code
      FROM read_parquet('{drivers_path}')
    )
    SELECT driver_code, round, position
    FROM res JOIN drv USING(driver_number)
    ORDER BY driver_code, round
    """
    
    try:
        rows = read_bronze(sql)
        pace_map: Dict[str, List[int]] = {}
        for r in rows:
            code = r["driver_code"]
            pos = r["position"]
            rnd = r["round"]
            if code is None or pos is None:
                continue
            pace_map.setdefault(code, []).append(int(pos))
        if pace_map:
            return {"pace": [{"driver_code": k, "positions": v} for k, v in pace_map.items()]}
    except Exception:
        pass
    
    # Fallback to warehouse fastf1 data
    try:
        fastf1_rows = fetch_fastf1(
            """
            SELECT driver_code, round_inferred as round, CAST(finish_position AS INT) AS position
            FROM fastf1.session_result_enriched
            WHERE season = ? AND session_code = 'R' AND finish_position IS NOT NULL
            ORDER BY driver_code, round_inferred
            """,
            [season],
        )
        pace_map_wh: Dict[str, List[int]] = {}
        for r in fastf1_rows:
            code = r.get("driver_code")
            pos = r.get("position")
            if code is None or pos is None:
                continue
            pace_map_wh.setdefault(code, []).append(int(pos))
        return {"pace": [{"driver_code": k, "positions": v} for k, v in pace_map_wh.items()]}
    except Exception:
        return {"pace": []}


@app.get("/api/races/{season}/{round}/sessions")
def race_sessions(season: int, round: int) -> Dict[str, Any]:
    sql = f"""
    SELECT season, round, grand_prix_slug, session_key, session_code, session_type, session_name
    FROM read_parquet('{BRONZE_DIR}/sessions/season=*/round=*/grand_prix=*/session=*/part-*.parquet')
    WHERE season = {season} AND round = {round}
    ORDER BY
      CASE session_code
        WHEN 'FP1' THEN 1
        WHEN 'FP2' THEN 2
        WHEN 'FP3' THEN 3
        WHEN 'SS' THEN 4
        WHEN 'SQ' THEN 5
        WHEN 'SPR' THEN 6
        WHEN 'Q' THEN 7
        WHEN 'R' THEN 8
        ELSE 9
      END,
      session_key
    """
    
    try:
        rows = read_bronze(sql)
        if rows:
            gp_slug = rows[0]["grand_prix_slug"]
            return {
                "season": season,
                "round": round,
                "grand_prix_slug": gp_slug,
                "sessions": [
                    {
                        "session_type": r["session_code"],
                        "name": r["session_name"],
                        "session_key": r["session_key"],
                    }
                    for r in rows
                ],
            }
    except Exception:
        pass
    
    # Fallback to warehouse fastf1 data
    try:
        fastf1_rows = fetch_fastf1(
            """
            SELECT DISTINCT
              season,
              round_inferred as round,
              grand_prix_slug,
              session_code,
              session_code as session_type
            FROM fastf1.session_result_enriched
            WHERE season = ? AND round_inferred = ?
            ORDER BY 
              CASE session_code
                WHEN 'FP1' THEN 1
                WHEN 'FP2' THEN 2
                WHEN 'FP3' THEN 3
                WHEN 'SS' THEN 4
                WHEN 'SQ' THEN 5
                WHEN 'SPR' THEN 6
                WHEN 'Q' THEN 7
                WHEN 'R' THEN 8
                ELSE 9
              END
            """,
            [season, round],
        )
        if fastf1_rows:
            gp_slug = fastf1_rows[0].get("grand_prix_slug", f"race-{round}")
            return {
                "season": season,
                "round": round,
                "grand_prix_slug": gp_slug,
                "sessions": [
                    {
                        "session_type": r.get("session_type"),
                        "name": f"{r.get('session_type')} Session",
                        "session_key": hash(f"{season}-{round}-{r.get('session_type')}"),
                    }
                    for r in fastf1_rows
                ],
            }
    except Exception:
        pass
    
    raise HTTPException(status_code=404, detail="Not found")


def _read_session_results(season: int, round: int, session_code: str) -> List[Dict[str, Any]]:
    round_dir = f"round={round:02d}"
    result_path = str(BRONZE_DIR / "session_result" / f"season={season}" / round_dir / "grand_prix=*" / f"session={session_code}" / "part-*.parquet")
    drivers_path = str(BRONZE_DIR / "drivers" / f"season={season}" / round_dir / "grand_prix=*" / f"session={session_code}" / "part-*.parquet")
    grid_path = str(BRONZE_DIR / "starting_grid" / f"season={season}" / round_dir / "grand_prix=*" / "session=Q" / "part-*.parquet")

    # If the parquet files for this session are missing, return an empty list so the caller can 404.
    if not _parquet_exists(result_path) or not _parquet_exists(drivers_path):
        return []

    # If grid data is missing, we can still return results, just without grid positions.
    grid_exists = _parquet_exists(grid_path)

    # Race sessions (R) include a points column in session_result parquet.
    # Practice / quali / sprint sessions typically do not. To avoid 500s
    # for those sessions, we use a NULL placeholder for points when the
    # column is absent (non‑race sessions).
    if session_code == "R":
        grid_join = "LEFT JOIN grid g USING(driver_number)" if grid_exists else ""
        grid_col = "g.grid_position" if grid_exists else "NULL AS grid_position"
        sql = f"""
        WITH result AS (
          SELECT * FROM read_parquet('{result_path}')
        ),
        drivers AS (
          SELECT driver_number, name_acronym AS driver_code, broadcast_name AS driver_name, team_name, team_colour, country_code
          FROM read_parquet('{drivers_path}')
        )
        {' ,grid AS (SELECT driver_number, position AS grid_position FROM read_parquet(\'' + grid_path + '\'))' if grid_exists else ''}
        SELECT
          r.position,
          d.driver_code,
          d.driver_name,
          d.team_name,
          d.team_colour,
          d.country_code,
          {grid_col},
          r.number_of_laps,
          r.points,
          r.duration,
          r.gap_to_leader,
          r.dnf,
          r.dns,
          r.dsq
        FROM result r
        LEFT JOIN drivers d USING(driver_number)
        {grid_join}
        ORDER BY r.position NULLS LAST, {grid_col} NULLS LAST, d.driver_name
        """
    else:
        grid_join = "LEFT JOIN grid g USING(driver_number)" if grid_exists else ""
        grid_col = "g.grid_position" if grid_exists else "NULL AS grid_position"
        sql = f"""
        WITH result AS (
          SELECT * FROM read_parquet('{result_path}')
        ),
        drivers AS (
          SELECT driver_number, name_acronym AS driver_code, broadcast_name AS driver_name, team_name, team_colour, country_code
          FROM read_parquet('{drivers_path}')
        )
        {' ,grid AS (SELECT driver_number, position AS grid_position FROM read_parquet(\'' + grid_path + '\'))' if grid_exists else ''}
        SELECT
          r.position,
          d.driver_code,
          d.driver_name,
          d.team_name,
          d.team_colour,
          d.country_code,
          {grid_col},
          r.number_of_laps,
          CAST(NULL AS DOUBLE) AS points,
          r.duration,
          r.gap_to_leader,
          r.dnf,
          r.dns,
          r.dsq
        FROM result r
        LEFT JOIN drivers d USING(driver_number)
        {grid_join}
        ORDER BY r.position NULLS LAST, {grid_col} NULLS LAST, d.driver_name
        """
    rows = read_bronze(sql)
    return [
        {
            "position": int(r["position"]) if r["position"] is not None else None,
            "driver_code": r["driver_code"],
            "driver_name": r["driver_name"],
            "team_name": r["team_name"],
            "team_colour": r.get("team_colour"),
            "country_code": r.get("country_code"),
            "grid": int(r["grid_position"]) if r["grid_position"] is not None else None,
            "laps": int(r["number_of_laps"]) if r["number_of_laps"] is not None else None,
            "points": float(r["points"]) if r["points"] is not None else None,
            "time_or_duration": r["duration"],
            "gap": r["gap_to_leader"],
            "status": (
                "DNF" if r["dnf"] else "DNS" if r["dns"] else "DSQ" if r["dsq"] else "Finished"
            ),
        }
        for r in rows
    ]


@app.get("/api/races/{season}/{round}/results")
def race_results(season: int, round: int, session_type: str = Query("R", description="Session code: R, Q, FP1, FP2, FP3, SPR, SQ")) -> List[Dict[str, Any]]:
    rows = _read_session_results(season, round, session_type)
    if rows:
        return rows

    # Fallback to warehouse fastf1 data if parquet not available
    try:
        fastf1_rows = fetch_fastf1(
            """
            SELECT
              CAST(finish_position AS INT) AS position,
              driver_code,
              driver_name,
              team_name,
              NULL AS team_colour,
              NULL AS country_code,
              CAST(grid_position AS INT) AS grid,
              NULL AS laps,
              CAST(points AS DOUBLE) AS points,
              time_retired AS time_or_duration,
              gap_to_leader AS gap,
              status
            FROM fastf1.session_result_enriched
            WHERE season = ? AND round_inferred = ? AND session_code = ?
            ORDER BY finish_position NULLS LAST, grid_position NULLS LAST, driver_name
            """,
            [season, round, session_type],
        )
        if fastf1_rows:
            return [
                {
                    "position": r.get("position"),
                    "driver_code": r.get("driver_code"),
                    "driver_name": r.get("driver_name") or get_driver_name(r.get("driver_code")),
                    "team_name": r.get("team_name"),
                    "team_colour": r.get("team_colour"),
                    "country_code": r.get("country_code"),
                    "grid": r.get("grid"),
                    "laps": r.get("laps"),
                    "points": r.get("points"),
                    "time_or_duration": r.get("time_or_duration"),
                    "gap": r.get("gap"),
                    "status": r.get("status") or "Finished",
                }
                for r in fastf1_rows
            ]
    except Exception:
        pass

    raise HTTPException(status_code=404, detail="Not found")


@app.get("/api/standings/drivers")
def driver_standings(season: int = Query(...), round: Optional[int] = Query(None, description="Optional round for race-specific standings")) -> List[Dict[str, Any]]:
    result_path = str(BRONZE_DIR / "session_result" / f"season={season}" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet")
    drivers_path = str(BRONZE_DIR / "drivers" / f"season={season}" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet")
    
    round_filter = ""
    if round is not None:
        round_filter = f"AND CAST(round AS INTEGER) <= {round}"
    
    sql = f"""
    WITH res AS (
      SELECT driver_number, points, position
      FROM read_parquet('{result_path}')
      WHERE 1=1 {round_filter}
    ),
    drv AS (
      SELECT DISTINCT driver_number, name_acronym AS driver_code, broadcast_name AS driver_name, team_name
      FROM read_parquet('{drivers_path}')
    )
    SELECT
      driver_code,
      driver_name,
      team_name,
      SUM(points) AS points,
      SUM(CASE WHEN position = 1 THEN 1 ELSE 0 END) AS wins,
      SUM(CASE WHEN position <= 3 THEN 1 ELSE 0 END) AS podiums
    FROM res
    JOIN drv USING(driver_number)
    GROUP BY 1,2,3
    ORDER BY points DESC
    """
    
    try:
        rows = read_bronze(sql)
        standings = [
            {
                "position": idx + 1,
                "driver_code": r["driver_code"],
                "driver_name": r["driver_name"],
                "team_name": r["team_name"],
                "points": float(r["points"]) if r["points"] is not None else 0.0,
                "wins": int(r["wins"] or 0),
                "podiums": int(r["podiums"] or 0),
            }
            for idx, r in enumerate(rows)
        ]
        if standings:
            return standings
    except Exception:
        pass

    # Fallback to warehouse fastf1 data
    round_clause = ""
    if round is not None:
        round_clause = "AND round_inferred <= CAST(? AS INTEGER)"
    try:
        params = [season]
        if round is not None:
            params.append(round)
        fastf1_rows = fetch_fastf1(
            f"""
            WITH res AS (
              SELECT driver_code, driver_name, team_name, COALESCE(points, 0) AS points, finish_position, round_inferred
              FROM fastf1.session_result_enriched
              WHERE session_code = 'R' AND season = ? {round_clause}
            )
            SELECT
              driver_code,
              ANY_VALUE(driver_name) AS driver_name,
              ANY_VALUE(team_name) AS team_name,
              SUM(points) AS points,
              SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) AS wins,
              SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) AS podiums
            FROM res
            GROUP BY driver_code
            ORDER BY points DESC
            """,
            params,
        )
        return [
            {
                "position": idx + 1,
                "driver_code": r.get("driver_code"),
                "driver_name": r.get("driver_name") or get_driver_name(r.get("driver_code")),
                "team_name": r.get("team_name"),
                "points": float(r.get("points") or 0.0),
                "wins": int(r.get("wins") or 0),
                "podiums": int(r.get("podiums") or 0),
            }
            for idx, r in enumerate(fastf1_rows)
        ]
    except Exception:
        return []


@app.get("/api/standings/constructors")
def constructor_standings(season: int = Query(...), round: Optional[int] = Query(None, description="Optional round for race-specific standings")) -> List[Dict[str, Any]]:
    result_path = str(BRONZE_DIR / "session_result" / f"season={season}" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet")
    drivers_path = str(BRONZE_DIR / "drivers" / f"season={season}" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet")
    
    round_filter = ""
    if round is not None:
        round_filter = f"AND CAST(round AS INTEGER) <= {round}"
    
    sql = f"""
    WITH res AS (
      SELECT driver_number, points
      FROM read_parquet('{result_path}')
      WHERE 1=1 {round_filter}
    ),
    drv AS (
      SELECT DISTINCT driver_number, team_name
      FROM read_parquet('{drivers_path}')
    )
    SELECT
      team_name,
      SUM(points) AS points
    FROM res
    JOIN drv USING(driver_number)
    GROUP BY 1
    ORDER BY points DESC
    """
    
    try:
        rows = read_bronze(sql)
        standings = [
            {
                "position": idx + 1,
                "team_name": r["team_name"],
                "points": float(r["points"]) if r["points"] is not None else 0.0,
            }
            for idx, r in enumerate(rows)
        ]
        if standings:
            return standings
    except Exception:
        pass

    round_clause = ""
    if round is not None:
        round_clause = "AND round_inferred <= CAST(? AS INTEGER)"
    try:
        params = [season]
        if round is not None:
            params.append(round)
        fastf1_rows = fetch_fastf1(
            f"""
            WITH res AS (
              SELECT team_name, COALESCE(points, 0) AS points, round_inferred
              FROM fastf1.session_result_enriched
              WHERE session_code = 'R' AND season = ? {round_clause}
            )
            SELECT team_name, SUM(points) AS points
            FROM res
            GROUP BY team_name
            ORDER BY points DESC
            """,
            params,
        )
        return [
            {
                "position": idx + 1,
                "team_name": r.get("team_name"),
                "points": float(r.get("points") or 0.0),
            }
            for idx, r in enumerate(fastf1_rows)
        ]
    except Exception:
        return []


@app.get("/api/standings/teams")
def team_standings(season: int = Query(...), round: Optional[int] = Query(None, description="Optional round for race-specific standings")) -> List[Dict[str, Any]]:
    """Get team standings with detailed information including drivers."""
    result_path = str(BRONZE_DIR / "session_result" / f"season={season}" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet")
    drivers_path = str(BRONZE_DIR / "drivers" / f"season={season}" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet")
    
    round_filter = ""
    if round is not None:
        round_filter = f"AND CAST(round AS INTEGER) <= {round}"
    
    sql = f"""
    WITH res AS (
      SELECT driver_number, points
      FROM read_parquet('{result_path}')
      WHERE 1=1 {round_filter}
    ),
    drv AS (
      SELECT DISTINCT driver_number, name_acronym AS driver_code, broadcast_name AS driver_name, team_name, team_colour, country_code
      FROM read_parquet('{drivers_path}')
    ),
    team_points AS (
      SELECT
        team_name,
        SUM(points) AS team_points,
        COUNT(DISTINCT driver_number) AS num_drivers
      FROM res
      JOIN drv USING(driver_number)
      GROUP BY 1
    ),
    team_drivers AS (
      SELECT
        team_name,
        driver_code,
        driver_name,
        SUM(points) AS driver_points,
        COUNT(*) AS races
      FROM res
      JOIN drv USING(driver_number)
      GROUP BY 1, 2, 3
      ORDER BY team_name, driver_points DESC
    )
    SELECT
      tp.team_name,
      tp.team_points,
      tp.num_drivers,
      td.driver_code,
      td.driver_name,
      td.driver_points,
      td.races
    FROM team_points tp
    LEFT JOIN team_drivers td ON tp.team_name = td.team_name
    ORDER BY tp.team_points DESC, td.driver_points DESC
    """
    
    try:
        rows = read_bronze(sql)
        teams: Dict[str, Dict[str, Any]] = {}
        for r in rows:
            team_name = r["team_name"]
            if team_name not in teams:
                teams[team_name] = {
                    "team_name": team_name,
                    "points": float(r["team_points"]) if r["team_points"] is not None else 0.0,
                    "drivers": []
                }
            
            if r["driver_code"] is not None:
                teams[team_name]["drivers"].append({
                    "driver_code": r["driver_code"],
                    "driver_name": r["driver_name"],
                    "points": float(r["driver_points"]) if r["driver_points"] is not None else 0.0,
                    "races": int(r["races"]) if r["races"] is not None else 0
                })

        team_list = sorted(teams.values(), key=lambda t: t["points"], reverse=True)
        standings = [
            {
                "position": idx + 1,
                "team_name": t["team_name"],
                "points": t["points"],
                "drivers": t["drivers"]
            }
            for idx, t in enumerate(team_list)
        ]
        if standings:
            return standings
    except Exception:
        pass

    # Fallback to warehouse fastf1 data
    round_clause = ""
    if round is not None:
        round_clause = "AND round_inferred <= CAST(? AS INTEGER)"
    try:
        params = [season]
        if round is not None:
            params.append(round)
        fastf1_rows = fetch_fastf1(
            f"""
            WITH res AS (
              SELECT team_name, driver_code, driver_name, COALESCE(points, 0) AS points, round_inferred
              FROM fastf1.session_result_enriched
              WHERE session_code = 'R' AND season = ? {round_clause}
            ),
            team_points AS (
              SELECT team_name, SUM(points) AS team_points
              FROM res
              GROUP BY team_name
            ),
            team_drivers AS (
              SELECT team_name, driver_code, ANY_VALUE(driver_name) AS driver_name, SUM(points) AS driver_points, COUNT(*) AS races
              FROM res
              GROUP BY team_name, driver_code
            )
            SELECT tp.team_name, tp.team_points, td.driver_code, td.driver_name, td.driver_points, td.races
            FROM team_points tp
            LEFT JOIN team_drivers td ON tp.team_name = td.team_name
            ORDER BY tp.team_points DESC, td.driver_points DESC
            """,
            params,
        )

        teams_wh: Dict[str, Dict[str, Any]] = {}
        for r in fastf1_rows:
            tname = r.get("team_name")
            if not tname:
                continue
            if tname not in teams_wh:
                teams_wh[tname] = {
                    "team_name": tname,
                    "points": float(r.get("team_points") or 0.0),
                    "drivers": []
                }
            if r.get("driver_code"):
                teams_wh[tname]["drivers"].append({
                    "driver_code": r.get("driver_code"),
                    "driver_name": r.get("driver_name") or get_driver_name(r.get("driver_code")),
                    "points": float(r.get("driver_points") or 0.0),
                    "races": int(r.get("races") or 0),
                })

        team_list_wh = sorted(teams_wh.values(), key=lambda t: t["points"], reverse=True)
        return [
            {
                "position": idx + 1,
                "team_name": t["team_name"],
                "points": t["points"],
                "drivers": t["drivers"],
            }
            for idx, t in enumerate(team_list_wh)
        ]
    except Exception:
        return []

@app.get("/api/telemetry")
def telemetry(
    season: int = Query(..., description="Season, e.g., 2024"),
    round: int = Query(..., description="Round number"),
    session_code: str = Query("R", description="Session code (R=Race, Q=Quali, S=Sprint)"),
    driver_code: Optional[str] = Query(None, description="Driver code to return telemetry for (defaults to winner)"),
) -> JSONResponse:
    if fastf1 is None:
        raise HTTPException(status_code=500, detail="fastf1 not installed on the server")

    FASTF1_CACHE.mkdir(exist_ok=True)
    fastf1.Cache.enable_cache(str(FASTF1_CACHE))

    try:
        session = fastf1.get_session(season, round, session_code)
        session.load()
    except Exception as exc:  # pragma: no cover - external API
        raise HTTPException(status_code=500, detail=f"FastF1 session load failed: {exc}")

    # Use race results to pick winner if driver_code not provided
    selected_driver = driver_code
    results_rows: List[Dict[str, Any]] = []
    try:
        if session.results is not None:
            for _, row in session.results.iterrows():
                results_rows.append(
                    {
                        "position": int(row.get("Position")) if row.get("Position") is not None else None,
                        "driver_code": row.get("Abbreviation") or row.get("DriverNumber"),
                        "driver_name": row.get("Driver") or "",
                        "team_name": row.get("TeamName") or row.get("Team"),
                        "status": row.get("Status"),
                        "points": row.get("Points"),
                        "grid_position": row.get("GridPosition"),
                        "time": row.get("Time") if isinstance(row.get("Time"), str) else None,
                    }
                )
            if not selected_driver and results_rows:
                results_sorted = sorted(
                    [r for r in results_rows if r["position"] is not None],
                    key=lambda r: r["position"],
                )
                if results_sorted:
                    selected_driver = results_sorted[0]["driver_code"]
    except Exception:
        results_rows = []

    # Fallback if still no driver
    if not selected_driver:
        selected_driver = session.results.iloc[0].Abbreviation if session.results is not None else None

    samples: List[Dict[str, Any]] = []
    try:
        if selected_driver:
            laps = session.laps.pick_driver(selected_driver)
            lap = laps.pick_fastest()
            tel = lap.get_telemetry()
            # downsample to keep payload light
            stride = max(1, int(len(tel) / 300))
            for _, row in tel.iloc[::stride].iterrows():
                samples.append(
                    {
                        "time_ms": float(row.get("Time").total_seconds() * 1000) if hasattr(row.get("Time"), "total_seconds") else None,
                        "distance": float(row.get("Distance")) if row.get("Distance") is not None else None,
                        "speed": float(row.get("Speed")) if row.get("Speed") is not None else None,
                        "throttle": float(row.get("Throttle")) if row.get("Throttle") is not None else None,
                        "brake": int(row.get("Brake")) if row.get("Brake") is not None else 0,
                        "n": float(row.get("n")) if row.get("n") is not None else None,
                        "x": float(row.get("X")) if row.get("X") is not None else None,
                        "y": float(row.get("Y")) if row.get("Y") is not None else None,
                    }
                )
    except Exception:
        samples = []

    # Weather summary (if available)
    rain = None
    track_temp = None
    try:
        weather_df = session.weather_data
        if weather_df is not None and not weather_df.empty:
            rain = float(weather_df["Rainfall"].max(skipna=True))
            track_temp = float(weather_df["TrackTemp"].mean(skipna=True))
    except Exception:
        rain = None
        track_temp = None

    return JSONResponse(
        {
            "season": season,
            "round": round,
            "session": session_code,
            "driver_code": selected_driver,
            "samples": samples,
            "results": results_rows,
            "weather": {"rain": rain, "track_temp_c": track_temp},
        }
    )
