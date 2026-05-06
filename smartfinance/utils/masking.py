from typing import Iterable, List, Dict, Any


def mask_account_id(account_id: str | None) -> str:
    if not account_id:
        return ""
    s = str(account_id)
    if len(s) <= 4:
        return "*" * len(s)
    return "*" * (len(s) - 4) + s[-4:]


def mask_transactions(txns: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    masked = []
    for t in txns:
        copy = dict(t)
        if "account_id" in copy:
            copy["account_id"] = mask_account_id(copy["account_id"])
        if "account_owner" in copy:
            copy["account_owner"] = None
        if "location" in copy and isinstance(copy["location"], dict):
            loc = dict(copy["location"])
            loc.pop("address", None)
            loc.pop("lat", None)
            loc.pop("lon", None)
            copy["location"] = loc
        masked.append(copy)
    return masked
