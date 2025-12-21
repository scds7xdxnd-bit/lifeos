"""Phase 3a read-only projection contract checks."""

from __future__ import annotations

import pytest

from lifeos.readmodels.projections import INSIGHT_FEED_CONTRACT, REVIEW_QUEUE_CONTRACT
from lifeos.readmodels.registry_impl import DefaultReadModelRegistry

pytestmark = pytest.mark.unit


def test_default_registry_exposes_phase_3a_projections():
    registry = DefaultReadModelRegistry()
    names = {contract.name for contract in registry.list()}
    assert names == {"insight_feed", "insight_review_queue"}
    assert registry.get("insight_feed") is INSIGHT_FEED_CONTRACT
    assert registry.get("insight_review_queue") is REVIEW_QUEUE_CONTRACT


def test_projection_contracts_are_timeline_and_event_idempotent():
    for contract in (INSIGHT_FEED_CONTRACT, REVIEW_QUEUE_CONTRACT):
        assert contract.type == "timeline"
        assert contract.idempotency_key == "event_id"
        assert contract.domain == "insights"
