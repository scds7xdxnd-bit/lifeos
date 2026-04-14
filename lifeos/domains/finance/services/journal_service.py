"""Finance journal service.

Transaction lifecycle decisions:
- **Hybrid mutability**: metadata fields (description, counterparty, category,
  occurred_at) may be edited in-place within a 24-hour grace period after
  creation. After 24h the transaction is immutable.
- **Amount / account changes**: always void + re-enter. This preserves the
  double-entry audit trail regardless of timing.
- **Void**: creates a mirror reversal journal entry (each debit becomes a
  credit and vice-versa) and marks the original Transaction.is_void = True.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from lifeos.domains.finance.events import (
    FINANCE_TRANSACTION_CREATED,
    FINANCE_TRANSACTION_EDITED,
    FINANCE_TRANSACTION_VOIDED,
)
from lifeos.domains.finance.models.accounting_models import (
    JournalEntry,
    Transaction,
)
from lifeos.domains.finance.services.accounting_service import post_journal_entry
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox

_GRACE_HOURS = 24
_TRANSFER_TYPES = {"asset", "liability"}


# ---------------------------------------------------------------------------
# Simple two-account transaction
# ---------------------------------------------------------------------------


def record_transaction(
    user_id: int,
    amount: float,
    debit_account_id: int,
    credit_account_id: int,
    description: str,
    currency_code: Optional[str] = None,
    occurred_at: Optional[datetime] = None,
    counterparty: Optional[str] = None,
    category: Optional[str] = None,
) -> JournalEntry:
    """Create a two-line balanced journal entry for a transaction."""
    lines = [
        {
            "account_id": debit_account_id,
            "debit": amount,
            "credit": 0,
            "memo": description,
            "currency_code": currency_code,
        },
        {
            "account_id": credit_account_id,
            "debit": 0,
            "credit": amount,
            "memo": description,
            "currency_code": currency_code,
        },
    ]
    posted_at = occurred_at or datetime.utcnow()
    entry = post_journal_entry(
        user_id=user_id,
        description=description or f"Transaction {posted_at.isoformat()}",
        lines=lines,
        posted_at=posted_at,
    )
    txn = Transaction(
        user_id=user_id,
        amount=amount,
        currency_code=currency_code,
        description=description or None,
        occurred_at=posted_at,
        journal_entry_id=entry.id,
        source="manual",
        counterparty=counterparty,
        category=category,
        is_void=False,
    )
    db.session.add(txn)
    db.session.flush()
    enqueue_outbox(
        FINANCE_TRANSACTION_CREATED,
        {
            "transaction_id": txn.id,
            "user_id": user_id,
            "amount": float(amount),
            "currency_code": currency_code,
            "description": description or None,
            "counterparty": counterparty,
            "category": category,
            "occurred_at": posted_at.isoformat(),
            "source": "manual",
            "payload_version": "v2",
        },
        user_id=user_id,
    )
    db.session.commit()
    return entry


# ---------------------------------------------------------------------------
# Split transaction (one source, N expense accounts)
# ---------------------------------------------------------------------------


def record_split_transaction(
    user_id: int,
    credit_account_id: int,
    total_amount: float,
    split_lines: list[dict],
    description: Optional[str] = None,
    currency_code: Optional[str] = None,
    occurred_at: Optional[datetime] = None,
    counterparty: Optional[str] = None,
) -> JournalEntry:
    """Create a multi-debit journal entry for a split transaction.

    split_lines: list of {account_id, amount, memo?}
    The sum of split amounts must equal total_amount (tolerance 0.005).
    """
    split_total = sum(Decimal(str(line["amount"])) for line in split_lines)
    total_dec = Decimal(str(total_amount))
    if abs(split_total - total_dec) > Decimal("0.005"):
        raise ValueError("split_amounts_do_not_balance")

    posted_at = occurred_at or datetime.utcnow()
    desc = description or f"Split transaction {posted_at.isoformat()}"

    lines: list[dict] = []
    for leg in split_lines:
        lines.append(
            {
                "account_id": leg["account_id"],
                "debit": float(Decimal(str(leg["amount"]))),
                "credit": 0,
                "memo": leg.get("memo") or description,
                "currency_code": currency_code,
            }
        )
    lines.append(
        {
            "account_id": credit_account_id,
            "debit": 0,
            "credit": float(total_dec),
            "memo": description,
            "currency_code": currency_code,
        }
    )

    entry = post_journal_entry(
        user_id=user_id,
        description=desc,
        lines=lines,
        posted_at=posted_at,
    )
    txn = Transaction(
        user_id=user_id,
        amount=float(total_dec),
        currency_code=currency_code,
        description=description or None,
        occurred_at=posted_at,
        journal_entry_id=entry.id,
        source="manual",
        counterparty=counterparty,
        is_void=False,
    )
    db.session.add(txn)
    db.session.flush()
    enqueue_outbox(
        FINANCE_TRANSACTION_CREATED,
        {
            "transaction_id": txn.id,
            "user_id": user_id,
            "amount": float(total_dec),
            "currency_code": currency_code,
            "description": description or None,
            "counterparty": counterparty,
            "occurred_at": posted_at.isoformat(),
            "source": "manual",
            "payload_version": "v2",
        },
        user_id=user_id,
    )
    db.session.commit()
    return entry


# ---------------------------------------------------------------------------
# Transfer between own accounts
# ---------------------------------------------------------------------------


def record_transfer(
    user_id: int,
    from_account_id: int,
    to_account_id: int,
    amount: float,
    description: Optional[str] = None,
    currency_code: Optional[str] = None,
    occurred_at: Optional[datetime] = None,
) -> JournalEntry:
    """Move funds between two of the user's own accounts.

    Both accounts must be of type 'asset' or 'liability'. No income/expense
    accounts are involved — this is a pure balance sheet transfer.
    Raises ValueError('invalid_transfer_accounts') if either account has the
    wrong type or does not belong to the user.
    """
    from lifeos.domains.finance.models.accounting_models import Account

    from_acct = Account.query.filter_by(id=from_account_id, user_id=user_id).first()
    to_acct = Account.query.filter_by(id=to_account_id, user_id=user_id).first()
    if not from_acct or not to_acct:
        raise ValueError("not_found")
    if from_acct.account_type not in _TRANSFER_TYPES or to_acct.account_type not in _TRANSFER_TYPES:
        raise ValueError("invalid_transfer_accounts")

    desc = description or f"Transfer to {to_acct.name}"
    return record_transaction(
        user_id=user_id,
        amount=amount,
        debit_account_id=to_account_id,
        credit_account_id=from_account_id,
        description=desc,
        currency_code=currency_code,
        occurred_at=occurred_at,
    )


# ---------------------------------------------------------------------------
# In-grace-period edit (metadata only)
# ---------------------------------------------------------------------------


def edit_transaction(
    user_id: int,
    transaction_id: int,
    *,
    description: Optional[str] = None,
    counterparty: Optional[str] = None,
    category: Optional[str] = None,
    occurred_at: Optional[datetime] = None,
) -> Transaction:
    """Edit metadata fields within the 24-hour grace period.

    Raises:
      - ValueError('not_found') — transaction does not exist / wrong user
      - ValueError('already_void') — transaction has been voided
      - ValueError('grace_period_expired') — more than 24h since creation
    """
    txn = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    if txn is None:
        raise ValueError("not_found")
    if txn.is_void:
        raise ValueError("already_void")

    now = datetime.utcnow()
    created_at = txn.occurred_at or now
    if (now - created_at) > timedelta(hours=_GRACE_HOURS):
        raise ValueError("grace_period_expired")

    changed_fields: list[str] = []
    if description is not None and description != txn.description:
        txn.description = description
        changed_fields.append("description")
    if counterparty is not None and counterparty != txn.counterparty:
        txn.counterparty = counterparty
        changed_fields.append("counterparty")
    if category is not None and category != txn.category:
        txn.category = category
        changed_fields.append("category")
    if occurred_at is not None and occurred_at != txn.occurred_at:
        txn.occurred_at = occurred_at
        changed_fields.append("occurred_at")

    if not changed_fields:
        return txn

    txn.edited_at = now
    db.session.flush()
    enqueue_outbox(
        FINANCE_TRANSACTION_EDITED,
        {
            "transaction_id": txn.id,
            "user_id": user_id,
            "changed_fields": changed_fields,
            "edited_at": now.isoformat(),
            "payload_version": "v1",
        },
        user_id=user_id,
    )
    db.session.commit()
    return txn


# ---------------------------------------------------------------------------
# Void (reversal journal entry)
# ---------------------------------------------------------------------------


def void_transaction(
    user_id: int,
    transaction_id: int,
    reason: Optional[str] = None,
) -> tuple[Transaction, JournalEntry]:
    """Void a transaction by creating a mirror reversal journal entry.

    The original transaction is marked is_void=True. A new Transaction record
    is created representing the reversal with void_of_id pointing to the
    original. The reversal journal entry swaps all debits ↔ credits.

    Raises:
      - ValueError('not_found') — transaction does not exist / wrong user
      - ValueError('already_void') — already voided
    """
    txn = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
    if txn is None:
        raise ValueError("not_found")
    if txn.is_void:
        raise ValueError("already_void")

    original_entry = txn.journal_entry
    if original_entry is None:
        raise ValueError("no_journal_entry")

    now = datetime.utcnow()
    desc = reason or f"Void of transaction #{transaction_id}"

    # Build reversal lines (swap debit ↔ credit)
    reversal_lines: list[dict] = []
    for line in original_entry.lines:
        reversal_lines.append(
            {
                "account_id": line.account_id,
                "debit": float(line.credit or 0),
                "credit": float(line.debit or 0),
                "memo": desc,
                "currency_code": line.currency_code,
            }
        )

    reversal_entry = post_journal_entry(
        user_id=user_id,
        description=desc,
        lines=reversal_lines,
        posted_at=now,
    )

    # Mark original void
    txn.is_void = True
    db.session.flush()

    # Create a reversal Transaction record for full auditability
    reversal_txn = Transaction(
        user_id=user_id,
        amount=float(txn.amount),
        currency_code=txn.currency_code,
        description=desc,
        occurred_at=now,
        journal_entry_id=reversal_entry.id,
        source=txn.source,
        is_void=True,
        void_of_id=txn.id,
    )
    db.session.add(reversal_txn)
    db.session.flush()

    enqueue_outbox(
        FINANCE_TRANSACTION_VOIDED,
        {
            "transaction_id": txn.id,
            "reversal_entry_id": reversal_entry.id,
            "user_id": user_id,
            "reason": reason,
            "voided_at": now.isoformat(),
            "payload_version": "v1",
        },
        user_id=user_id,
    )
    db.session.commit()
    return txn, reversal_entry
