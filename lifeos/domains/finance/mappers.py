"""DTO ↔ model mappers for finance domain."""

from __future__ import annotations

from typing import List

from lifeos.domains.finance.models.receivable_models import (
    ReceivableManualEntry,
    ReceivableTracker,
)
from lifeos.domains.finance.schemas.finance_schemas import JournalEntryCreateRequest


def map_journal_entry_request(payload: JournalEntryCreateRequest) -> List[dict]:
    """Convert a journal entry request into service-ready line dicts."""
    return [
        {
            "account_id": line.account_id,
            "dc": line.dc,
            "amount": line.amount,
            "memo": line.memo,
        }
        for line in payload.lines
    ]


def map_receivable(tracker: ReceivableTracker) -> dict:
    return {
        "id": tracker.id,
        "counterparty": tracker.counterparty,
        "principal": float(tracker.principal),
        "start_date": tracker.start_date.isoformat() if tracker.start_date else None,
        "due_date": tracker.due_date.isoformat() if tracker.due_date else None,
        "interest_rate": (
            float(tracker.interest_rate) if tracker.interest_rate is not None else None
        ),
    }


def map_receivable_entry(entry: ReceivableManualEntry) -> dict:
    return {
        "id": entry.id,
        "tracker_id": entry.tracker_id,
        "entry_date": entry.entry_date.isoformat(),
        "amount": float(entry.amount),
        "memo": entry.memo,
    }
