from __future__ import annotations

import pytest
from pydantic import ValidationError

from lifeos.core.insights.schemas import InsightsFeedQuery, InterpretationDecisionRequest

pytestmark = pytest.mark.unit


def test_insights_feed_query_normalizes_domains_and_severity():
    query = InsightsFeedQuery.model_validate(
        {
            "domain": ["finance, calendar", "health"],
            "severity": " INFO ",
            "status": "confirmed",
        }
    )
    assert query.domain == ["finance", "calendar", "health"]
    assert query.severity == "info"
    assert query.status == "confirmed"


def test_insights_feed_query_rejects_invalid_status():
    with pytest.raises(ValidationError):
        InsightsFeedQuery.model_validate({"status": "invalid-status"})


def test_interpretation_decision_request_rejects_invalid_action():
    with pytest.raises(ValidationError):
        InterpretationDecisionRequest.model_validate({"action": "approve"})
