import logging
from pathlib import Path

import duckdb
import joblib
import numpy as np
import pandas as pd
import json

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
WAREHOUSE_PATH = BASE_DIR / "warehouse" / "f1_openf1.duckdb"
MODEL_PATH = BASE_DIR / "ml_artifacts" / "race_win_logreg.joblib"
META_PATH = BASE_DIR / "ml_artifacts" / "race_win_logreg.json"


def _load_feature_cols() -> list[str]:
  """Read feature column list from the model metadata."""
  if META_PATH.exists():
      meta = json.loads(META_PATH.read_text())
      feats = meta.get("feature_cols")
      if isinstance(feats, list) and feats:
          return [str(f) for f in feats]
  # Fallback to the enriched bronze feature set used in train_models.py
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


FEATURE_COLS = _load_feature_cols()
LABEL_COL = "target_win_race"


def softmax(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    values = series.to_numpy(dtype=float)
    values = np.nan_to_num(values, nan=0.0)
    values = values - np.max(values)
    exp = np.exp(values)
    denom = exp.sum()
    if denom == 0:
        return pd.Series([0.0] * len(series), index=series.index)
    return pd.Series(exp / denom, index=series.index)


def load_training_data(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    query = """
    SELECT *
    FROM features.race_win_training_enriched
    WHERE season >= 2020
    """
    df = con.execute(query).df()
    # Align with training: fill missing label/feature values with 0 to avoid
    # dropping all rows when form features are sparse.
    df[LABEL_COL] = df[LABEL_COL].fillna(0)
    df[FEATURE_COLS] = df[FEATURE_COLS].fillna(0)
    return df


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("generate_race_predictions")

    logger.info("Connecting to DuckDB warehouse at %s", WAREHOUSE_PATH)
    con = duckdb.connect(str(WAREHOUSE_PATH))

    df = load_training_data(con)
    print(df.info())
    return


if __name__ == "__main__":
    main()
