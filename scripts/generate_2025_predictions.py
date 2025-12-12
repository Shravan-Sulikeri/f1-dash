#!/usr/bin/env python3
"""
Generate race win predictions for 2025 season using the trained model.
"""

import json
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
import joblib

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "warehouse" / "f1_openf1.duckdb"
MODEL_PATH = REPO_ROOT / "ml_artifacts" / "race_win_full.joblib"
META_PATH = REPO_ROOT / "ml_artifacts" / "race_win_full.json"

def load_model_and_features():
    """Load the trained model and feature list."""
    print(f"Loading model from {MODEL_PATH}...")
    model = joblib.load(MODEL_PATH)
    
    with open(META_PATH) as f:
        meta = json.load(f)
    
    feature_cols = meta['feature_list']
    print(f"Model expects {len(feature_cols)} features")
    
    return model, feature_cols

def load_2025_data():
    """Load 2025 race data from gold_fastf1.win_prediction_dataset."""
    print("\nLoading 2025 data from DuckDB...")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    
    # Get metadata about available races
    races = con.execute("""
        SELECT DISTINCT grand_prix_slug, COUNT(*) as drivers
        FROM gold_fastf1.win_prediction_dataset
        WHERE season = 2025
        GROUP BY grand_prix_slug
        ORDER BY grand_prix_slug
    """).fetchdf()
    
    print(f"\nFound {len(races)} races for 2025:")
    for _, row in races.iterrows():
        print(f"  - {row['grand_prix_slug']}: {row['drivers']} drivers")
    
    # Load all 2025 data
    df = con.execute("""
        SELECT *
        FROM gold_fastf1.win_prediction_dataset
        WHERE season = 2025
        ORDER BY grand_prix_slug, driver_code
    """).fetchdf()
    
    con.close()
    
    print(f"\nLoaded {len(df)} driver-race combinations")
    return df

def generate_predictions(model, feature_cols, df):
    """Generate predictions for 2025 data."""
    print("\nGenerating predictions...")
    
    # Prepare features
    X = df[feature_cols].copy()
    X = X.fillna(0)  # Fill missing values with 0
    
    # Generate predictions
    pred_proba = model.predict_proba(X)[:, 1]
    
    # Add predictions to dataframe
    df['pred_win_proba'] = pred_proba
    
    # Calculate softmax probabilities per race
    races = []
    for gp_slug, group in df.groupby('grand_prix_slug'):
        indices = group.index
        probs = pred_proba[indices - df.index[0]]  # Adjust for dataframe index
        
        # Softmax
        exp_probs = np.exp(probs - np.max(probs))  # Subtract max for numerical stability
        softmax_probs = exp_probs / exp_probs.sum()
        
        df.loc[indices, 'pred_win_proba_softmax'] = softmax_probs
    
    print(f"Generated predictions for {len(df)} entries")
    
    return df

def save_predictions(df):
    """Save predictions to DuckDB."""
    print("\nSaving predictions to database...")
    
    con = duckdb.connect(str(DB_PATH), read_only=False)
    
    # Create predictions schema if it doesn't exist
    con.execute("CREATE SCHEMA IF NOT EXISTS predictions")
    
    # Prepare data for insertion
    predictions_df = df[[
        'season', 'grand_prix_slug', 'driver_code', 'driver_name', 'team_name',
        'grid_position', 'pred_win_proba', 'pred_win_proba_softmax'
    ]].copy()
    
    # Add round as 0 for 2025 (since we don't know the order yet)
    predictions_df['round'] = 0
    
    # Drop existing 2025 predictions
    con.execute("DELETE FROM predictions.race_win WHERE season = 2025")
    
    # Insert new predictions (append to existing table)
    con.execute("""
        INSERT INTO predictions.race_win 
        SELECT 
            season,
            round,
            grand_prix_slug,
            NULL as driver_name_col,  -- Placeholder
            driver_code,
            team_name,
            grid_position,
            0.0 as grid_position_norm,
            0.0 as driver_points_pre,
            0.0 as team_points_pre,
            0.0 as track_temp_c,
            0.0 as rain_probability,
            0.0 as driver_avg_finish_last_3,
            0.0 as driver_points_last_3,
            0.0 as team_points_last_3,
            0.0 as driver_track_avg_finish_last_3_at_gp,
            0.0 as driver_track_points_last_3_at_gp,
            0.0 as team_track_points_last_3_at_gp,
            0 as target_win_race,
            pred_win_proba,
            pred_win_proba_softmax
        FROM predictions_df
    """)
    
    count = con.execute("SELECT COUNT(*) FROM predictions.race_win WHERE season = 2025").fetchone()[0]
    print(f"✓ Saved {count} predictions to predictions.race_win")
    
    con.close()

def show_top_predictions(df):
    """Display top predictions for each race."""
    print("\n" + "="*60)
    print("TOP PREDICTIONS FOR 2025 RACES")
    print("="*60)
    
    for gp_slug, group in df.groupby('grand_prix_slug'):
        top3 = group.nlargest(3, 'pred_win_proba_softmax')
        
        gp_name = gp_slug.replace('-', ' ').title()
        print(f"\n{gp_name}")
        print("-" * 40)
        
        for _, row in top3.iterrows():
            driver = row['driver_code']
            team = row['team_name']
            prob = row['pred_win_proba_softmax'] * 100
            print(f"  {driver:3s} ({team:20s}): {prob:5.1f}%")

def main():
    """Main execution."""
    print("="*60)
    print("GENERATING 2025 RACE WIN PREDICTIONS")
    print("="*60)
    
    # Load model
    model, feature_cols = load_model_and_features()
    
    # Load 2025 data
    df = load_2025_data()
    
    # Generate predictions
    df = generate_predictions(model, feature_cols, df)
    
    # Show top predictions
    show_top_predictions(df)
    
    # Save to database
    save_predictions(df)
    
    print("\n" + "="*60)
    print("✓ COMPLETE!")
    print("="*60)

if __name__ == '__main__':
    main()
