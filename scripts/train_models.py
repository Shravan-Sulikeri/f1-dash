import json
from pathlib import Path
from typing import Dict, List, Tuple

import duckdb
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

WAREHOUSE = "/Volumes/SAMSUNG/apps/f1-dash/warehouse/f1_openf1.duckdb"
ARTIFACT_DIR = Path("/Volumes/SAMSUNG/apps/f1-dash/ml_artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

CV_SPLITS = 5
CORR_THRESHOLD = 0.9
GRID_CLIP = 10
RANDOM_STATE = 42


def load_features() -> pd.DataFrame:
    con = duckdb.connect(WAREHOUSE)
    return con.execute(
        "SELECT * FROM features.race_win_training_enriched ORDER BY season, round, driver_code"
    ).fetchdf()


def split_for_eval(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    trainval = df[df["season"] <= 2023].copy()
    test = df[df["season"] == 2024].copy()
    holdout = df[df["season"] >= 2025].copy()
    return {"trainval": trainval, "test": test, "holdout": holdout}


def get_feature_columns(df: pd.DataFrame, target_col: str) -> List[str]:
    exclude = {
        target_col,
        "target_top3",
        "target_win_race",
        "finish_position",
        "points_race",
        "driver_name",
        "team_name",
        "grand_prix_slug",
        "driver_code",
    }
    numeric_cols = [
        c
        for c in df.columns
        if c not in exclude
        and c not in {"season", "round"}
        and pd.api.types.is_numeric_dtype(df[c])
    ]
    return sorted(numeric_cols)


def prepare_features(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    X = df[feature_cols].copy()

    if "grid_position" in X.columns:
        grid_fill = df["grid_position"].dropna().median() if df["grid_position"].notna().any() else GRID_CLIP
        X["grid_position"] = df["grid_position"].fillna(grid_fill).clip(lower=1, upper=GRID_CLIP)

    if "grid_position_norm" in X.columns:
        X["grid_position_norm"] = (
            df["grid_position_norm"].fillna(1.0).clip(lower=0.0, upper=1.0)
        )

    X = X.fillna(0)
    X = X.replace([np.inf, -np.inf], 0)
    return X


def prune_correlated_features(X: pd.DataFrame, threshold: float = CORR_THRESHOLD) -> Tuple[List[str], List[str]]:
    corr = X.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    drop_cols = [col for col in upper.columns if any(upper[col] > threshold)]
    keep_cols = [c for c in X.columns if c not in drop_cols]
    return keep_cols, drop_cols


def hit_at_k(df: pd.DataFrame, proba: np.ndarray, target_col: str, k: int = 1) -> float:
    df = df.copy()
    df["proba"] = proba
    hits = 0
    races = 0
    for _, grp in df.groupby(["season", "round", "grand_prix_slug"]):
        races += 1
        ordered = grp.sort_values("proba", ascending=False)
        true_codes = set(ordered[ordered[target_col] == 1]["driver_code"])
        topk_codes = set(ordered.head(k)["driver_code"])
        if true_codes & topk_codes:
            hits += 1
    return hits / races if races else 0.0


def compute_metrics(y_true: pd.Series, proba: np.ndarray, df: pd.DataFrame, target_col: str) -> Dict[str, float]:
    auc = float(roc_auc_score(y_true, proba)) if len(np.unique(y_true)) > 1 else 0.0
    ll = float(log_loss(y_true, proba, labels=[0, 1]))
    hit1 = float(hit_at_k(df.assign(**{target_col: y_true}), proba, target_col, k=1))
    hit3 = float(hit_at_k(df.assign(**{target_col: y_true}), proba, target_col, k=3))
    return {"roc_auc": auc, "log_loss": ll, "hit1": hit1, "hit3": hit3}


def evaluate(model, X_train, y_train, X_val, y_val, val_df, target_col: str):
    model.fit(X_train, y_train)
    val_proba = model.predict_proba(X_val)[:, 1]
    return compute_metrics(y_val, val_proba, val_df, target_col), val_proba


def score_split(model, X, y, df, target_col: str) -> Tuple[Dict[str, float], np.ndarray]:
    if len(X) == 0:
        return {}, np.array([])
    proba = model.predict_proba(X)[:, 1]
    return compute_metrics(y, proba, df, target_col), proba


def time_series_race_splits(df: pd.DataFrame, n_splits: int = CV_SPLITS):
    races = (
        df[["season", "round"]]
        .drop_duplicates()
        .sort_values(["season", "round"])
        .reset_index(drop=True)
    )
    if len(races) <= n_splits:
        raise ValueError(f"Not enough races ({len(races)}) for {n_splits} folds")

    tss = TimeSeriesSplit(n_splits=n_splits)
    index_df = df.reset_index()
    for train_r_idx, val_r_idx in tss.split(races):
        train_keys = races.iloc[train_r_idx]
        val_keys = races.iloc[val_r_idx]
        train_idx = index_df.merge(train_keys, on=["season", "round"])["index"].to_numpy()
        val_idx = index_df.merge(val_keys, on=["season", "round"])["index"].to_numpy()
        yield train_idx, val_idx


def cross_validate_model(model, df: pd.DataFrame, feature_cols: List[str], target_col: str):
    fold_metrics = []
    for train_idx, val_idx in time_series_race_splits(df, n_splits=CV_SPLITS):
        train_df = df.iloc[train_idx]
        val_df = df.iloc[val_idx]
        X_train = prepare_features(train_df, feature_cols)
        y_train = train_df[target_col].astype(int)
        X_val = prepare_features(val_df, feature_cols)
        y_val = val_df[target_col].astype(int)
        metrics, _ = evaluate(clone(model), X_train, y_train, X_val, y_val, val_df, target_col)
        fold_metrics.append(metrics)

    if not fold_metrics:
        return {}, []

    keys = fold_metrics[0].keys()
    avg = {k: float(np.mean([m[k] for m in fold_metrics])) for k in keys}
    return avg, fold_metrics


def train_task(df: pd.DataFrame, target_col: str, artifact_name: str):
    splits = split_for_eval(df)
    trainval_df = splits["trainval"]

    feature_cols = get_feature_columns(trainval_df, target_col)
    base_train_features = prepare_features(trainval_df, feature_cols)
    feature_cols, dropped_corr = prune_correlated_features(base_train_features, threshold=CORR_THRESHOLD)
    print(f"[features] using {len(feature_cols)} columns after dropping {len(dropped_corr)} highly correlated features")

    candidates = [
        (
            "logreg",
            make_pipeline(
                StandardScaler(),
                LogisticRegression(max_iter=400, class_weight="balanced", n_jobs=-1),
            ),
        ),
        (
            "rf",
            RandomForestClassifier(
                n_estimators=400,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=5,
                max_features="sqrt",
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
        ),
    ]

    best = None
    cv_results = {}
    for name, model in candidates:
        avg_metrics, fold_metrics = cross_validate_model(model, trainval_df, feature_cols, target_col)
        cv_results[name] = {"avg": avg_metrics, "folds": fold_metrics}
        print(f"[cv] {name} avg metrics {avg_metrics}")
        if (best is None) or (avg_metrics.get("roc_auc", 0.0) > best[2].get("roc_auc", 0.0)):
            best = (name, model, avg_metrics)

    if best is None:
        raise RuntimeError("No model trained")

    best_name, best_model, best_cv = best
    print(f"[select] best model={best_name} (cv roc_auc={best_cv.get('roc_auc', 0.0):.4f})")

    # Fit on all pre-2024 data (train + val years)
    X_trainval = prepare_features(trainval_df, feature_cols)
    y_trainval = trainval_df[target_col].astype(int)
    best_model.fit(X_trainval, y_trainval)

    test_metrics, _ = score_split(
        best_model,
        prepare_features(splits["test"], feature_cols),
        splits["test"][target_col].astype(int),
        splits["test"],
        target_col,
    )
    hold_metrics, _ = score_split(
        best_model,
        prepare_features(splits["holdout"], feature_cols),
        splits["holdout"][target_col].astype(int),
        splits["holdout"],
        target_col,
    )

    joblib.dump(best_model, ARTIFACT_DIR / f"{artifact_name}.joblib")
    meta = {
        "model": best_name,
        "feature_list": feature_cols,
        "dropped_correlated_features": dropped_corr,
        "correlation_threshold": CORR_THRESHOLD,
        "grid_position_clip": GRID_CLIP,
        "cv_folds": CV_SPLITS,
        "cv_avg_metrics": best_cv,
        "cv_fold_metrics": cv_results[best_name]["folds"],
        "test_metrics": test_metrics,
        "holdout_metrics": hold_metrics,
        "splits": {"trainval": "<=2023", "test": "2024", "holdout": ">=2025"},
    }
    with open(ARTIFACT_DIR / f"{artifact_name}.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[saved] {artifact_name}.joblib and metadata")


def main():
    df = load_features()
    print(f"[data] loaded features rows={len(df)}, seasons {df['season'].min()}-{df['season'].max()}")
    train_task(df, "target_win_race", "race_win_best")
    train_task(df, "target_top3", "race_top3_best")


if __name__ == "__main__":
    main()
