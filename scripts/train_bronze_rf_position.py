import logging
from pathlib import Path
from typing import Iterable, List

import duckdb
import pandas as pd

from train_fastf1_rf_position import (  # type: ignore[import]
    ML_ARTIFACTS_DIR,
    engineer_features,
    train_random_forest,
)


BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_DIR = BASE_DIR / "bronze"

logger = logging.getLogger(__name__)


def collect_race_results_from_bronze(
    seasons: Iterable[int] = (2020, 2021, 2022, 2023, 2024, 2025),
) -> pd.DataFrame:
    """
    Collect historical race results from the local OpenF1 bronze layer.

    For each race, we record:
      - season, round, grand prix name and circuit/location
      - driver code, team name
      - grid position and finish position
    """
    if not BRONZE_DIR.exists():
        raise RuntimeError(f"Bronze directory not found at {BRONZE_DIR}")

    result_path = BRONZE_DIR / "session_result" / "season=*" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet"
    drivers_path = BRONZE_DIR / "drivers" / "season=*" / "round=*" / "grand_prix=*" / "session=R" / "part-*.parquet"
    grid_path = BRONZE_DIR / "starting_grid" / "season=*" / "round=*" / "grand_prix=*" / "session=Q" / "part-*.parquet"
    # Sessions parquet is partitioned by session (FP1/FP2/FP3/Q/R/etc.), but we
    # don't have a dedicated session=R folder everywhere. Read all sessions and
    # filter on session_code='R' inside DuckDB.
    sessions_path = BRONZE_DIR / "sessions" / "season=*" / "round=*" / "grand_prix=*" / "session=*" / "part-*.parquet"

    seasons_list: List[int] = list(seasons)
    if not seasons_list:
        raise ValueError("At least one season must be provided")
    seasons_sql = ", ".join(str(s) for s in seasons_list)

    sql = f"""
    SELECT
      r.season::INT                           AS season,
      CAST(r.round AS INT)                   AS round,
      r.grand_prix                            AS grand_prix,
      COALESCE(s.circuit_short_name, r.grand_prix) AS circuit,
      d.name_acronym                          AS driver_code,
      d.team_name                             AS team_name,
      COALESCE(g.position, r.position)        AS grid_position,
      r.position                              AS finish_position
    FROM read_parquet('{result_path}') r
    JOIN read_parquet('{drivers_path}') d
      USING(season, round, grand_prix_slug, session_code, driver_number)
    LEFT JOIN read_parquet('{grid_path}') g
      USING(season, round, grand_prix_slug, driver_number)
    LEFT JOIN read_parquet('{sessions_path}') s
      ON r.season = s.season
      AND r.round = s.round
      AND r.grand_prix_slug = s.grand_prix_slug
      AND s.session_code = 'R'
    WHERE r.session_code = 'R'
      AND r.season IN ({seasons_sql})
    """

    con = duckdb.connect(":memory:")
    try:
        df = con.execute(sql).fetchdf()
    finally:
        con.close()

    df = df.dropna(
        subset=["season", "round", "grand_prix", "driver_code", "team_name", "grid_position", "finish_position"]
    )
    df = df.sort_values(["season", "round"]).reset_index(drop=True)
    return df


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    seasons = (2020, 2021, 2022, 2023, 2024, 2025)
    logger.info("Collecting bronze race results for seasons %s...", seasons)
    raw = collect_race_results_from_bronze(seasons=seasons)
    logger.info("Collected %d driver‑race rows from bronze.", len(raw))

    logger.info("Engineering driver / team / circuit features from bronze...")
    feats = engineer_features(raw)
    logger.info("Feature dataset shape: %s", feats.shape)

    ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    feats_path = ML_ARTIFACTS_DIR / "rf_position_features.parquet"
    feats.to_parquet(feats_path, index=False)
    logger.info("Engineered features saved to %s", feats_path)

    logger.info("Training RandomForestRegressor on bronze finishing positions...")
    meta = train_random_forest(feats)
    logger.info(
        "Training complete. MSE=%.4f, position_accuracy=%.3f",
        meta["metrics"]["mse"],
        meta["metrics"]["position_accuracy"],
    )
    logger.info("Model saved to %s", (ML_ARTIFACTS_DIR / "rf_position_model.joblib"))
    logger.info("Metadata saved to %s", (ML_ARTIFACTS_DIR / "rf_position_model.json"))


if __name__ == "__main__":
    main()
