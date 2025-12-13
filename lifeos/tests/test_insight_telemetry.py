import pytest

from lifeos.core.events.event_service import log_event
from lifeos.core.insights.telemetry import insight_telemetry
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user

pytestmark = pytest.mark.integration


def _make_user():
    return create_user(
        UserCreateRequest(
            email="telemetry@example.com",
            password="secret123",
            full_name="Telemetry User",
            timezone="UTC",
        )
    )


def test_insight_telemetry_tracks_generation_and_latency(app):
    with app.app_context():
        insight_telemetry.reset()
        user = _make_user()

        log_event(
            "finance.transaction.created",
            {"amount": 120, "category": "electronics"},
            user_id=user.id,
        )

        snapshot = insight_telemetry.snapshot()
        assert snapshot.events_processed == 1
        assert snapshot.events_with_insights == 1
        assert snapshot.total_insights >= 1
        assert snapshot.coverage == pytest.approx(1.0)
        assert snapshot.per_rule_counts.get("finance_rules", 0) >= 1
        assert snapshot.avg_latency_ms >= 0
        assert snapshot.per_rule_avg_latency_ms.get("finance_rules", 0) >= 0
