from datetime import date, timedelta
from ..db import archive_old_transactions, init_db
from ..config import get_config


def archive_older_than(days: int = 365) -> dict:
    cfg = get_config()
    init_db(cfg["DATABASE_URL"])
    cutoff = date.today() - timedelta(days=days)
    n = archive_old_transactions(cutoff)
    return {"archived": n, "cutoff": cutoff.isoformat()}
