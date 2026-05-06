from pathlib import Path
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from ..config import get_config
from ..db import init_db, fetch_transactions
from .features import build_features, label_overspend, FEATURE_COLUMNS


def _load_training_frame() -> pd.DataFrame:
    cfg = get_config()
    init_db(cfg["DATABASE_URL"])
    rows = fetch_transactions(limit=100000)
    if not rows:
        sample = Path(cfg["DATA_DIR"]) / "sample_transactions.csv"
        if sample.exists():
            return pd.read_csv(sample)
        raise RuntimeError("No transactions available for training. Load data via /etl/run first.")
    return pd.DataFrame(rows)


def train_overspend_model() -> dict:
    cfg = get_config()
    df = _load_training_frame()
    features = build_features(df)
    y = label_overspend(features)
    X = features[FEATURE_COLUMNS]

    if len(X) < 4 or y.nunique() < 2:
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000)),
        ])
        if y.nunique() < 2:
            return {
                "ok": False,
                "error": "not enough class diversity to train",
                "samples": int(len(X)),
            }
        pipeline.fit(X, y)
        Path(cfg["MODEL_PATH"]).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, cfg["MODEL_PATH"])
        return {"ok": True, "samples": int(len(X)), "note": "trained on full set, no holdout"}

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000)),
    ])
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    Path(cfg["MODEL_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, cfg["MODEL_PATH"])

    return {
        "ok": True,
        "samples": int(len(X)),
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
        "f1": float(f1_score(y_test, preds, zero_division=0)),
        "model_path": cfg["MODEL_PATH"],
    }
