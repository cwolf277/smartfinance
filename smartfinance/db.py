from datetime import datetime
from typing import Iterable, List, Dict, Any

from sqlalchemy import (
    Column,
    String,
    Float,
    Date,
    DateTime,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
_engine = None
_Session = None


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String, primary_key=True)
    account_id = Column(String, index=True)
    name = Column(String)
    merchant_name = Column(String, nullable=True)
    amount = Column(Float)
    iso_currency_code = Column(String, default="USD")
    category = Column(String, nullable=True)
    date = Column(Date, index=True)
    pending = Column(String, default="false")
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db(database_url: str):
    global _engine, _Session
    _engine = create_engine(database_url, future=True)
    Base.metadata.create_all(_engine)
    _Session = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    return _engine


def get_session():
    if _Session is None:
        raise RuntimeError("DB not initialized. Call init_db() first.")
    return _Session()


def _to_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, "year"):
        return value
    return datetime.fromisoformat(str(value)).date()


def save_transactions(txns: Iterable[Dict[str, Any]]) -> int:
    session = get_session()
    count = 0
    try:
        for t in txns:
            categories = t.get("category") or []
            category = categories[0] if isinstance(categories, list) and categories else (categories if isinstance(categories, str) else None)
            row = Transaction(
                transaction_id=str(t.get("transaction_id") or t.get("id") or f"manual-{count}"),
                account_id=str(t.get("account_id", "")),
                name=t.get("name"),
                merchant_name=t.get("merchant_name"),
                amount=float(t.get("amount", 0.0)),
                iso_currency_code=t.get("iso_currency_code") or "USD",
                category=category,
                date=_to_date(t.get("date")),
                pending=str(t.get("pending", False)).lower(),
            )
            session.merge(row)
            count += 1
        session.commit()
    finally:
        session.close()
    return count


def fetch_transactions(limit: int = 100) -> List[Dict[str, Any]]:
    session = get_session()
    try:
        rows = session.query(Transaction).order_by(Transaction.date.desc()).limit(limit).all()
        return [
            {
                "transaction_id": r.transaction_id,
                "account_id": r.account_id,
                "name": r.name,
                "merchant_name": r.merchant_name,
                "amount": r.amount,
                "iso_currency_code": r.iso_currency_code,
                "category": r.category,
                "date": r.date.isoformat() if r.date else None,
                "pending": r.pending,
            }
            for r in rows
        ]
    finally:
        session.close()


def archive_old_transactions(cutoff_date) -> int:
    session = get_session()
    try:
        n = session.query(Transaction).filter(Transaction.date < cutoff_date).delete()
        session.commit()
        return n
    finally:
        session.close()
