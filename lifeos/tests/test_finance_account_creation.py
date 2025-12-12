"""Unit tests for finance account search and inline creation services."""

import pytest
from datetime import datetime
from decimal import Decimal

pytestmark = pytest.mark.integration  # Uses database fixtures

from lifeos.extensions import db
from lifeos.domains.finance.models.accounting_models import Account, AccountCategory
from lifeos.domains.finance.services.accounting_service import (
    search_accounts,
    create_account_inline,
    get_account_subtypes,
    get_suggested_accounts,
    _normalize_name,
    VALID_ACCOUNT_TYPES,
    ACCOUNT_SUBTYPES_MAP,
)
from lifeos.domains.finance.events import FINANCE_ACCOUNT_CREATED
from lifeos.lifeos_platform.outbox.models import OutboxMessage


class TestNormalizeName:
    """Test _normalize_name utility function."""

    def test_lowercase_conversion(self):
        """Test that uppercase letters are converted to lowercase."""
        assert _normalize_name("CASH") == "cash"
        assert _normalize_name("My Savings") == "my savings"

    def test_whitespace_handling(self):
        """Test that whitespace is trimmed and deduplicated."""
        assert _normalize_name("  cash  ") == "cash"
        assert _normalize_name("my   savings   account") == "my savings account"

    def test_empty_string(self):
        """Test that empty string returns empty string."""
        assert _normalize_name("") == ""
        assert _normalize_name("   ") == ""


class TestAccountSubtypes:
    """Test get_account_subtypes function."""

    def test_valid_asset_subtypes(self):
        """Test getting subtypes for asset account type."""
        subtypes = get_account_subtypes("asset")
        assert isinstance(subtypes, list)
        assert len(subtypes) > 0
        assert "cash" in subtypes
        assert "bank" in subtypes
        assert "other" in subtypes

    def test_valid_liability_subtypes(self):
        """Test getting subtypes for liability account type."""
        subtypes = get_account_subtypes("liability")
        assert "loan" in subtypes
        assert "credit_card" in subtypes

    def test_all_account_types_have_subtypes(self):
        """Test that all valid account types have corresponding subtypes."""
        for account_type in VALID_ACCOUNT_TYPES:
            subtypes = get_account_subtypes(account_type)
            assert isinstance(subtypes, list)
            assert len(subtypes) > 0

    def test_invalid_account_type(self):
        """Test that invalid account type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            get_account_subtypes("invalid_type")
        assert str(exc_info.value) == "invalid_account_type"


class TestSearchAccounts:
    """Test search_accounts function."""

    @pytest.fixture
    def setup_accounts(self, app):
        """Create test accounts in database."""
        with app.app_context():
            category = AccountCategory.query.first()
            if not category:
                category = AccountCategory(
                    code="ASSET",
                    name="Assets",
                    slug="assets",
                    base_type="asset",
                    normal_balance="debit",
                    is_default=True,
                    is_system=True,
                )
                db.session.add(category)
                db.session.flush()

            user_id = 1

            # Create test accounts
            acc1 = Account(
                user_id=user_id,
                category_id=category.id,
                name="Cash",
                account_type="asset",
                account_subtype="cash",
                normalized_name="cash",
                is_active=True,
            )
            acc2 = Account(
                user_id=user_id,
                category_id=category.id,
                name="Checking Account",
                account_type="asset",
                account_subtype="bank",
                normalized_name="checking account",
                is_active=True,
            )
            acc3 = Account(
                user_id=user_id,
                category_id=category.id,
                name="Savings Account",
                account_type="asset",
                account_subtype="bank",
                normalized_name="savings account",
                is_active=True,
            )
            acc4 = Account(
                user_id=user_id,
                category_id=category.id,
                name="Inactive Account",
                account_type="asset",
                normalized_name="inactive account",
                is_active=False,
            )

            db.session.add_all([acc1, acc2, acc3, acc4])
            db.session.commit()

            yield {"user_id": user_id, "accounts": [acc1, acc2, acc3, acc4]}

    def test_search_by_prefix(self, app, setup_accounts):
        """Test searching accounts by prefix match."""
        with app.app_context():
            data = setup_accounts
            results = search_accounts(data["user_id"], "cash")
            assert len(results) >= 1
            assert results[0].name == "Cash"

    def test_search_by_substring(self, app, setup_accounts):
        """Test searching accounts by substring match."""
        with app.app_context():
            data = setup_accounts
            results = search_accounts(data["user_id"], "account")
            # Should match "Checking Account", "Savings Account"
            assert len(results) >= 2
            account_names = [r.name for r in results]
            assert "Checking Account" in account_names
            assert "Savings Account" in account_names

    def test_search_inactive_excluded(self, app, setup_accounts):
        """Test that inactive accounts are excluded from search."""
        with app.app_context():
            data = setup_accounts
            results = search_accounts(data["user_id"], "inactive")
            assert len(results) == 0

    def test_search_empty_query(self, app):
        """Test that empty query raises ValueError."""
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                search_accounts(1, "")
            assert str(exc_info.value) == "invalid_query"

    def test_search_query_too_long(self, app):
        """Test that overly long query raises ValueError."""
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                search_accounts(1, "x" * 101)
            assert str(exc_info.value) == "invalid_query"

    def test_search_limit(self, app, setup_accounts):
        """Test that search respects limit parameter."""
        with app.app_context():
            data = setup_accounts
            results = search_accounts(data["user_id"], "a", limit=1)
            assert len(results) <= 1


class TestCreateAccountInline:
    """Test create_account_inline function."""

    @pytest.fixture
    def setup_category(self, app):
        """Ensure a default category exists."""
        with app.app_context():
            category = AccountCategory.query.filter_by(code="ASSET").first()
            if not category:
                category = AccountCategory(
                    code="ASSET",
                    name="Assets",
                    slug="assets",
                    base_type="asset",
                    normal_balance="debit",
                    is_default=True,
                    is_system=True,
                )
                db.session.add(category)
                db.session.commit()
            yield category

    def test_create_account_success(self, app, setup_category):
        """Test successful account creation."""
        with app.app_context():
            account = create_account_inline(
                user_id=1,
                name="My Savings",
                account_type="asset",
                account_subtype="bank",
            )

            assert account.id is not None
            assert account.user_id == 1
            assert account.name == "My Savings"
            assert account.account_type == "asset"
            assert account.account_subtype == "bank"
            assert account.normalized_name == "my savings"
            assert account.is_active is True

    def test_create_account_emits_event(self, app, setup_category):
        """Test that creating an account emits an outbox event."""
        with app.app_context():
            account = create_account_inline(
                user_id=1,
                name="Test Account",
                account_type="liability",
                account_subtype="loan",
            )

            # Check that event was queued in outbox
            outbox_msg = OutboxMessage.query.filter_by(
                event_type=FINANCE_ACCOUNT_CREATED,
                user_id=1,
            ).first()

            assert outbox_msg is not None
            payload = outbox_msg.payload
            assert payload["account_id"] == account.id
            assert payload["user_id"] == 1
            assert payload["name"] == "Test Account"
            assert payload["account_type"] == "liability"
            assert payload["account_subtype"] == "loan"

    def test_create_account_idempotent(self, app, setup_category):
        """Test that creating the same account twice returns the existing one."""
        with app.app_context():
            account1 = create_account_inline(
                user_id=1,
                name="My Savings",
                account_type="asset",
                account_subtype="bank",
            )

            account2 = create_account_inline(
                user_id=1,
                name="My Savings",
                account_type="asset",
                account_subtype="bank",
            )

            # Should return same account
            assert account1.id == account2.id

    def test_create_account_normalized_name_match(self, app, setup_category):
        """Test that accounts with same normalized name are deduplicated."""
        with app.app_context():
            account1 = create_account_inline(
                user_id=1,
                name="My Savings",
                account_type="asset",
                account_subtype="bank",
            )

            # Try creating with different casing/whitespace
            account2 = create_account_inline(
                user_id=1,
                name="MY SAVINGS",
                account_type="asset",
                account_subtype="bank",
            )

            assert account1.id == account2.id

    def test_create_account_invalid_name(self, app, setup_category):
        """Test that empty or oversized names raise ValueError."""
        with app.app_context():
            # Empty name
            with pytest.raises(ValueError) as exc_info:
                create_account_inline(1, "", "asset", None)
            assert str(exc_info.value) == "invalid_name"

            # Oversized name
            with pytest.raises(ValueError) as exc_info:
                create_account_inline(1, "x" * 256, "asset", None)
            assert str(exc_info.value) == "invalid_name"

    def test_create_account_invalid_type(self, app, setup_category):
        """Test that invalid account type raises ValueError."""
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                create_account_inline(1, "Test", "invalid_type", None)
            assert str(exc_info.value) == "invalid_account_type"

    def test_create_account_invalid_subtype(self, app, setup_category):
        """Test that invalid account subtype raises ValueError."""
        with app.app_context():
            with pytest.raises(ValueError) as exc_info:
                create_account_inline(1, "Test", "asset", "invalid_subtype")
            assert str(exc_info.value) == "invalid_account_subtype"

    def test_create_account_with_subtype_none(self, app, setup_category):
        """Test creating account without subtype."""
        with app.app_context():
            account = create_account_inline(
                user_id=1,
                name="Test Account",
                account_type="expense",
                account_subtype=None,
            )

            assert account.account_subtype is None


class TestGetSuggestedAccounts:
    """Test get_suggested_accounts function (combining search + ML)."""

    @pytest.fixture
    def setup_accounts_for_suggestions(self, app):
        """Create test accounts for suggestion testing."""
        with app.app_context():
            category = AccountCategory.query.first()
            if not category:
                category = AccountCategory(
                    code="ASSET",
                    name="Assets",
                    slug="assets",
                    base_type="asset",
                    normal_balance="debit",
                    is_default=True,
                    is_system=True,
                )
                db.session.add(category)
                db.session.flush()

            user_id = 1

            acc1 = Account(
                user_id=user_id,
                category_id=category.id,
                name="Salary Income",
                account_type="income",
                normalized_name="salary income",
                is_active=True,
            )
            acc2 = Account(
                user_id=user_id,
                category_id=category.id,
                name="Freelance Income",
                account_type="income",
                normalized_name="freelance income",
                is_active=True,
            )

            db.session.add_all([acc1, acc2])
            db.session.commit()

            yield {"user_id": user_id}

    def test_get_suggested_accounts_existing(self, app, setup_accounts_for_suggestions):
        """Test getting suggestions returns existing accounts."""
        with app.app_context():
            data = setup_accounts_for_suggestions
            results = get_suggested_accounts(data["user_id"], "salary", limit=10, include_ml=False)

            assert len(results) >= 1
            assert results[0]["is_existing"] is True
            assert "salary" in results[0]["name"].lower()

    def test_get_suggested_accounts_format(self, app, setup_accounts_for_suggestions):
        """Test that suggestions have correct format."""
        with app.app_context():
            data = setup_accounts_for_suggestions
            results = get_suggested_accounts(data["user_id"], "income", limit=10)

            assert len(results) >= 1
            for result in results:
                assert "id" in result
                assert "name" in result
                assert "account_type" in result
                assert "account_subtype" in result
                assert "is_existing" in result
