import pytest

pytestmark = [pytest.mark.integration, pytest.mark.ml]

from lifeos.core.events.event_service import log_event
from lifeos.core.insights.models import InsightRecord
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user


def _make_user():
    return create_user(
        UserCreateRequest(
            email="insight@example.com",
            password="secret123",
            full_name="Insight User",
            timezone="UTC",
        )
    )


def test_finance_event_creates_insight(app):
    with app.app_context():
        user = _make_user()
        log_event("finance.transaction.created", {"amount": 200, "category": "dining"}, user_id=user.id)
        assert InsightRecord.query.filter_by(user_id=user.id).count() >= 1


def test_cross_domain_sleep_spend_insight(app):
    with app.app_context():
        user = _make_user()
        # Low sleep metric logged first
        log_event("health.metric.updated", {"user_id": user.id, "metric": "sleep_hours", "value": 5.0}, user_id=user.id)
        # Trigger finance transaction
        log_event("finance.transaction.created", {"amount": 150, "category": "electronics"}, user_id=user.id)
        insight = InsightRecord.query.filter_by(user_id=user.id, kind="finance_sleep_spend").first()
        assert insight is not None
