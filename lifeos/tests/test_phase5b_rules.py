"""Phase 5b rule evaluation tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.rules import phase5b_rules
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.calendar.events import CALENDAR_EVENT_CREATED
from lifeos.domains.finance.events import FINANCE_TRANSACTION_CREATED
from lifeos.extensions import db

pytestmark = pytest.mark.integration

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "phase5b_insight_golden.json"


def _create_user(email: str = "phase5b@example.com"):
    return create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 5b Tester",
            timezone="UTC",
        )
    )


def _create_event(event_type: str, payload: dict, user_id: int, created_at: datetime) -> EventRecord:
    event = EventRecord(event_type=event_type, payload=payload, user_id=user_id, created_at=created_at)
    db.session.add(event)
    db.session.commit()
    return event


def test_phase5b_rules_emit_golden_insight(app):
    with app.app_context():
        app.config["ENABLE_PHASE5B_INSIGHTS"] = True
        app.config["PHASE5B_INSIGHT_TYPES"] = ["finance_calendar_obligation_risk"]
        user = _create_user(email="phase5b-golden@example.com")
        _create_event(
            FINANCE_TRANSACTION_CREATED,
            {"amount": -750.0, "occurred_at": "2025-01-09T12:00:00"},
            user.id,
            datetime(2025, 1, 9, 12, 0, 0),
        )
        calendar_event = _create_event(
            CALENDAR_EVENT_CREATED,
            {"title": "Rent payment", "start_time": "2025-01-10T22:00:00"},
            user.id,
            datetime(2025, 1, 10, 22, 0, 0),
        )

        insights = phase5b_rules.apply_rules(calendar_event)

        assert len(insights) == 1
        item = insights[0]
        expected = json.loads(FIXTURE_PATH.read_text())["insight"]

        assert item["type"] == expected["type"]
        assert item["message"] == expected["message"]
        assert item["severity"] == expected["severity"]
        assert item["priority"] == expected["priority"]
        assert item["delivery_policy"] == expected["delivery_policy"]
        assert item["context"]["obligation_count"] == expected["context"]["obligation_count"]
        assert item["context"]["spend_total"] == expected["context"]["spend_total"]
        assert item["context"]["window_days"] == expected["context"]["window_days"]
        assert item["context"]["window_end"] == expected["context"]["window_end"]
        assert item["context"]["feature_snapshot"] == expected["context"]["feature_snapshot"]
        assert item["context"]["detail"] == expected["context"]["detail"]
        assert item["context"]["confidence"] == pytest.approx(expected["context"]["confidence"], rel=1e-6)


def test_phase5b_rules_skip_duplicates(app):
    with app.app_context():
        app.config["ENABLE_PHASE5B_INSIGHTS"] = True
        app.config["PHASE5B_INSIGHT_TYPES"] = ["finance_calendar_obligation_risk"]
        user = _create_user(email="phase5b-duplicate@example.com")
        _create_event(
            FINANCE_TRANSACTION_CREATED,
            {"amount": -750.0, "occurred_at": "2025-01-09T12:00:00"},
            user.id,
            datetime(2025, 1, 9, 12, 0, 0),
        )
        calendar_event = _create_event(
            CALENDAR_EVENT_CREATED,
            {"title": "Rent payment", "start_time": "2025-01-10T22:00:00"},
            user.id,
            datetime(2025, 1, 10, 22, 0, 0),
        )

        window_end = "2025-01-10"
        db.session.add(
            InsightRecord(
                user_id=user.id,
                event_id=calendar_event.id,
                event_type=calendar_event.event_type,
                kind="finance_calendar_obligation_risk",
                message="existing",
                severity="info",
                data={"window_end": window_end, "window_days": 30},
                created_at=datetime(2025, 1, 10, 22, 5, 0),
            )
        )
        db.session.commit()

        insights = phase5b_rules.apply_rules(calendar_event)
        assert insights == []
