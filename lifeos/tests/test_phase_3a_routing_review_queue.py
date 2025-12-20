"""Phase 3a routing persistence and review queue projection tests."""

from __future__ import annotations

import pytest

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.services import persist_insights
from lifeos.core.users.models import User
from lifeos.extensions import db
from lifeos.readmodels.projections.review_queue import fetch_review_queue_projection

pytestmark = pytest.mark.integration


def _create_user() -> User:
    user = User(email="phase3a-review@example.com", password_hash="test")
    db.session.add(user)
    db.session.flush()
    return user


def test_persist_insights_sets_confidence_and_routing(app):
    user = _create_user()
    event = EventRecord(
        event_type="finance.transaction.created",
        payload={"amount": 25.0, "category": "Groceries"},
        user_id=user.id,
    )
    db.session.add(event)
    db.session.flush()

    insights = [
        {
            "type": "finance_spend",
            "message": "Recorded spending of 25.0 in Groceries",
            "severity": "info",
            "context": {},
        }
    ]
    saved = persist_insights(insights, event)

    assert len(saved) == 1
    rec = saved[0]
    assert rec.confidence_band == "informational"
    assert rec.routing == "display"
    assert rec.data.get("confidence_band") == "informational"
    assert rec.data.get("routing") == "display"


def test_review_queue_projection_filters_and_uses_fallback(app):
    user = _create_user()

    review_band = InsightRecord(
        user_id=user.id,
        event_id=None,
        event_type="finance.transaction.inferred",
        kind="finance_spend",
        message="Review band",
        severity="info",
        confidence_band="needs_review",
        routing="review_only",
        data={},
    )
    fallback_band = InsightRecord(
        user_id=user.id,
        event_id=None,
        event_type="habits.habit.inferred",
        kind="habit_progress",
        message="Fallback band",
        severity="info",
        confidence_band=None,
        routing=None,
        data={"confidence_band": "needs_review"},
    )
    fallback_routing = InsightRecord(
        user_id=user.id,
        event_id=None,
        event_type="skills.practice.inferred",
        kind="skill_practice",
        message="Fallback routing",
        severity="info",
        confidence_band=None,
        routing=None,
        data={"routing": "review_only"},
    )
    ignore = InsightRecord(
        user_id=user.id,
        event_id=None,
        event_type="finance.transaction.created",
        kind="finance_spend",
        message="Ignore",
        severity="info",
        confidence_band="informational",
        routing="display",
        data={},
    )
    db.session.add_all([review_band, fallback_band, fallback_routing, ignore])
    db.session.flush()

    results = fetch_review_queue_projection(user.id, limit=10, offset=0)
    ids = {rec.id for rec in results}

    assert review_band.id in ids
    assert fallback_band.id in ids
    assert fallback_routing.id in ids
    assert ignore.id not in ids
