"""Receivable and loan group services."""

from __future__ import annotations

from datetime import date
from typing import List, Tuple

from lifeos.domains.finance.events import (
    FINANCE_RECEIVABLE_CREATED,
    FINANCE_RECEIVABLE_ENTRY_RECORDED,
)
from lifeos.domains.finance.models.receivable_models import (
    LoanGroup,
    LoanGroupLink,
    ReceivableManualEntry,
    ReceivableTracker,
)
from lifeos.extensions import db
from lifeos.platform.outbox import enqueue as enqueue_outbox


def create_receivable(
    user_id: int,
    *,
    counterparty: str,
    principal: float,
    start_date: date,
    due_date: date | None = None,
    interest_rate: float | None = None,
) -> ReceivableTracker:
    tracker = ReceivableTracker(
        user_id=user_id,
        counterparty=counterparty.strip(),
        principal=principal,
        start_date=start_date,
        due_date=due_date,
        interest_rate=interest_rate,
    )
    db.session.add(tracker)
    db.session.flush()
    enqueue_outbox(
        FINANCE_RECEIVABLE_CREATED,
        {
            "tracker_id": tracker.id,
            "user_id": user_id,
            "principal": float(principal),
            "counterparty": counterparty,
        },
        user_id=user_id,
    )
    db.session.commit()
    return tracker


def update_receivable(user_id: int, tracker_id: int, **fields) -> ReceivableTracker | None:
    tracker = ReceivableTracker.query.filter_by(id=tracker_id, user_id=user_id).first()
    if not tracker:
        return None
    for key in ("counterparty", "principal", "start_date", "due_date", "interest_rate"):
        if key in fields and fields[key] is not None:
            setattr(tracker, key, fields[key])
    db.session.commit()
    return tracker


def delete_receivable(user_id: int, tracker_id: int) -> bool:
    tracker = ReceivableTracker.query.filter_by(id=tracker_id, user_id=user_id).first()
    if not tracker:
        return False
    db.session.delete(tracker)
    db.session.commit()
    return True


def get_receivable(user_id: int, tracker_id: int) -> ReceivableTracker | None:
    return ReceivableTracker.query.filter_by(id=tracker_id, user_id=user_id).first()


def list_receivables(user_id: int, page: int = 1, per_page: int = 50) -> Tuple[List[ReceivableTracker], int]:
    query = ReceivableTracker.query.filter_by(user_id=user_id).order_by(ReceivableTracker.start_date.desc())
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def record_receivable_entry(
    user_id: int,
    tracker_id: int,
    amount: float,
    entry_date: date,
    memo: str | None = None,
) -> ReceivableManualEntry:
    tracker = ReceivableTracker.query.filter_by(id=tracker_id, user_id=user_id).first()
    if not tracker:
        raise ValueError("not_found")
    entry = ReceivableManualEntry(tracker_id=tracker_id, amount=amount, entry_date=entry_date, memo=memo)
    db.session.add(entry)
    db.session.flush()
    enqueue_outbox(
        FINANCE_RECEIVABLE_ENTRY_RECORDED,
        {
            "tracker_id": tracker_id,
            "amount": float(amount),
            "entry_date": entry_date.isoformat(),
            "user_id": user_id,
        },
        user_id=user_id,
    )
    db.session.commit()
    return entry


def list_receivable_entries(
    user_id: int, tracker_id: int, page: int = 1, per_page: int = 50
) -> Tuple[List[ReceivableManualEntry], int]:
    tracker = ReceivableTracker.query.filter_by(id=tracker_id, user_id=user_id).first()
    if not tracker:
        raise ValueError("not_found")
    query = ReceivableManualEntry.query.filter_by(tracker_id=tracker_id).order_by(
        ReceivableManualEntry.entry_date.desc()
    )
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def create_loan_group(user_id: int, name: str, description: str | None = None) -> LoanGroup:
    group = LoanGroup(
        user_id=user_id,
        name=name.strip(),
        description=(description or "").strip() or None,
    )
    db.session.add(group)
    db.session.commit()
    return group


def link_tracker_to_group(user_id: int, group_id: int, tracker_id: int) -> LoanGroupLink | None:
    group = LoanGroup.query.filter_by(id=group_id, user_id=user_id).first()
    tracker = ReceivableTracker.query.filter_by(id=tracker_id, user_id=user_id).first()
    if not group or not tracker:
        return None
    link = LoanGroupLink(group=group, tracker=tracker)
    db.session.add(link)
    db.session.commit()
    return link
