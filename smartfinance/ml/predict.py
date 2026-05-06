from pathlib import Path
import joblib
import pandas as pd

from ..config import get_config
from .features import FEATURE_COLUMNS


def predict_overspend(features: dict) -> dict:
    cfg = get_config()
    model_path = Path(cfg["MODEL_PATH"])
    if not model_path.exists():
        return {"ok": False, "error": "model not trained. POST /ml/train first."}

    pipeline = joblib.load(model_path)
    row = {col: float(features.get(col, 0.0)) for col in FEATURE_COLUMNS}
    X = pd.DataFrame([row])
    proba = float(pipeline.predict_proba(X)[0][1])
    label = int(proba >= 0.5)
    risk = "high" if proba >= 0.66 else ("medium" if proba >= 0.33 else "low")
    return {
        "ok": True,
        "overspend_probability": proba,
        "overspend_label": label,
        "risk_level": risk,
        "features": row,
    }
