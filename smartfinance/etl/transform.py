import pandas as pd

REQUIRED_COLS = ["transaction_id", "date", "amount", "name", "category"]


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = None

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["category"] = df["category"].fillna("Uncategorized").astype(str)
    df["name"] = df["name"].fillna("").astype(str)
    df = df.dropna(subset=["date"])
    df["transaction_id"] = df["transaction_id"].fillna(
        df.index.to_series().astype(str).radd("auto-")
    )
    return df


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "date" in df.columns:
        dates = pd.to_datetime(df["date"])
        df["year"] = dates.dt.year
        df["month"] = dates.dt.month
        df["day_of_week"] = dates.dt.dayofweek
    df["is_expense"] = df["amount"] > 0
    df["abs_amount"] = df["amount"].abs()
    return df


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dates = pd.to_datetime(df["date"])
    df["year_month"] = dates.dt.to_period("M").astype(str)
    grouped = (
        df.groupby(["year_month", "category"], as_index=False)
        .agg(total=("amount", "sum"), count=("amount", "size"))
    )
    return grouped
