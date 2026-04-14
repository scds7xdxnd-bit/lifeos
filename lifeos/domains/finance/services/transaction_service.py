"""Transaction query service — list and retrieve transactions."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from lifeos.domains.finance.models.accounting_models import JournalLine, Transaction
from lifeos.extensions import db


def list_transactions(
    user_id: int,
    *,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_id: Optional[int] = None,
    category: Optional[str] = None,
    counterparty: Optional[str] = None,
    currency_code: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    source: Optional[str] = None,
    include_void: bool = False,
    page: int = 1,
    per_page: int = 50,
) -> dict:
    """Return a paginated list of transactions for *user_id*.

    Supports optional filtering by date range, account involvement, category,
    counterparty, currency, amount range, source, and void status.

    Returns:
        {
            "items": [Transaction, ...],
            "total": int,
            "page": int,
            "per_page": int,
            "pages": int,
        }
    """
    query = Transaction.query.filter(Transaction.user_id == user_id)

    if not include_void:
        query = query.filter(Transaction.is_void.is_(False))

    if start_date:
        query = query.filter(Transaction.occurred_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Transaction.occurred_at <= datetime.combine(end_date, datetime.max.time()))

    if account_id is not None:
        # Filter to transactions whose journal entry contains this account
        entry_ids = db.session.query(JournalLine.entry_id).filter(JournalLine.account_id == account_id).subquery()
        query = query.filter(Transaction.journal_entry_id.in_(entry_ids))

    if category:
        query = query.filter(Transaction.category == category)
    if counterparty:
        query = query.filter(Transaction.counterparty.ilike(f"%{counterparty}%"))
    if currency_code:
        query = query.filter(Transaction.currency_code == currency_code)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    if source:
        query = query.filter(Transaction.source == source)

    query = query.order_by(Transaction.occurred_at.desc(), Transaction.id.desc())

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    pages = max(1, (total + per_page - 1) // per_page)

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


def get_transaction(user_id: int, transaction_id: int) -> Optional[Transaction]:
    """Fetch a single transaction belonging to *user_id*. Returns None if not found."""
    return Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
