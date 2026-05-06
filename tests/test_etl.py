import pandas as pd
from smartfinance.etl.transform import normalize, enrich, aggregate_monthly
from smartfinance.etl.pipeline import run_pipeline


def test_normalize_fills_missing():
    df = pd.DataFrame([
        {"transaction_id": "a", "date": "2025-01-01", "amount": "12.5", "name": "X", "category": None},
        {"transaction_id": None, "date": "2025-01-02", "amount": "abc", "name": None, "category": "Food"},
    ])
    out = normalize(df)
    assert out.iloc[1]["category"] == "Food"
    assert out.iloc[1]["amount"] == 0.0
    assert all(out["transaction_id"].notna())


def test_enrich_adds_columns():
    df = pd.DataFrame([{"transaction_id": "a", "date": "2025-01-01", "amount": 10, "name": "X", "category": "F"}])
    out = enrich(normalize(df))
    assert "year" in out.columns
    assert "month" in out.columns
    assert "abs_amount" in out.columns
    assert "is_expense" in out.columns


def test_aggregate_monthly():
    df = pd.DataFrame([
        {"transaction_id": "a", "date": "2025-01-01", "amount": 10, "name": "X", "category": "Food"},
        {"transaction_id": "b", "date": "2025-01-15", "amount": 20, "name": "Y", "category": "Food"},
        {"transaction_id": "c", "date": "2025-02-01", "amount": 5, "name": "Z", "category": "Food"},
    ])
    out = aggregate_monthly(normalize(df))
    assert len(out) == 2
    jan = out[out["year_month"] == "2025-01"].iloc[0]
    assert jan["total"] == 30


def test_pipeline_runs():
    summary = run_pipeline("data/sample_transactions.csv")
    assert summary["ok"]
    assert summary["rows_loaded"] > 0
