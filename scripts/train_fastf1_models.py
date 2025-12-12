#!/usr/bin/env python3
"""
Train comprehensive F1 race outcome prediction models.

Uses gold_fastf1.race_prediction_features with 2018-2025 data including:
- Driver career & venue-specific performance
- Weather conditions & adaptation patterns
- Current season form
- Team capabilities
- Historical patterns at each venue

Trains separate models for:
1. Race winner prediction (target_win)
2. Podium prediction (target_podium)
3. Finish prediction (target_finish)

Uses ensemble methods (Logistic Regression, Random Forest, XGBoost) with validation
on 2023 data, testing on 2024 data, and holdout on 2025 data.

Saves best models to ml_artifacts/
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import duckdb
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None

WAREHOUSE_PATH = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"
ARTIFACT_DIR = Path("/Volumes/SAMSUNG/apps/f1-dash/ml_artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_fastf1_models")


def load_training_data(target_col: str) -> pd.DataFrame:
    """Load feature-engineered data from gold_fastf1."""
    con = duckdb.connect(WAREHOUSE_PATH)
    df = con.execute("""
        SELECT * FROM gold_fastf1.race_prediction_features
    """).fetchdf()
    con.close()
    # Include DNFs so finish prediction is not trained on only positives.
    return df


def split_by_season(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Split data by season for temporal validation."""
    splits = {
        "train": df[df["season"].between(2018, 2022)],
        "val": df[df["season"] == 2023],
        "test": df[df["season"] == 2024],
        "holdout": df[df["season"] == 2025],
    }
    return splits


def get_feature_columns(df: pd.DataFrame, target_col: str) -> List[str]:
    """Get list of feature columns, excluding targets and identifiers."""
    exclude = {
        target_col,
        "target_win",
        "target_podium",
        "target_finish",
        "finish_position",
        "points",
        "dnf",
        "driver_name",
        "team_name",
        "grand_prix_slug",
        "driver_code",
        "driver_number",
        "race_date",
        "season",
        "round",
    }
    
    # Include all numeric columns not in exclude list
    feature_cols = [
        c for c in df.columns
        if c not in exclude
        and pd.api.types.is_numeric_dtype(df[c])
    ]
    
    return sorted(feature_cols)


def prepare_features(df: pd.DataFrame, feature_cols: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """Prepare features with NaN handling."""
    X = df[feature_cols].fillna(0)
    
    # Replace infinite values
    X = X.replace([np.inf, -np.inf], 0)
    
    return X, feature_cols


def evaluate_model(model, X_train, y_train, X_val, y_val, val_df, target_col: str, model_name: str) -> Dict:
    """Evaluate model on validation set."""
    model.fit(X_train, y_train)
    
    try:
        val_proba = model.predict_proba(X_val)[:, 1] if hasattr(model, 'predict_proba') else model.decision_function(X_val)
    except:
        val_proba = model.predict(X_val)
    
    metrics = {}
    
    # ROC-AUC
    if len(np.unique(y_val)) > 1:
        metrics['roc_auc'] = roc_auc_score(y_val, val_proba)
    else:
        metrics['roc_auc'] = 0.0
    
    # Log loss
    try:
        metrics['log_loss'] = log_loss(y_val, val_proba, labels=[0, 1])
    except:
        metrics['log_loss'] = float('inf')
    
    # Accuracy
    val_pred = model.predict(X_val)
    metrics['accuracy'] = accuracy_score(y_val, val_pred)
    
    # Hit @ K metrics (per race)
    metrics['hit@1'] = hit_at_k(val_df, val_proba, target_col, k=1)
    metrics['hit@3'] = hit_at_k(val_df, val_proba, target_col, k=3)
    metrics['hit@5'] = hit_at_k(val_df, val_proba, target_col, k=5)
    
    logger.info(f"[{model_name}] val metrics: AUC={metrics['roc_auc']:.4f}, LL={metrics['log_loss']:.4f}, "
                f"Acc={metrics['accuracy']:.4f}, Hit@1={metrics['hit@1']:.4f}, Hit@3={metrics['hit@3']:.4f}")
    
    return metrics, val_proba


def hit_at_k(df: pd.DataFrame, proba: np.ndarray, target_col: str, k: int = 1) -> float:
    """Calculate hit rate at K per race."""
    df_tmp = df.copy()
    df_tmp["proba"] = proba
    
    hits = 0
    races = 0
    
    for _, race_group in df_tmp.groupby(["season", "round", "grand_prix_slug"]):
        races += 1
        race_group = race_group.sort_values("proba", ascending=False)
        
        true_codes = set(race_group[race_group[target_col] == 1]["driver_code"].unique())
        topk_codes = set(race_group.head(k)["driver_code"].unique())
        
        if true_codes & topk_codes:
            hits += 1
    
    return hits / races if races > 0 else 0.0


def train_prediction_task(df: pd.DataFrame, target_col: str, model_prefix: str):
    """Train models for a prediction task."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Training {model_prefix.upper()} prediction model")
    logger.info(f"{'='*60}")
    
    splits = split_by_season(df)
    feature_cols = get_feature_columns(df, target_col)
    
    logger.info(f"Features: {len(feature_cols)} columns")
    logger.info(f"Training set: {len(splits['train'])} records, {sum(splits['train'][target_col])} positives")
    logger.info(f"Validation set: {len(splits['val'])} records, {sum(splits['val'][target_col])} positives")
    logger.info(f"Test set: {len(splits['test'])} records, {sum(splits['test'][target_col])} positives")
    
    # Prepare training data
    X_train, _ = prepare_features(splits["train"], feature_cols)
    y_train = splits["train"][target_col].astype(int)
    
    X_val, _ = prepare_features(splits["val"], feature_cols)
    y_val = splits["val"][target_col].astype(int)
    
    # Define candidate models
    candidates = [
        ("logreg", Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=500, class_weight='balanced'))
        ])),
        ("rf", RandomForestClassifier(
            n_estimators=500,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )),
    ]
    
    if XGBClassifier:
        candidates.append(("xgb", XGBClassifier(
            n_estimators=500,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.8,
            scale_pos_weight=sum(y_train == 0) / sum(y_train == 1) if sum(y_train == 1) > 0 else 1,
            objective='binary:logistic',
            random_state=42,
            eval_metric='logloss',
            n_jobs=-1,
            verbosity=0
        )))
    
    # Train and evaluate candidates
    best_model = None
    best_metrics = None
    best_name = None
    
    for model_name, model in candidates:
        logger.info(f"\nTraining {model_name}...")
        try:
            metrics, _ = evaluate_model(
                model, X_train, y_train, X_val, y_val,
                splits["val"].assign(**{target_col: y_val}),
                target_col, model_name
            )
            
            if best_metrics is None or metrics['roc_auc'] > best_metrics['roc_auc']:
                best_model = model
                best_metrics = metrics
                best_name = model_name
        except Exception as e:
            logger.warning(f"Failed to train {model_name}: {e}")
    
    if best_model is None:
        logger.error(f"No model trained successfully for {model_prefix}")
        return None
    
    logger.info(f"\nBest model: {best_name}")
    
    # Retrain on train+val
    X_tv = pd.concat([X_train, X_val])
    y_tv = pd.concat([y_train, y_val])
    
    logger.info(f"Retraining {best_name} on train+val ({len(X_tv)} records)...")
    best_model.fit(X_tv, y_tv)
    
    # Evaluate on test
    X_test, _ = prepare_features(splits["test"], feature_cols)
    y_test = splits["test"][target_col].astype(int)
    
    if len(X_test) > 0:
        test_metrics, test_proba = evaluate_model(
            best_model, X_test, y_test, X_test, y_test,
            splits["test"].assign(**{target_col: y_test}),
            target_col, f"{best_name} (test)"
        )
    else:
        test_metrics = {}
        test_proba = np.array([])
    
    # Evaluate on holdout
    X_hold, _ = prepare_features(splits["holdout"], feature_cols)
    y_hold = splits["holdout"][target_col].astype(int)
    
    if len(X_hold) > 0:
        hold_metrics, hold_proba = evaluate_model(
            best_model, X_hold, y_hold, X_hold, y_hold,
            splits["holdout"].assign(**{target_col: y_hold}),
            target_col, f"{best_name} (holdout)"
        )
    else:
        hold_metrics = {}
        hold_proba = np.array([])
    
    # Save model
    model_path = ARTIFACT_DIR / f"{model_prefix}_{best_name}.joblib"
    joblib.dump(best_model, model_path)
    logger.info(f"✓ Saved model to {model_path}")
    
    # Save metadata
    metadata = {
        "model_type": best_name,
        "target": target_col,
        "features": feature_cols,
        "feature_count": len(feature_cols),
        "train_size": len(X_train),
        "val_size": len(X_val),
        "test_size": len(X_test),
        "holdout_size": len(X_hold),
        "val_metrics": {k: float(v) for k, v in best_metrics.items()},
        "test_metrics": {k: float(v) for k, v in test_metrics.items()},
        "holdout_metrics": {k: float(v) for k, v in hold_metrics.items()},
    }
    
    metadata_path = ARTIFACT_DIR / f"{model_prefix}_{best_name}.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"✓ Saved metadata to {metadata_path}")
    
    return {
        "model": best_model,
        "metadata": metadata,
        "feature_cols": feature_cols
    }


def main() -> None:
    logger.info("Loading training data from gold_fastf1...")
    df = load_training_data("target_win")
    
    if len(df) == 0:
        logger.error("No training data found!")
        return
    
    logger.info(f"Loaded {len(df)} total records")
    
    # Train models for different prediction tasks
    results = {}
    
    # 1. Race winner prediction
    results["win"] = train_prediction_task(df, "target_win", "race_win")
    
    # 2. Podium prediction
    results["podium"] = train_prediction_task(df, "target_podium", "race_podium")
    
    # 3. Finish prediction
    results["finish"] = train_prediction_task(df, "target_finish", "race_finish")
    
    logger.info(f"\n{'='*60}")
    logger.info("Training Complete")
    logger.info(f"{'='*60}")
    
    for task, result in results.items():
        if result:
            logger.info(f"✓ {task:10s} | Model: {result['metadata']['model_type']:6s} | "
                       f"Val AUC: {result['metadata']['val_metrics'].get('roc_auc', 0):.4f}")


if __name__ == "__main__":
    main()
