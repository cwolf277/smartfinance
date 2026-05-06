import pandas as pd
from ..db import save_transactions


def load_dataframe(df: pd.DataFrame) -> int:
    records = df.to_dict(orient="records")
    return save_transactions(records)
