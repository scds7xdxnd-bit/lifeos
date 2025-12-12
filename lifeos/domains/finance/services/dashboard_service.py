"""Finance dashboard aggregations."""

from __future__ import annotations

import datetime as dt
from typing import List

from lifeos.domains.finance.models.accounting_models import Account, Transaction
from lifeos.domains.finance.models.receivable_models import ReceivableTracker
from lifeos.domains.finance.models.schedule_models import (
    MoneyScheduleDailyBalance,
    MoneyScheduleRow,
)
from lifeos.domains.finance.services.trial_balance_service import (
    calculate_trial_balance,
    net_balance_for_account,
)


def get_dashboard(user_id: int) -> dict:
    # Balances per account
    accounts: List[Account] = (
        Account.query.filter_by(user_id=user_id)
        .order_by(Account.code.asc().nullsfirst(), Account.name.asc())
        .all()
    )
    totals = calculate_trial_balance(user_id)
    balance_rows = [
        {
            "account_id": acct.id,
            "name": acct.name,
            "code": acct.code,
            "balance": net_balance_for_account(acct, totals),
        }
        for acct in accounts
    ]

    # Recent transactions
    txns = (
        Transaction.query.filter_by(user_id=user_id)
        .order_by(Transaction.occurred_at.desc())
        .limit(10)
        .all()
    )
    recent_transactions = [
        {
            "id": t.id,
            "amount": float(t.amount),
            "description": t.description,
            "occurred_at": t.occurred_at.isoformat() if t.occurred_at else None,
            "journal_entry_id": t.journal_entry_id,
        }
        for t in txns
    ]

    # Upcoming schedule rows
    today = dt.date.today()
    rows = (
        MoneyScheduleRow.query.filter(
            MoneyScheduleRow.user_id == user_id, MoneyScheduleRow.event_date >= today
        )
        .order_by(MoneyScheduleRow.event_date.asc())
        .limit(10)
        .all()
    )
    upcoming_schedule = [
        {
            "id": r.id,
            "account_id": r.account_id,
            "event_date": r.event_date.isoformat(),
            "amount": float(r.amount),
            "memo": r.memo,
        }
        for r in rows
    ]

    # Receivables summary
    trackers = ReceivableTracker.query.filter_by(user_id=user_id).all()
    receivable_total = 0.0
    for t in trackers:
        entries_sum = sum(float(e.amount) for e in t.manual_entries)
        receivable_total += float(t.principal) + entries_sum

    # Forecast snapshot (7-day)
    balances = {
        row.as_of: float(row.balance)
        for row in MoneyScheduleDailyBalance.query.filter_by(user_id=user_id).all()
    }
    forecast: List[dict] = []
    running = 0.0
    for offset in range(7):
        day = today + dt.timedelta(days=offset)
        running += balances.get(day, 0.0)
        forecast.append(
            {"date": day.isoformat(), "projected_balance": round(running, 2)}
        )

    return {
        "accounts": balance_rows,
        "recent_transactions": recent_transactions,
        "upcoming_schedule": upcoming_schedule,
        "receivables_total": receivable_total,
        "forecast": forecast,
    }
