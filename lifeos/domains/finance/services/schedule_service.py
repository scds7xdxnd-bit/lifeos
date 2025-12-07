"""Money schedule service."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Dict, List, Tuple

from lifeos.domains.finance.events import (
    FINANCE_SCHEDULE_CREATED,
    FINANCE_SCHEDULE_UPDATED,
    FINANCE_SCHEDULE_DELETED,
    FINANCE_SCHEDULE_RECOMPUTED,
)
from lifeos.domains.finance.models.accounting_models import Account
from lifeos.domains.finance.models.schedule_models import MoneyScheduleDailyBalance, MoneyScheduleRow
from lifeos.extensions import db
from lifeos.platform.outbox import enqueue as enqueue_outbox


def _validate_account(user_id: int, account_id: int) -> None:
    acct = Account.query.filter_by(id=account_id, user_id=user_id).first()
    if not acct or not acct.is_active:
        raise ValueError("not_found")


def add_schedule_row(user_id: int, account_id: int, event_date: date, amount: float, memo: str | None = None) -> MoneyScheduleRow:
    _validate_account(user_id, account_id)
    row = MoneyScheduleRow(user_id=user_id, account_id=account_id, event_date=event_date, amount=amount, memo=memo)
    db.session.add(row)
    db.session.flush()
    enqueue_outbox(
        FINANCE_SCHEDULE_CREATED,
        {"row_id": row.id, "user_id": user_id, "amount": float(amount), "account_id": account_id, "event_date": event_date.isoformat()},
        user_id=user_id,
    )
    db.session.commit()
    return row


def update_schedule_row(user_id: int, row_id: int, **fields) -> MoneyScheduleRow | None:
    row = MoneyScheduleRow.query.filter_by(id=row_id, user_id=user_id).first()
    if not row:
        return None
    if "account_id" in fields and fields["account_id"] is not None:
        _validate_account(user_id, int(fields["account_id"]))
    for key in ("account_id", "event_date", "amount", "memo"):
        if key in fields and fields[key] is not None:
            setattr(row, key, fields[key])

    payload_fields: dict[str, object] = {}
    for k, v in fields.items():
        if v is None:
            continue
        if isinstance(v, date):
            payload_fields[k] = v.isoformat()
        elif isinstance(v, (float, int)):
            payload_fields[k] = float(v)
        else:
            payload_fields[k] = v

    enqueue_outbox(
        FINANCE_SCHEDULE_UPDATED,
        {"row_id": row.id, "user_id": user_id, "fields": payload_fields},
        user_id=user_id,
    )
    db.session.commit()
    return row


def delete_schedule_row(user_id: int, row_id: int) -> bool:
    row = MoneyScheduleRow.query.filter_by(id=row_id, user_id=user_id).first()
    if not row:
        return False
    db.session.delete(row)
    enqueue_outbox(FINANCE_SCHEDULE_DELETED, {"row_id": row_id, "user_id": user_id}, user_id=user_id)
    db.session.commit()
    return True


def list_schedule_rows(user_id: int) -> List[MoneyScheduleRow]:
    return MoneyScheduleRow.query.filter_by(user_id=user_id).order_by(MoneyScheduleRow.event_date.asc()).all()


def recompute_daily_balances(user_id: int) -> Dict[str, float]:
    """Aggregate scheduled events into daily balances."""
    rows = MoneyScheduleRow.query.filter_by(user_id=user_id).all()
    totals: Dict[str, float] = defaultdict(float)
    for row in rows:
        totals[str(row.event_date)] += float(row.amount)
    MoneyScheduleDailyBalance.query.filter_by(user_id=user_id).delete()
    for date_str, amount in totals.items():
        db.session.add(MoneyScheduleDailyBalance(user_id=user_id, as_of=date.fromisoformat(date_str), balance=amount))
    db.session.commit()
    enqueue_outbox(FINANCE_SCHEDULE_RECOMPUTED, {"user_id": user_id, "days": len(totals)}, user_id=user_id)
    return totals
