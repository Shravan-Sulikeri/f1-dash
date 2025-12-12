#!/usr/bin/env python3
"""
Train race win prediction model using 2019-2025 data.
Uses gold_fastf1.win_prediction_dataset table.
"""

import json
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, log_loss, accuracy_score, f1_score
import joblib

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "warehouse" / "f1_openf1.duckdb"
ML_ARTIFACTS_DIR = REPO_ROOT / "ml_artifacts"
ML_ARTIFACTS_DIR.mkdir(exist_ok=True)

OUTPUT_MODEL_PATH = ML_ARTIFACTS_DIR / "race_win_full.joblib"
OUTPUT_META_PATH = ML_ARTIFACTS_DIR / "race_win_full.json"

# Feature configuration
FEATURE_COLS = [
    # Grid position
    'grid_position',
    'grid_deviation_from_venue_avg',

    # Weather (focus on rain; drop temp/humidity noise)
    'max_rainfall_mm',
    'is_wet_race',
    'normalized_wind_speed',
    
    # Driver career stats
    'driver_career_wins',
    'driver_career_podiums',
    'driver_career_races',
    'driver_career_win_pct',
    'driver_career_podium_pct',
    'driver_avg_finish_position',
    'driver_finish_rate',
    'driver_avg_position_gain',
    
    # Driver recent form
    'driver_avg_finish_last_5',
    'driver_points_last_5',
    'driver_avg_grid_last_5',
    
    # Driver venue-specific
    'driver_races_at_venue',
    'driver_wins_at_venue',
    'driver_podiums_at_venue',
    'driver_win_pct_at_venue',
    'driver_podium_pct_at_venue',
    'driver_avg_finish_at_venue',
    'driver_avg_grid_at_venue',
    'driver_avg_points_at_venue',
    'driver_ever_wet_at_venue',
    
    # Driver weather performance
    'driver_dry_races',
    'driver_dry_wins',
    'driver_dry_win_pct',
    'driver_avg_finish_dry',
    'driver_wet_races',
    'driver_wet_wins',
    'driver_wet_win_pct',
    'driver_avg_finish_wet',
    'driver_humid_races',
    'driver_avg_finish_humid',
    
    # Team stats
    'team_wins_history',
    'team_podiums_history',
    'team_points_history',
    'team_avg_finish',
]

TARGET_COL = 'target_win'

def load_data():
    """Load training data from DuckDB."""
    print("Loading data from DuckDB...")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    
    # Load data from 2019-2025 (excluding 2018 as it might have incomplete history)
    query = f"""
    SELECT 
        season,
        round,
        grand_prix_slug,
        driver_code,
        {', '.join(FEATURE_COLS)},
        {TARGET_COL}
    FROM gold_fastf1.win_prediction_dataset
    WHERE season >= 2019 AND season <= 2025
    ORDER BY season, round, driver_code
    """
    
    df = con.execute(query).fetchdf()
    con.close()
    
    print(f"Loaded {len(df)} rows from {df['season'].min()}-{df['season'].max()}")
    print(f"Seasons: {sorted(df['season'].unique())}")
    print(f"Target distribution: {df[TARGET_COL].value_counts().to_dict()}")
    
    return df

def split_data(df):
    """Split data into train/val/test by season."""
    # Train: 2019-2022
    # Val: 2023
    # Test: 2024
    # Holdout: 2025
    
    train_df = df[df['season'].between(2019, 2022)].copy()
    val_df = df[df['season'] == 2023].copy()
    test_df = df[df['season'] == 2024].copy()
    holdout_df = df[df['season'] == 2025].copy()
    
    print(f"\nData splits:")
    print(f"  Train (2019-2022): {len(train_df)} rows, {train_df[TARGET_COL].sum()} wins")
    print(f"  Val (2023): {len(val_df)} rows, {val_df[TARGET_COL].sum()} wins")
    print(f"  Test (2024): {len(test_df)} rows, {test_df[TARGET_COL].sum()} wins")
    print(f"  Holdout (2025): {len(holdout_df)} rows, {holdout_df[TARGET_COL].sum()} wins")
    
    return train_df, val_df, test_df, holdout_df

def prepare_features(df, feature_cols):
    """Prepare feature matrix."""
    X = df[feature_cols].copy()
    
    # Fill NaN with 0 (for drivers with no history at venue, etc.)
    X = X.fillna(0)
    
    return X

def evaluate_ranking(y_true, y_pred_proba, races_df):
    """Evaluate how well the model ranks winners."""
    results = []
    
    # Reset index to ensure alignment
    races_df = races_df.reset_index(drop=True)
    
    for (season, round_num), group in races_df.groupby(['season', 'round']):
        if group[TARGET_COL].sum() == 0:
            continue  # No winner in this race (e.g., future race)
        
        # Get predictions for this race using reset indices
        indices = group.index.tolist()
        true_winner = group[TARGET_COL].values
        pred_proba = y_pred_proba[indices]
        
        # Rank by prediction
        sorted_indices = np.argsort(-pred_proba)
        winner_rank = np.where(true_winner[sorted_indices] == 1)[0]
        
        if len(winner_rank) > 0:
            results.append({
                'season': season,
                'round': round_num,
                'winner_rank': winner_rank[0] + 1,  # 1-indexed
                'hit1': winner_rank[0] < 1,
                'hit3': winner_rank[0] < 3,
            })
    
    if not results:
        return {}
    
    results_df = pd.DataFrame(results)
    return {
        'races_evaluated': len(results_df),
        'hit1': results_df['hit1'].mean(),
        'hit3': results_df['hit3'].mean(),
        'avg_winner_rank': results_df['winner_rank'].mean(),
    }

def train_model(X_train, y_train, X_val, y_val):
    """Train Random Forest model."""
    print("\nTraining Random Forest model...")
    
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=10,
        min_samples_leaf=5,
        max_features='sqrt',
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train, y_train)
    
    # Feature importance
    importances = pd.DataFrame({
        'feature': FEATURE_COLS,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 features:")
    print(importances.head(10).to_string(index=False))
    
    return model

def evaluate_model(model, X, y, df, split_name):
    """Evaluate model performance."""
    print(f"\nEvaluating on {split_name}...")
    
    y_pred_proba = model.predict_proba(X)[:, 1]
    y_pred = model.predict(X)
    
    scores = {
        'accuracy': accuracy_score(y, y_pred),
        'f1': f1_score(y, y_pred),
        'roc_auc': roc_auc_score(y, y_pred_proba),
        'log_loss': log_loss(y, y_pred_proba),
    }
    
    # Ranking metrics
    ranking = evaluate_ranking(y, y_pred_proba, df)
    scores.update(ranking)
    
    print(f"  ROC AUC: {scores['roc_auc']:.4f}")
    print(f"  Log Loss: {scores['log_loss']:.4f}")
    print(f"  Accuracy: {scores['accuracy']:.4f}")
    print(f"  F1: {scores['f1']:.4f}")
    if ranking:
        print(f"  Hit@1: {ranking['hit1']:.2%} ({ranking['races_evaluated']} races)")
        print(f"  Hit@3: {ranking['hit3']:.2%}")
        print(f"  Avg Winner Rank: {ranking['avg_winner_rank']:.2f}")
    
    return scores

def main():
    """Main training pipeline."""
    print("=" * 60)
    print("Training Race Win Model (2019-2025)")
    print("=" * 60)
    
    # Load data
    df = load_data()
    
    # Split data
    train_df, val_df, test_df, holdout_df = split_data(df)
    
    # Prepare features
    X_train = prepare_features(train_df, FEATURE_COLS)
    y_train = train_df[TARGET_COL].values
    
    X_val = prepare_features(val_df, FEATURE_COLS)
    y_val = val_df[TARGET_COL].values
    
    X_test = prepare_features(test_df, FEATURE_COLS)
    y_test = test_df[TARGET_COL].values
    
    X_holdout = prepare_features(holdout_df, FEATURE_COLS)
    y_holdout = holdout_df[TARGET_COL].values
    
    # Train model
    model = train_model(X_train, y_train, X_val, y_val)
    
    # Evaluate
    train_scores = evaluate_model(model, X_train, y_train, train_df, "Train (2019-2022)")
    val_scores = evaluate_model(model, X_val, y_val, val_df, "Val (2023)")
    test_scores = evaluate_model(model, X_test, y_test, test_df, "Test (2024)")
    holdout_scores = evaluate_model(model, X_holdout, y_holdout, holdout_df, "Holdout (2025)")
    
    # Save model
    print(f"\nSaving model to {OUTPUT_MODEL_PATH}...")
    joblib.dump(model, OUTPUT_MODEL_PATH)
    
    # Save metadata
    metadata = {
        'model_type': 'RandomForest',
        'features': FEATURE_COLS,
        'feature_list': FEATURE_COLS,  # kept for backward compatibility
        'target': TARGET_COL,
        'n_features': len(FEATURE_COLS),
        'data': {
            'train_years': '2019-2022',
            'val_year': '2023',
            'test_year': '2024',
            'holdout_year': '2025',
            'train_rows': len(train_df),
            'val_rows': len(val_df),
            'test_rows': len(test_df),
            'holdout_rows': len(holdout_df),
        },
        'scores': {
            'train': train_scores,
            'val': val_scores,
            'test': test_scores,
            'holdout': holdout_scores,
        },
        'model_params': {
            'n_estimators': 200,
            'max_depth': 12,
            'min_samples_split': 10,
            'min_samples_leaf': 5,
            'max_features': 'sqrt',
            'class_weight': 'balanced',
        }
    }
    
    print(f"Saving metadata to {OUTPUT_META_PATH}...")
    with open(OUTPUT_META_PATH, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✓ Training complete!")
    print("=" * 60)
    print(f"\nModel: {OUTPUT_MODEL_PATH}")
    print(f"Metadata: {OUTPUT_META_PATH}")
    print(f"\nKey metrics:")
    print(f"  Val ROC AUC: {val_scores['roc_auc']:.4f}")
    print(f"  Test ROC AUC: {test_scores['roc_auc']:.4f}")
    print(f"  Test Hit@1: {test_scores.get('hit1', 0):.2%}")
    print(f"  Test Hit@3: {test_scores.get('hit3', 0):.2%}")

if __name__ == '__main__':
    main()
