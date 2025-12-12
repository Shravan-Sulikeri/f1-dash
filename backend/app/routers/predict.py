import json
from pathlib import Path
from typing import Any, Dict, List

import duckdb
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException

WAREHOUSE = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"
ARTIFACT_DIR = Path("/Volumes/SAMSUNG/apps/f1-dash/ml_artifacts")

router = APIRouter()


def _load_model(name: str):
    model_path = ARTIFACT_DIR / f"{name}.joblib"
    meta_path = ARTIFACT_DIR / f"{name}.json"
    if not model_path.exists() or not meta_path.exists():
        raise FileNotFoundError(f"Missing artifact {model_path} or {meta_path}")
    model = joblib.load(model_path)
    with open(meta_path) as f:
        meta = json.load(f)
    features = meta.get("feature_list", [])
    return model, features


def _get_features_df(season: int, round_num: int) -> pd.DataFrame:
    con = duckdb.connect(WAREHOUSE)
    query = """
    SELECT *
    FROM features.race_win_training_enriched
    WHERE season = ? AND round = ?
    """
    return con.execute(query, [season, round_num]).fetchdf()


def _prepare_X(df: pd.DataFrame, feature_list: List[str]) -> pd.DataFrame:
    missing = [c for c in feature_list if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")
    X = df[feature_list].copy()
    return X.fillna(0)


@router.get("/races/{season}/{round}/predictions")
def race_predictions(season: int, round: int) -> Dict[str, Any]:
    try:
        win_model, win_features = _load_model("race_win_best")
        top3_model, top3_features = _load_model("race_top3_best")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    df = _get_features_df(season, round)
    if df.empty:
        raise HTTPException(status_code=404, detail="No feature rows for this race")

    X_win = _prepare_X(df, win_features)
    X_top = _prepare_X(df, top3_features)
    p_win = win_model.predict_proba(X_win)[:, 1]
    p_top3 = top3_model.predict_proba(X_top)[:, 1]

    df = df.assign(p_win=p_win, p_top3=p_top3)
    df_sorted = df.sort_values("p_win", ascending=False)
    winner_row = df_sorted.iloc[0]
    top3_rows = df.sort_values("p_top3", ascending=False).head(3)

    field = [
        {
            "driver_code": r.driver_code,
            "driver_name": r.driver_name,
            "team_name": r.team_name,
            "grid_position": r.grid_position,
            "p_win": float(r.p_win),
            "p_top3": float(r.p_top3),
        }
        for _, r in df.iterrows()
    ]

    return {
        "season": season,
        "round": round,
        "grand_prix_slug": df.grand_prix_slug.iloc[0],
        "winner": {
            "driver_code": winner_row.driver_code,
            "driver_name": winner_row.driver_name,
            "proba": float(winner_row.p_win),
        },
        "top3": [
            {
                "driver_code": r.driver_code,
                "driver_name": r.driver_name,
                "proba": float(r.p_top3),
                "rank": i + 1,
            }
            for i, (_, r) in enumerate(top3_rows.iterrows())
        ],
        "field": field,
    }


@router.get("/races/next/predictions")
def next_race_predictions() -> Dict[str, Any]:
    # Simplified: choose the latest season/round available in features
    con = duckdb.connect(WAREHOUSE)
    latest = con.execute(
        "SELECT season, MAX(round) AS round FROM features.race_win_training_enriched GROUP BY season ORDER BY season DESC LIMIT 1"
    ).fetchone()
    if not latest:
        raise HTTPException(status_code=404, detail="No races available")
    season, round_num = latest
    return race_predictions(int(season), int(round_num))
