"""Trial balance and rollup calculations."""

from __future__ import annotations

import datetime as dt
from collections import defaultdict
from typing import Dict, List

from sqlalchemy import func

from lifeos.domains.finance.models.accounting_models import Account, AccountCategory, JournalEntry, JournalLine
from lifeos.extensions import db


def _end_of_day(d: dt.date) -> dt.datetime:
    return dt.datetime.combine(d, dt.time.max)


def calculate_trial_balance(user_id: int, as_of: dt.date | None = None) -> Dict[int, Dict[str, float]]:
    """Return debit/credit totals per account up to as_of (inclusive)."""
    totals: Dict[int, Dict[str, float]] = defaultdict(lambda: {"debit": 0.0, "credit": 0.0})
    query = (
        db.session.query(JournalLine.account_id, func.sum(JournalLine.debit), func.sum(JournalLine.credit))
        .join(JournalEntry, JournalEntry.id == JournalLine.entry_id)
        .filter(JournalEntry.user_id == user_id)
    )
    if as_of:
        query = query.filter(JournalEntry.posted_at <= _end_of_day(as_of))
    query = query.group_by(JournalLine.account_id)
    for account_id, debit_sum, credit_sum in query.all():
        totals[account_id]["debit"] = float(debit_sum or 0)
        totals[account_id]["credit"] = float(credit_sum or 0)
    return totals


def period_balance(user_id: int, start_date: dt.date, end_date: dt.date) -> Dict[int, Dict[str, float]]:
    """Return debit/credit totals per account within date range inclusive."""
    totals: Dict[int, Dict[str, float]] = defaultdict(lambda: {"debit": 0.0, "credit": 0.0})
    query = (
        db.session.query(JournalLine.account_id, func.sum(JournalLine.debit), func.sum(JournalLine.credit))
        .join(JournalEntry, JournalEntry.id == JournalLine.entry_id)
        .filter(JournalEntry.user_id == user_id)
        .filter(JournalEntry.posted_at >= dt.datetime.combine(start_date, dt.time.min))
        .filter(JournalEntry.posted_at <= _end_of_day(end_date))
        .group_by(JournalLine.account_id)
    )
    for account_id, debit_sum, credit_sum in query.all():
        totals[account_id]["debit"] = float(debit_sum or 0)
        totals[account_id]["credit"] = float(credit_sum or 0)
    return totals


def monthly_rollup(user_id: int) -> Dict[str, Dict[str, float]]:
    """Aggregate debits/credits by YYYY-MM for the user."""
    query = (
        db.session.query(
            func.strftime("%Y-%m", JournalEntry.posted_at).label("ym"),
            func.sum(JournalLine.debit),
            func.sum(JournalLine.credit),
        )
        .join(JournalEntry, JournalEntry.id == JournalLine.entry_id)
        .filter(JournalEntry.user_id == user_id)
        .group_by("ym")
        .order_by("ym")
    )
    rollup: Dict[str, Dict[str, float]] = {}
    for ym, debit_sum, credit_sum in query.all():
        rollup[ym] = {"debit": float(debit_sum or 0), "credit": float(credit_sum or 0)}
    return rollup


def net_balance_for_account(account: Account, totals: Dict[int, Dict[str, float]]) -> float:
    """Compute net balance respecting account normal balance."""
    total = totals.get(account.id, {"debit": 0.0, "credit": 0.0})
    normal = (account.category.normal_balance if account.category else "debit") or "debit"
    if normal == "credit":
        return float(total["credit"] - total["debit"])
    return float(total["debit"] - total["credit"])


def trial_balance_view(user_id: int, as_of: dt.date | None = None) -> dict:
    totals = calculate_trial_balance(user_id, as_of=as_of)
    accounts: List[Account] = (
        Account.query.join(AccountCategory, isouter=True)
        .filter(Account.user_id == user_id)
        .order_by(Account.account_type.asc(), Account.category_id.asc().nullsfirst(), Account.code.asc().nullsfirst(), Account.name.asc())
        .all()
    )
    rows: List[dict] = []
    category_totals: Dict[tuple[str, int | None], Dict[str, float]] = defaultdict(lambda: {"debit": 0.0, "credit": 0.0, "net": 0.0})

    for acct in accounts:
        row_total = totals.get(acct.id, {"debit": 0.0, "credit": 0.0})
        net_val = net_balance_for_account(acct, totals)
        rows.append(
            {
                "account_id": acct.id,
                "account_name": acct.name,
                "account_code": acct.code,
                "base_type": acct.account_type,
                "category_id": acct.category.id if acct.category else None,
                "category_name": acct.category.name if acct.category else None,
                "normal_balance": acct.category.normal_balance if acct.category else "debit",
                "debit": row_total["debit"],
                "credit": row_total["credit"],
                "net": net_val,
            }
        )

        key = (acct.account_type, acct.category_id)
        category_totals[key]["debit"] += row_total["debit"]
        category_totals[key]["credit"] += row_total["credit"]
        category_totals[key]["net"] += net_val

    category_rows: List[dict] = []
    for (base_type, category_id), agg in category_totals.items():
        category_obj = next((acct.category for acct in accounts if acct.category_id == category_id and acct.account_type == base_type), None)
        category_rows.append(
            {
                "base_type": base_type,
                "category_id": category_id,
                "category_name": category_obj.name if category_obj else "Uncategorized",
                "normal_balance": category_obj.normal_balance if category_obj else "debit",
                "debit": agg["debit"],
                "credit": agg["credit"],
                "net": agg["net"],
            }
        )

    return {"accounts": rows, "categories": category_rows}
