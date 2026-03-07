"""Finance journal service."""

from __future__ import annotations

from datetime import datetime

from lifeos.domains.finance.events import FINANCE_TRANSACTION_CREATED
from lifeos.domains.finance.models.accounting_models import Transaction
from lifeos.domains.finance.services.accounting_service import post_journal_entry
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox


def record_transaction(
    user_id: int,
    amount: float,
    debit_account_id: int,
    credit_account_id: int,
    description: str,
):
    """Create a two-line journal entry for a transaction."""
    lines = [
        {
            "account_id": debit_account_id,
            "debit": amount,
            "credit": 0,
            "memo": description,
        },
        {
            "account_id": credit_account_id,
            "debit": 0,
            "credit": amount,
            "memo": description,
        },
    ]
    entry = post_journal_entry(
        user_id=user_id,
        description=description or f"Transaction {datetime.utcnow().isoformat()}",
        lines=lines,
    )
    txn = Transaction(
        user_id=user_id,
        amount=amount,
        description=(description or None),
        occurred_at=entry.posted_at,
        journal_entry_id=entry.id,
        source="manual",
    )
    db.session.add(txn)
    db.session.flush()
    enqueue_outbox(
        FINANCE_TRANSACTION_CREATED,
        {
            "transaction_id": txn.id,
            "user_id": user_id,
            "amount": float(amount),
            "description": description or None,
            "occurred_at": txn.occurred_at.isoformat() if txn.occurred_at else datetime.utcnow().isoformat(),
            "payload_version": "v1",
        },
        user_id=user_id,
    )
    db.session.commit()
    return entry
