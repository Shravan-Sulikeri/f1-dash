#!/usr/bin/env python3
"""
Generate F1 race outcome predictions using trained models.

Generates predictions for:
1. Race winner (top finisher at each race)
2. Podium finishers (top 3)
3. Both wet and dry conditions

Uses trained models from ml_artifacts/ and features from gold_fastf1.

Outputs predictions to gold_fastf1.race_predictions table.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import duckdb
import joblib
import numpy as np
import pandas as pd

WAREHOUSE_PATH = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"
ARTIFACT_DIR = Path("/Volumes/SAMSUNG/apps/f1-dash/ml_artifacts")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fastf1_predictions")


def load_model_and_metadata(model_prefix: str) -> Optional[Tuple]:
    """Load trained model and its metadata."""
    # Find the model file (could be various types, prefer fastf1 trained ones)
    model_files = list(ARTIFACT_DIR.glob(f"{model_prefix}_*.joblib"))
    
    if not model_files:
        logger.warning(f"No model found for {model_prefix}")
        return None
    
    # Sort by modified time to pick the freshest artifact
    model_files = sorted(model_files, key=lambda p: p.stat().st_mtime)
    model_path = model_files[-1]  # Take the most recently updated
    metadata_path = model_path.with_suffix('.json')
    
    try:
        model = joblib.load(model_path)
        with open(metadata_path) as f:
            metadata = json.load(f)
        logger.info(f"✓ Loaded {model_prefix} model from {model_path.name}")
        return model, metadata
    except Exception as e:
        logger.error(f"Failed to load model {model_prefix}: {e}")
        return None


def _feature_list_from_metadata(model, metadata: dict) -> List[str]:
    """Return feature list from metadata or model attributes."""
    cols = metadata.get("features") or metadata.get("feature_list") or metadata.get("feature_cols")
    if cols:
        return list(cols)
    if hasattr(model, "feature_names_in_"):
        return list(getattr(model, "feature_names_in_"))
    return []


def _ensure_feature_frame(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    """Ensure df contains all feature_cols, filling missing with zeros and ordering columns."""
    working = df.copy()
    for col in feature_cols:
        if col not in working.columns:
            working[col] = 0
    return working[feature_cols].replace([np.inf, -np.inf], 0).fillna(0)


def generate_predictions(con: duckdb.DuckDBPyConnection) -> Dict[str, pd.DataFrame]:
    """Generate race outcome predictions."""
    logger.info("Loading feature data from gold_fastf1...")
    
    df = con.execute("""
        SELECT * FROM gold_fastf1.race_prediction_features
        WHERE season >= 2024
    """).fetchdf()
    
    if len(df) == 0:
        logger.warning("No data found for predictions")
        return {}
    
    logger.info(f"Loaded {len(df)} records for prediction")
    
    # Load models
    logger.info("Loading trained models...")
    win_model_data = load_model_and_metadata("race_win")
    podium_model_data = load_model_and_metadata("race_podium")
    finish_model_data = load_model_and_metadata("race_finish")
    
    if not win_model_data:
        logger.error("Cannot proceed without race_win model")
        return {}
    
    win_model, win_metadata = win_model_data
    win_features = _feature_list_from_metadata(win_model, win_metadata)
    if not win_features:
        logger.error("No feature list found in model metadata; cannot generate predictions")
        return {}
    
    logger.info(f"Using {len(win_features)} features from trained model")
    
    # Prepare base feature frames for each model
    logger.info("Preparing features...")
    X_win = _ensure_feature_frame(df, win_features)
    
    # Generate predictions
    logger.info("Generating predictions...")
    predictions = df[["season", "round", "grand_prix_slug", "driver_code", "driver_name", 
                       "team_name", "grid_position"]].copy()
    
    # Win probability
    if hasattr(win_model, 'predict_proba'):
        try:
            proba = win_model.predict_proba(X_win)
            predictions["win_probability"] = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
        except:
            predictions["win_probability"] = win_model.decision_function(X_win)
    else:
        predictions["win_probability"] = win_model.decision_function(X_win)
    
    # Normalize to 0-1
    min_val = predictions["win_probability"].min()
    max_val = predictions["win_probability"].max()
    if max_val > min_val:
        predictions["win_probability"] = (predictions["win_probability"] - min_val) / (max_val - min_val)
    
    # Podium probability
    if podium_model_data:
        podium_model, podium_metadata = podium_model_data
        podium_features = _feature_list_from_metadata(podium_model, podium_metadata)
        X_podium = _ensure_feature_frame(df, podium_features) if podium_features else X_win
        if hasattr(podium_model, 'predict_proba'):
            try:
                proba = podium_model.predict_proba(X_podium)
                predictions["podium_probability"] = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
            except:
                predictions["podium_probability"] = podium_model.decision_function(X_podium)
        else:
            predictions["podium_probability"] = podium_model.decision_function(X_podium)
        
        min_val = predictions["podium_probability"].min()
        max_val = predictions["podium_probability"].max()
        if max_val > min_val:
            predictions["podium_probability"] = (predictions["podium_probability"] - min_val) / (max_val - min_val)
    else:
        predictions["podium_probability"] = predictions["win_probability"]
    
    # Finish probability
    if finish_model_data:
        finish_model, finish_metadata = finish_model_data
        finish_features = _feature_list_from_metadata(finish_model, finish_metadata)
        X_finish = _ensure_feature_frame(df, finish_features) if finish_features else X_win
        if hasattr(finish_model, 'predict_proba'):
            try:
                proba = finish_model.predict_proba(X_finish)
                predictions["finish_probability"] = proba[:, 1] if proba.shape[1] > 1 else proba[:, 0]
            except:
                predictions["finish_probability"] = finish_model.decision_function(X_finish)
        else:
            predictions["finish_probability"] = finish_model.decision_function(X_finish)
        
        min_val = predictions["finish_probability"].min()
        max_val = predictions["finish_probability"].max()
        if max_val > min_val:
            predictions["finish_probability"] = (predictions["finish_probability"] - min_val) / (max_val - min_val)
    else:
        predictions["finish_probability"] = predictions["win_probability"]
    
    # Add prediction timestamp
    predictions["prediction_generated_at"] = pd.Timestamp.now()
    
    return {
        "all_drivers": predictions,
        "by_race": predictions.groupby(["season", "round", "grand_prix_slug"]).apply(
            lambda x: x.sort_values("win_probability", ascending=False)
        ).reset_index(drop=True)
    }


def save_predictions(con: duckdb.DuckDBPyConnection, predictions: Dict[str, pd.DataFrame]) -> None:
    """Save predictions to DuckDB."""
    if not predictions:
        logger.warning("No predictions to save")
        return
    
    con.execute("CREATE SCHEMA IF NOT EXISTS gold_fastf1;")
    
    # Save all predictions
    con.execute("DROP TABLE IF EXISTS gold_fastf1.race_predictions;")
    con.from_df(predictions["all_drivers"]).create("gold_fastf1.race_predictions")
    logger.info(f"✓ Saved {len(predictions['all_drivers'])} predictions to gold_fastf1.race_predictions")
    
    # Create view for top 1, 3, 5 per race
    con.execute("""
        CREATE OR REPLACE VIEW gold_fastf1.race_win_predictions AS
        WITH ranked AS (
            SELECT
                season,
                round,
                grand_prix_slug,
                driver_code,
                driver_name,
                team_name,
                grid_position,
                win_probability,
                podium_probability,
                finish_probability,
                ROW_NUMBER() OVER (PARTITION BY season, round, grand_prix_slug 
                                   ORDER BY win_probability DESC) AS win_rank,
                ROW_NUMBER() OVER (PARTITION BY season, round, grand_prix_slug 
                                   ORDER BY podium_probability DESC) AS podium_rank
            FROM gold_fastf1.race_predictions
        )
        SELECT * FROM ranked WHERE win_rank <= 10;
    """)
    logger.info("✓ Created gold_fastf1.race_win_predictions view")


def generate_prediction_report(con: duckdb.DuckDBPyConnection) -> None:
    """Generate summary report of predictions."""
    try:
        summary = con.execute("""
            SELECT
                season,
                round,
                grand_prix_slug,
                COUNT(*) as drivers_in_race,
                MAX(win_probability) as max_win_prob,
                AVG(win_probability) as avg_win_prob,
                MAX(podium_probability) as max_podium_prob
            FROM gold_fastf1.race_predictions
            GROUP BY season, round, grand_prix_slug
            ORDER BY season DESC, round DESC
        """).fetchdf()
        
        logger.info("\n" + "="*80)
        logger.info("PREDICTION SUMMARY")
        logger.info("="*80)
        print(summary.to_string(index=False))
        logger.info("="*80 + "\n")
    except Exception as e:
        logger.warning(f"Could not generate summary: {e}")


def main() -> None:
    logger.info("F1 Race Prediction Generator")
    logger.info("=" * 80)
    
    con = duckdb.connect(WAREHOUSE_PATH)
    
    try:
        # Generate predictions
        predictions = generate_predictions(con)
        
        if predictions:
            # Save to database
            save_predictions(con, predictions)
            
            # Generate report
            generate_prediction_report(con)
            
            logger.info("✓ Prediction generation complete")
        else:
            logger.warning("No predictions generated")
    
    finally:
        con.close()


if __name__ == "__main__":
    main()
