#!/usr/bin/env python3
"""
Build the predictions.race_win table by inference on the training data.
Creates predictions for all rows in the gold.race_winner_top3 table for 2023 and 2024.
"""
import logging
from pathlib import Path
import json
import duckdb
import joblib
import numpy as np
import pandas as pd

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
WAREHOUSE_PATH = BASE_DIR / "warehouse" / "f1_openf1.duckdb"
MODEL_PATH = BASE_DIR / "ml_artifacts" / "race_win_logreg.joblib"
META_PATH = BASE_DIR / "ml_artifacts" / "race_win_logreg.json"

def load_feature_cols() -> list[str]:
    """Read feature column list from the model metadata."""
    if META_PATH.exists():
        try:
            meta = json.loads(META_PATH.read_text())
            feats = meta.get("feature_cols")
            if isinstance(feats, list) and feats:
                return [str(f) for f in feats]
        except Exception as e:
            logging.warning(f"Could not load feature columns from {META_PATH}: {e}")
    
    # Fallback feature set
    return [
        "grid_position",
        "grid_position_norm",
        "driver_points_pre",
        "team_points_pre",
        "track_temp_c",
        "rain_probability",
        "starting_compound_index",
        "driver_avg_finish_last_3",
        "driver_points_last_3",
        "team_points_last_3",
        "driver_track_avg_finish_last_3_at_gp",
        "driver_track_points_last_3_at_gp",
        "team_track_points_last_3_at_gp",
    ]

def softmax(arr: np.ndarray) -> np.ndarray:
    """Compute softmax across races (axis 0) per driver."""
    arr = np.nan_to_num(arr, nan=0.0)
    arr = arr - np.max(arr, axis=0, keepdims=True)
    exp = np.exp(arr)
    denom = exp.sum(axis=0, keepdims=True)
    denom = np.where(denom == 0, 1, denom)
    return exp / denom

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logger = logging.getLogger("build_predictions")

    if not MODEL_PATH.exists():
        logger.error(f"Model not found at {MODEL_PATH}")
        return

    logger.info(f"Loading model from {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    feature_cols = load_feature_cols()
    logger.info(f"Feature columns: {feature_cols}")

    logger.info(f"Connecting to {WAREHOUSE_PATH}")
    con = duckdb.connect(str(WAREHOUSE_PATH))

    # Load the training enriched data for both seasons
    logger.info("Loading training data...")
    df = con.execute("""
        SELECT *
        FROM features.race_win_training_enriched
        WHERE season IN (2023, 2024)
        ORDER BY season, round
    """).df()
    logger.info(f"Loaded {len(df)} rows")

    # Fill NaN with 0 for all feature columns
    for col in feature_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0.0)
        else:
            logger.warning(f"Feature column {col} not found in data")
            df[col] = 0.0

    # Build feature matrix
    X = df[feature_cols].astype(float).values
    logger.info(f"Feature matrix shape: {X.shape}")

    # Generate predictions
    logger.info("Running model inference...")
    pred_proba = model.predict_proba(X)[:, 1]
    df['pred_win_proba'] = pred_proba

    # Compute softmax by race
    logger.info("Computing softmax probabilities by race...")
    df['pred_win_proba_softmax'] = 0.0
    for (season, round_num), group in df.groupby(['season', 'round']):
        indices = group.index
        race_probs = df.loc[indices, 'pred_win_proba'].values.reshape(-1, 1)
        softmax_probs = softmax(race_probs).flatten()
        df.loc[indices, 'pred_win_proba_softmax'] = softmax_probs

    # Select relevant columns for the prediction table
    output_cols = [
        'season', 'round', 'grand_prix_slug', 'driver_number', 'driver_name',
        'driver_code', 'team_name', 'grid_position', 'grid_position_norm',
        'driver_points_pre', 'team_points_pre', 'track_temp_c', 'rain_probability',
        'driver_avg_finish_last_3', 'driver_points_last_3', 'team_points_last_3',
        'driver_track_avg_finish_last_3_at_gp', 'driver_track_points_last_3_at_gp',
        'team_track_points_last_3_at_gp', 'target_win_race', 'pred_win_proba',
        'pred_win_proba_softmax'
    ]

    # Check which columns exist
    available_cols = [c for c in output_cols if c in df.columns]
    df_out = df[available_cols].copy()

    # Create predictions schema if it doesn't exist
    logger.info("Creating predictions schema...")
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS predictions")
    except Exception as e:
        logger.warning(f"Schema may already exist: {e}")

    # Drop the old table if it exists
    logger.info("Dropping old predictions.race_win table if exists...")
    try:
        con.execute("DROP TABLE IF EXISTS predictions.race_win")
    except Exception as e:
        logger.warning(f"Table may not exist: {e}")

    # Write predictions to the warehouse
    logger.info("Writing predictions table...")
    con.register('pred_df', df_out)
    con.execute("""
        CREATE TABLE predictions.race_win AS
        SELECT * FROM pred_df
    """)
    
    # Verify
    result = con.execute("""
        SELECT season, COUNT(*) as n_rows, COUNT(DISTINCT round) as n_races
        FROM predictions.race_win
        GROUP BY season
        ORDER BY season
    """).fetchall()

    logger.info("Predictions table created successfully:")
    for row in result:
        logger.info(f"  Season {row[0]}: {row[1]} rows, {row[2]} races")

    con.close()
    logger.info("Done!")

if __name__ == "__main__":
    main()
