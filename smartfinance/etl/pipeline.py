from pathlib import Path

from ..config import get_config
from ..db import init_db
from .extract import extract_csv
from .transform import normalize, enrich, aggregate_monthly
from .load import load_dataframe


def run_pipeline(source: str) -> dict:
    cfg = get_config()
    init_db(cfg["DATABASE_URL"])

    path = Path(source)
    if not path.exists():
        return {"ok": False, "error": f"source not found: {source}"}

    raw = extract_csv(path)
    normalized = normalize(raw)
    enriched = enrich(normalized)
    monthly = aggregate_monthly(enriched)
    inserted = load_dataframe(enriched)

    return {
        "ok": True,
        "rows_extracted": int(len(raw)),
        "rows_loaded": int(inserted),
        "monthly_summaries": monthly.to_dict(orient="records"),
    }
