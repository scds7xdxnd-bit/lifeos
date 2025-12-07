"""Finance HTML pages."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

from lifeos.domains.finance.models.accounting_models import Account, JournalEntry, Transaction
from lifeos.domains.finance.models.receivable_models import ReceivableManualEntry, ReceivableTracker
from lifeos.domains.finance.models.schedule_models import MoneyScheduleRow
from lifeos.domains.finance.services.trial_balance_service import calculate_trial_balance, net_balance_for_account

finance_pages_bp = Blueprint("finance_pages", __name__)


@finance_pages_bp.get("/")
@jwt_required(optional=True)
def dashboard():
    accounts = Account.query.limit(10).all()
    totals = calculate_trial_balance(accounts[0].user_id) if accounts else {}
    balances = {acct.id: net_balance_for_account(acct, totals) for acct in accounts}
    return render_template("finance/dashboard.html", accounts=accounts, balances=balances)


@finance_pages_bp.get("/accounts")
@jwt_required(optional=True)
def accounts_page():
    accounts = Account.query.all()
    totals = calculate_trial_balance(accounts[0].user_id) if accounts else {}
    balances = {acct.id: net_balance_for_account(acct, totals) for acct in accounts}
    return render_template("finance/accounts.html", accounts=accounts, balances=balances)


@finance_pages_bp.get("/transactions")
@jwt_required(optional=True)
def transactions_page():
    txns = Transaction.query.order_by(Transaction.occurred_at.desc()).limit(100).all()
    accounts = Account.query.all()
    return render_template("finance/transactions.html", transactions=txns, accounts=accounts)


@finance_pages_bp.get("/journal")
@jwt_required(optional=True)
def journal_page():
    entries = (
        JournalEntry.query.order_by(JournalEntry.posted_at.desc()).limit(50).all()
    )
    return render_template("finance/journal.html", entries=entries)


@finance_pages_bp.get("/trial-balance")
@jwt_required(optional=True)
def trial_balance_page():
    accounts = Account.query.all()
    user_id = accounts[0].user_id if accounts else None
    totals = calculate_trial_balance(user_id) if user_id else {}
    rows = [
        {
            "account": acct.name,
            "code": acct.code,
            "balance": net_balance_for_account(acct, totals),
        }
        for acct in accounts
    ]
    total_balance = sum(r["balance"] for r in rows)
    return render_template("finance/trial_balance.html", rows=rows, total=total_balance)


@finance_pages_bp.get("/receivables")
@jwt_required(optional=True)
def receivables_page():
    trackers = ReceivableTracker.query.all()
    trackers_ctx = []
    for t in trackers:
        entries = (
            ReceivableManualEntry.query.filter_by(tracker_id=t.id)
            .order_by(ReceivableManualEntry.entry_date.desc())
            .all()
        )
        trackers_ctx.append(
            {
                "tracker": t,
                "entries": entries,
                "balance": float(t.principal) + sum(float(e.amount) for e in entries),
            }
        )
    return render_template("finance/receivables.html", trackers=trackers_ctx)


@finance_pages_bp.get("/import")
@jwt_required(optional=True)
def import_page():
    accounts = Account.query.all()
    return render_template("finance/import.html", accounts=accounts)


@finance_pages_bp.get("/forecast")
@jwt_required(optional=True)
def forecast_page():
    accounts = Account.query.all()
    rows = MoneyScheduleRow.query.order_by(MoneyScheduleRow.event_date.asc()).limit(50).all()
    return render_template("finance/forecast.html", accounts=accounts, rows=rows)
