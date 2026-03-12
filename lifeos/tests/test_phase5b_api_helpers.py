from __future__ import annotations

import pytest

from lifeos.core.insights.api_v1 import (
    _default_idempotency_key,
    _feedback_event_type,
    _feedback_fingerprint,
)

pytestmark = pytest.mark.unit


def test_feedback_event_type_mapping():
    assert _feedback_event_type("dismiss") == "insight_dismissed"
    assert _feedback_event_type("act") == "insight_feedback_positive"
    assert _feedback_event_type("unknown") == "insight_dismissed"


def test_feedback_fingerprint_changes_with_context():
    base = _feedback_fingerprint(
        user_id=1,
        insight_id=10,
        insight_type="finance_calendar_obligation_risk",
        action="dismiss",
        context={"window_end": "2025-01-10", "window_days": 30},
        idempotency_key="a",
    )
    changed = _feedback_fingerprint(
        user_id=1,
        insight_id=10,
        insight_type="finance_calendar_obligation_risk",
        action="dismiss",
        context={"window_end": "2025-01-11", "window_days": 30},
        idempotency_key="a",
    )
    assert base != changed


def test_default_idempotency_key_is_stable():
    context = {"window_end": "2025-01-10", "window_days": 30}
    first = _default_idempotency_key(1, 10, "finance_calendar_obligation_risk", "dismiss", context)
    second = _default_idempotency_key(1, 10, "finance_calendar_obligation_risk", "dismiss", context)
    assert first == second
