"""Finance journal service."""

from __future__ import annotations

from datetime import datetime

from lifeos.domains.finance.services.accounting_service import post_journal_entry


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
    return post_journal_entry(
        user_id=user_id,
        description=description or f"Transaction {datetime.utcnow().isoformat()}",
        lines=lines,
    )
