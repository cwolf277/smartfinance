from pathlib import Path
import pandas as pd


def extract_csv(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def extract_records(records: list[dict]) -> pd.DataFrame:
    return pd.DataFrame.from_records(records)
