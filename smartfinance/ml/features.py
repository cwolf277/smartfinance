import pandas as pd
import numpy as np

FEATURE_COLUMNS = [
    "monthly_spend",
    "txn_count",
    "avg_txn",
    "max_txn",
    "weekend_ratio",
    "category_diversity",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    df["is_weekend"] = df["date"].dt.dayofweek.isin([5, 6])

    grouped = df.groupby("year_month")
    features = pd.DataFrame({
        "monthly_spend": grouped["amount"].sum(),
        "txn_count": grouped["amount"].count(),
        "avg_txn": grouped["amount"].mean(),
        "max_txn": grouped["amount"].max(),
        "weekend_ratio": grouped["is_weekend"].mean(),
        "category_diversity": grouped["category"].nunique(),
    }).reset_index()

    features = features.fillna(0.0)
    return features


def label_overspend(features: pd.DataFrame, threshold: float | None = None) -> pd.Series:
    if threshold is None:
        threshold = features["monthly_spend"].quantile(0.7)
    return (features["monthly_spend"] > threshold).astype(int)
