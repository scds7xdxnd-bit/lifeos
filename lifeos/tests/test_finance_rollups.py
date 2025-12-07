import pytest
from datetime import date

pytestmark = pytest.mark.integration

from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.finance.models.accounting_models import AccountCategory
from lifeos.domains.finance.services.accounting_service import create_account, post_journal_entry
from lifeos.domains.finance.services.schedule_service import add_schedule_row, recompute_daily_balances
from lifeos.domains.finance.services.trial_balance_service import calculate_trial_balance, net_balance_for_account
from lifeos.extensions import db


def test_trial_balance_and_net_balance(app):
    with app.app_context():
        user = create_user(UserCreateRequest(email="a@example.com", password="secret123", full_name="A", timezone="UTC"))
        asset = AccountCategory(
            code="1000",
            name="Cash",
            slug="cash",
            base_type="asset",
            normal_balance="debit",
            is_default=True,
            is_system=True,
        )
        revenue = AccountCategory(
            code="4000",
            name="Revenue",
            slug="revenue",
            base_type="income",
            normal_balance="credit",
            is_default=True,
            is_system=True,
        )
        db.session.add_all([asset, revenue])
        db.session.commit()

        cash = create_account(user.id, "Cash", "asset", category_id=asset.id)
        income = create_account(user.id, "Income", "income", category_id=revenue.id)
        entry = post_journal_entry(
            user.id,
            description="Sale",
            lines=[
                {"account_id": cash.id, "debit": 100, "credit": 0},
                {"account_id": income.id, "debit": 0, "credit": 100},
            ],
        )
        assert entry.is_balanced is True

        totals = calculate_trial_balance(user.id)
        assert net_balance_for_account(cash, totals) == 100
        assert net_balance_for_account(income, totals) == 100


def test_money_schedule_recompute(app):
    with app.app_context():
        user = create_user(UserCreateRequest(email="b@example.com", password="secret123", full_name="B", timezone="UTC"))
        category = AccountCategory(
            code="2000",
            name="Checking",
            slug="checking",
            base_type="asset",
            normal_balance="debit",
            is_default=True,
            is_system=True,
        )
        db.session.add(category)
        db.session.commit()
        account = create_account(user.id, "Checking", "asset", category_id=category.id)

        add_schedule_row(user.id, account.id, date.today(), 50)
        add_schedule_row(user.id, account.id, date.today(), -25)
        balances = recompute_daily_balances(user.id)
        today = str(date.today())
        assert balances[today] == 25
