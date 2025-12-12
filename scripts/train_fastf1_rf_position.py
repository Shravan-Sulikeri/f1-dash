import json
import logging
from pathlib import Path
from typing import Iterable, List

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

try:
    import fastf1  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    fastf1 = None


BASE_DIR = Path(__file__).resolve().parent.parent
FASTF1_CACHE = BASE_DIR / "fastf1_cache"
ML_ARTIFACTS_DIR = BASE_DIR / "ml_artifacts"

logger = logging.getLogger(__name__)


def _enable_fastf1_cache() -> None:
    if fastf1 is None:
        raise RuntimeError("fastf1 is not installed. Install with `pip install fastf1` in your venv.")
    FASTF1_CACHE.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(FASTF1_CACHE))  # type: ignore[union-attr]


def collect_race_results(
    seasons: Iterable[int] = (2020, 2021, 2022, 2023, 2024, 2025),
    session_code: str = "R",
) -> pd.DataFrame:
    """
    Collect historical race results via FastF1.

    For each race, we record:
      - season, round, grand prix name and circuit/location
      - driver code, team name
      - grid position and finish position
    """
    _enable_fastf1_cache()

    rows: List[dict] = []
    for season in seasons:
        # Conservatively scan rounds 1–30; FastF1 will raise if the event doesn't exist.
        for rnd in range(1, 30):
            try:
                session = fastf1.get_session(season, rnd, session_code)  # type: ignore[union-attr]
            except Exception:
                # No such round for this season – move on.
                continue

            try:
                session.load()  # type: ignore[union-attr]
            except Exception as exc:  # pragma: no cover - external API
                logger.warning("Failed to load session %s %s %s: %s", season, rnd, session_code, exc)
                continue

            event = getattr(session, "event", None)
            gp_name = getattr(event, "EventName", None) or getattr(event, "OfficialEventName", None) or ""
            location = getattr(event, "Location", None) or getattr(event, "EventName", None) or ""

            results = getattr(session, "results", None)
            if results is None:
                continue

            for _, row in results.iterrows():
                # Skip drivers without a classified grid / finishing position where possible.
                grid = row.get("GridPosition")
                pos = row.get("Position")
                if grid is None or (isinstance(grid, float) and np.isnan(grid)):
                    continue

                # Map non-finishers to a large position so the regressor can still learn ordering.
                finish_pos: float
                if pos is None or (isinstance(pos, float) and np.isnan(pos)):
                    # Treat as DNF at the back of the field.
                    finish_pos = 21.0
                else:
                    try:
                        finish_pos = float(pos)
                    except Exception:
                        # Strings like 'R' / 'NC' – treat as backmarker.
                        finish_pos = 21.0

                rows.append(
                    {
                        "season": season,
                        "round": rnd,
                        "grand_prix": str(gp_name),
                        "circuit": str(location),
                        "driver_code": row.get("Abbreviation") or row.get("DriverNumber"),
                        "team_name": row.get("TeamName") or row.get("Team"),
                        "grid_position": float(grid),
                        "finish_position": finish_pos,
                    }
                )

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["driver_code", "team_name", "grid_position", "finish_position"])
    df = df.sort_values(["season", "round"]).reset_index(drop=True)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build driver / team / circuit history features on top of raw race results.

    Features created:
      - driver_races_so_far
      - driver_avg_finish_prev
      - team_races_so_far
      - team_avg_finish_prev
      - circuit_avg_finish_prev
    """
    df = df.copy()

    # Driver experience: number of prior race starts.
    df["driver_races_so_far"] = (
        df.sort_values(["season", "round"])
        .groupby("driver_code")
        .cumcount()
        .astype(float)
    )

    # Driver average finishing position prior to this race.
    df["driver_avg_finish_prev"] = (
        df.sort_values(["season", "round"])
        .groupby("driver_code")["finish_position"]
        .transform(lambda s: s.shift().expanding().mean())
    )

    # Team experience: number of prior race entries for this team.
    df["team_races_so_far"] = (
        df.sort_values(["season", "round"])
        .groupby("team_name")
        .cumcount()
        .astype(float)
    )

    # Team average finishing position prior to this race.
    df["team_avg_finish_prev"] = (
        df.sort_values(["season", "round"])
        .groupby("team_name")["finish_position"]
        .transform(lambda s: s.shift().expanding().mean())
    )

    # Circuit-specific average finishing position prior to this race.
    df["circuit_avg_finish_prev"] = (
        df.sort_values(["season", "round"])
        .groupby(["driver_code", "circuit"])["finish_position"]
        .transform(lambda s: s.shift().expanding().mean())
    )

    # Drop rows where we do not have any history yet (first race for driver/team).
    feature_cols = [
        "grid_position",
        "driver_races_so_far",
        "driver_avg_finish_prev",
        "team_races_so_far",
        "team_avg_finish_prev",
        "circuit_avg_finish_prev",
    ]
    df = df.dropna(subset=feature_cols + ["finish_position"])
    return df


def train_random_forest(df: pd.DataFrame) -> dict:
    """Train a Random Forest regressor to predict finishing position."""
    feature_cols = [
        "grid_position",
        "driver_races_so_far",
        "driver_avg_finish_prev",
        "team_races_so_far",
        "team_avg_finish_prev",
        "circuit_avg_finish_prev",
    ]

    X = df[feature_cols].astype(float)
    y = df["finish_position"].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf = RandomForestRegressor(
        n_estimators=400,
        max_depth=None,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    # "Position accuracy": fraction of predictions where rounded position matches true position.
    pos_acc = float((np.round(y_pred) == np.round(y_test)).mean())

    # Feature importances for inspection.
    importances = dict(zip(feature_cols, rf.feature_importances_.tolist()))

    ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = ML_ARTIFACTS_DIR / "rf_position_model.joblib"
    meta_path = ML_ARTIFACTS_DIR / "rf_position_model.json"

    joblib.dump(rf, model_path)

    metadata = {
        "model_name": "rf_position_model",
        "type": "RandomForestRegressor",
        "feature_cols": feature_cols,
        "n_rows": int(len(df)),
        "metrics": {
            "mse": float(mse),
            "position_accuracy": pos_acc,
        },
        "feature_importances": importances,
        "seasons_min": int(df["season"].min()),
        "seasons_max": int(df["season"].max()),
    }
    with meta_path.open("w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    seasons = (2020, 2021, 2022, 2023, 2024, 2025)
    logger.info("Collecting FastF1 race results for seasons %s...", seasons)
    raw = collect_race_results(seasons=seasons)
    logger.info("Collected %d driver‑race rows.", len(raw))

    logger.info("Engineering driver / team / circuit features...")
    feats = engineer_features(raw)
    logger.info("Feature dataset shape: %s", feats.shape)

    # Persist engineered features so the API can reuse them at inference time.
    ML_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    feats_path = ML_ARTIFACTS_DIR / "rf_position_features.parquet"
    feats.to_parquet(feats_path, index=False)
    logger.info("Engineered features saved to %s", feats_path)

    logger.info("Training RandomForestRegressor on finishing positions...")
    meta = train_random_forest(feats)
    logger.info("Training complete. MSE=%.4f, position_accuracy=%.3f", meta["metrics"]["mse"], meta["metrics"]["position_accuracy"])
    logger.info("Model saved to %s", (ML_ARTIFACTS_DIR / "rf_position_model.joblib"))
    logger.info("Metadata saved to %s", (ML_ARTIFACTS_DIR / "rf_position_model.json"))
    logger.info("Top feature importances:")
    for name, score in sorted(meta["feature_importances"].items(), key=lambda kv: kv[1], reverse=True):
        logger.info("  %s: %.3f", name, score)


if __name__ == "__main__":
    main()
