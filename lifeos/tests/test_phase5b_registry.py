"""Phase 5b insight registry tests."""

from __future__ import annotations

import pytest

from lifeos.core.insights.contracts import INSIGHT_CONTRACTS
from lifeos.core.insights.registry import (
    PHASE5B_INSIGHT_DEFINITIONS,
    enabled_insight_types,
    get_enabled_insight_definitions,
)

pytestmark = pytest.mark.unit


def test_phase5b_definitions_minimum_count():
    assert len(PHASE5B_INSIGHT_DEFINITIONS) >= 5


def test_phase5b_definitions_have_contracts_and_feed_policy():
    for definition in PHASE5B_INSIGHT_DEFINITIONS:
        assert definition.insight_type in INSIGHT_CONTRACTS
        contract = INSIGHT_CONTRACTS[definition.insight_type]
        assert "display" in contract.allowed_actions
        assert definition.required_features
        assert definition.window_days > 0
        assert definition.delivery_policy == "feed"


def test_enabled_insight_types_respects_config_list():
    config = {"PHASE5B_INSIGHT_TYPES": ["finance_calendar_obligation_risk", "journal_habit_reflection_link"]}
    enabled = set(enabled_insight_types(config))
    assert enabled == {"finance_calendar_obligation_risk", "journal_habit_reflection_link"}

    definitions = {d.insight_type for d in get_enabled_insight_definitions(config)}
    assert definitions == enabled


def test_enabled_insight_types_respects_env_override(monkeypatch):
    monkeypatch.setenv("PHASE5B_INSIGHT_TYPES", "finance_calendar_obligation_risk,calendar_relationship_gap")
    enabled = enabled_insight_types()
    assert enabled == {"finance_calendar_obligation_risk", "calendar_relationship_gap"}
