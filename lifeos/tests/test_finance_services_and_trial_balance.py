import pytest

pytestmark = pytest.mark.integration

from lifeos.extensions import db
from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.finance.models.accounting_models import AccountCategory, Account
from lifeos.domains.finance.services.accounting_service import (
    create_account,
    create_custom_account_category,
    get_or_create_default_category,
    post_journal_entry,
)
from lifeos.domains.finance.services.trial_balance_service import trial_balance_view


@pytest.fixture
def user(app):
    with app.app_context():
        u = User(email="svc-tester@example.com", password_hash=hash_password("secret"))
        db.session.add(u)
        db.session.commit()
        return u


def test_create_account_normalizes_and_creates_category(app, user):
    with app.app_context():
        acct = create_account(
            user_id=user.id,
            name="  Cash   Savings  ",
            base_type="asset",
            account_subtype="bank",
            category_name_new="Operations",
        )

        assert acct.normalized_name == "cash savings"
        assert acct.category is not None
        assert acct.category.user_id == user.id
        assert acct.category.base_type == "asset"
        assert acct.category.normal_balance == "debit"
        assert acct.category.is_default is False

        # Idempotent by normalized name
        acct_again = create_account(
            user_id=user.id,
            name="cash savings",
            base_type="asset",
            account_subtype="bank",
            category_name_new="Operations",
        )
        assert acct_again.id == acct.id


def test_get_or_create_default_category_prefers_system_default(app, user):
    with app.app_context():
        system_default = AccountCategory(
            user_id=None,
            code="INCDEFAULT",
            name="Income Default",
            slug="income-default",
            base_type="income",
            normal_balance="credit",
            is_default=True,
            is_system=True,
        )
        db.session.add(system_default)
        db.session.commit()

        resolved = get_or_create_default_category(user.id, "income")
        assert resolved.id == system_default.id
        assert resolved.is_system is True


def test_trial_balance_groups_by_category_and_uncategorized(app, user):
    with app.app_context():
        cash_acct = create_account(
            user_id=user.id,
            name="Cash",
            base_type="asset",
            account_subtype="cash",
            category_name_new="Cash Ops",
        )

        uncategorized_expense = Account(
            user_id=user.id,
            name="Misc Expense",
            account_type="expense",
            account_subtype=None,
            normalized_name="misc expense",
            category_id=None,
            is_active=True,
        )
        db.session.add(uncategorized_expense)
        db.session.commit()

        post_journal_entry(
            user_id=user.id,
            description="Pay misc expense",
            lines=[
                {"account_id": uncategorized_expense.id, "debit": 50, "credit": 0},
                {"account_id": cash_acct.id, "debit": 0, "credit": 50},
            ],
        )

        view = trial_balance_view(user.id)
        categories = {(c["base_type"], c["category_id"]): c for c in view["categories"]}

        asset_row = categories.get(("asset", cash_acct.category_id))
        assert asset_row is not None
        assert asset_row["net"] == pytest.approx(-50.0)
        assert asset_row["category_name"] == cash_acct.category.name

        uncategorized_row = categories.get(("expense", None))
        assert uncategorized_row is not None
        assert uncategorized_row["category_name"] == "Uncategorized"
        assert uncategorized_row["net"] == pytest.approx(50.0)

        # Ensure accounts are reflected too
        account_ids = {row["account_id"] for row in view["accounts"]}
        assert cash_acct.id in account_ids
        assert uncategorized_expense.id in account_ids
