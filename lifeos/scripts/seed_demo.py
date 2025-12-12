"""Seed demo data for LifeOS finance domain."""

from __future__ import annotations

from datetime import date

from lifeos import create_app
from lifeos.core.auth.models import Role
from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.finance.models.accounting_models import (
    Account,
    AccountCategory,
    JournalEntry,
    JournalLine,
    Transaction,
)
from lifeos.domains.finance.models.receivable_models import (
    ReceivableManualEntry,
    ReceivableTracker,
)
from lifeos.extensions import db


def seed_demo_user() -> User:
    user = User.query.filter_by(email="demo@lifeos.test").first()
    if not user:
        user = User(
            email="demo@lifeos.test",
            full_name="Demo User",
            password_hash=hash_password("demo12345"),
        )
        db.session.add(user)
        db.session.flush()
    # ensure finance:write role
    finance_role = Role.query.filter_by(name="finance:write").first()
    if finance_role and finance_role not in user.roles:
        user.roles.append(finance_role)
    db.session.commit()
    return user


def seed_accounts(user_id: int) -> tuple[list[AccountCategory], list[Account]]:
    categories = [
        AccountCategory(code="1000", name="Cash", normal_balance="debit"),
        AccountCategory(code="2000", name="Checking", normal_balance="debit"),
        AccountCategory(code="4000", name="Revenue", normal_balance="credit"),
        AccountCategory(code="5000", name="Expense", normal_balance="debit"),
    ]
    for cat in categories:
        if not AccountCategory.query.filter_by(code=cat.code).first():
            db.session.add(cat)
    db.session.flush()

    accounts = []
    acc_defs = [
        ("Cash", "1001"),
        ("Checking", "2001"),
        ("Sales Revenue", "4001"),
        ("Supplies Expense", "5001"),
    ]
    for name, code in acc_defs:
        existing = Account.query.filter_by(user_id=user_id, code=code).first()
        if not existing:
            cat = (
                categories[0]
                if "Cash" in name or "Checking" in name
                else categories[2 if "Revenue" in name else 3]
            )
            acc = Account(user_id=user_id, name=name, code=code, category=cat)
            db.session.add(acc)
            accounts.append(acc)
        else:
            accounts.append(existing)
    db.session.flush()
    return categories, accounts


def seed_journal_and_transactions(user_id: int, accounts: list[Account]) -> None:
    cash = next(a for a in accounts if a.name == "Cash")
    revenue = next(a for a in accounts if "Revenue" in a.name)
    expense = next(a for a in accounts if "Expense" in a.name)

    entry1 = JournalEntry(user_id=user_id, description="Demo sale")
    entry1.lines.append(
        JournalLine(account=cash, debit=500, credit=0, memo="Cash sale")
    )
    entry1.lines.append(
        JournalLine(account=revenue, debit=0, credit=500, memo="Revenue")
    )
    db.session.add(entry1)

    entry2 = JournalEntry(user_id=user_id, description="Buy supplies")
    entry2.lines.append(
        JournalLine(account=expense, debit=150, credit=0, memo="Supplies")
    )
    entry2.lines.append(
        JournalLine(account=cash, debit=0, credit=150, memo="Cash payment")
    )
    db.session.add(entry2)
    db.session.flush()

    txn1 = Transaction(
        user_id=user_id,
        amount=500,
        description="Sale",
        occurred_at=date.today(),
        journal_entry_id=entry1.id,
        category="Income",
    )
    txn2 = Transaction(
        user_id=user_id,
        amount=150,
        description="Supplies",
        occurred_at=date.today(),
        journal_entry_id=entry2.id,
        category="Expense",
    )
    db.session.add_all([txn1, txn2])


def seed_receivables(user_id: int) -> None:
    tracker = ReceivableTracker(
        user_id=user_id, counterparty="Alice", principal=300, start_date=date.today()
    )
    db.session.add(tracker)
    db.session.flush()
    db.session.add(
        ReceivableManualEntry(
            tracker_id=tracker.id,
            entry_date=date.today(),
            amount=50,
            memo="Partial payment",
        )
    )


def main():
    app = create_app()
    with app.app_context():
        user = seed_demo_user()
        _, accounts = seed_accounts(user.id)
        seed_journal_and_transactions(user.id, accounts)
        seed_receivables(user.id)
        db.session.commit()
        print("Seeded demo data for", user.email)


if __name__ == "__main__":
    main()
