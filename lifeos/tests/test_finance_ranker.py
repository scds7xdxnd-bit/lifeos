"""Smoke tests for finance ranker adapters and logging."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.ml

from lifeos.core.events.event_models import EventRecord
from lifeos.domains.finance.events import FINANCE_ML_SUGGEST_ACCOUNTS
from lifeos.domains.finance.ml.ranker_client import (
    RANKER_MODEL_NAME,
    RANKER_MODEL_VERSION,
    RANKER_PAYLOAD_VERSION,
    predict_account,
)
from lifeos.domains.finance.models.accounting_models import Account, AccountCategory
from lifeos.domains.finance.services.suggestion_service import suggest_accounts
from lifeos.core.users.models import User
from lifeos.extensions import db


def _seed_accounts(user_id: int) -> None:
    category = AccountCategory(
        code="100",
        name="Assets",
        slug="assets",
        base_type="asset",
        normal_balance="debit",
        is_default=True,
        is_system=True,
    )
    db.session.add(category)
    db.session.flush()
    db.session.add_all(
        [
            Account(
                user_id=user_id,
                category_id=category.id,
                name="Cash",
                account_type="asset",
                normalized_name="cash",
                code="101",
            ),
            Account(
                user_id=user_id,
                category_id=category.id,
                name="Accounts Receivable",
                account_type="asset",
                normalized_name="accounts receivable",
                code="102",
            ),
        ]
    )
    db.session.commit()


def test_ranker_adapter_returns_metadata(app):
    with app.app_context():
        result = predict_account("coffee", [(1, "Cash"), (2, "Accounts Receivable")])
        assert result.suggestions and len(result.suggestions) == 2
        assert result.model == RANKER_MODEL_NAME
        assert result.model_version == RANKER_MODEL_VERSION
        assert result.payload_version == RANKER_PAYLOAD_VERSION
        assert result.context.get("candidate_count") == 2


def test_suggest_accounts_logs_event_with_versions(app):
    with app.app_context():
        user = User(email="user@example.com", password_hash="x")
        db.session.add(user)
        db.session.commit()
        _seed_accounts(user.id)

        suggestions = suggest_accounts(user.id, "coffee shop purchase")
        assert suggestions, "expected ranked suggestions from adapter"

        event = EventRecord.query.order_by(EventRecord.created_at.desc()).first()
        assert event is not None
        assert event.event_type == FINANCE_ML_SUGGEST_ACCOUNTS
        payload = event.payload
        assert payload.get("suggestions") == suggestions[:3]
        assert payload.get("model") == RANKER_MODEL_NAME
        assert payload.get("model_version") == RANKER_MODEL_VERSION
        assert payload.get("payload_version") == RANKER_PAYLOAD_VERSION
        assert payload.get("context", {}).get("candidate_count") == 2
