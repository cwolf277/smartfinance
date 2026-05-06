import pandas as pd
from smartfinance.ml.features import build_features, label_overspend, FEATURE_COLUMNS
from smartfinance.ml.model import train_overspend_model
from smartfinance.ml.predict import predict_overspend
from smartfinance.etl.pipeline import run_pipeline


def test_build_features():
    df = pd.DataFrame([
        {"transaction_id": "a", "date": "2025-01-01", "amount": 100, "name": "X", "category": "Food"},
        {"transaction_id": "b", "date": "2025-01-15", "amount": 50, "name": "Y", "category": "Travel"},
        {"transaction_id": "c", "date": "2025-02-01", "amount": 200, "name": "Z", "category": "Food"},
    ])
    feats = build_features(df)
    assert all(c in feats.columns for c in FEATURE_COLUMNS)
    assert len(feats) == 2


def test_label_overspend():
    feats = pd.DataFrame({
        "monthly_spend": [100, 200, 300, 400, 500],
        "txn_count": [1, 2, 3, 4, 5],
        "avg_txn": [10] * 5,
        "max_txn": [50] * 5,
        "weekend_ratio": [0.3] * 5,
        "category_diversity": [3] * 5,
    })
    labels = label_overspend(feats)
    assert labels.sum() > 0
    assert labels.sum() < len(feats)


def test_train_and_predict():
    run_pipeline("data/sample_transactions.csv")
    metrics = train_overspend_model()
    assert metrics["ok"]
    out = predict_overspend({
        "monthly_spend": 5000,
        "txn_count": 50,
        "avg_txn": 100,
        "max_txn": 1500,
        "weekend_ratio": 0.4,
        "category_diversity": 8,
    })
    assert out["ok"]
    assert 0.0 <= out["overspend_probability"] <= 1.0
    assert out["risk_level"] in {"low", "medium", "high"}
