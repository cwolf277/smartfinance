import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent


def get_config():
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'data' / 'smartfinance.db'}"),
        "PLAID_CLIENT_ID": os.getenv("PLAID_CLIENT_ID", ""),
        "PLAID_SECRET": os.getenv("PLAID_SECRET", ""),
        "PLAID_ENV": os.getenv("PLAID_ENV", "sandbox"),
        "MODEL_PATH": os.getenv("MODEL_PATH", str(ROOT / "data" / "overspend_model.joblib")),
        "MASK_PII": os.getenv("MASK_PII", "true").lower() == "true",
        "DATA_DIR": str(ROOT / "data"),
    }
