"""Phase 3a governance alignment tests."""

from __future__ import annotations

import pytest

from lifeos.core.events.semantic_contracts import EVENT_SEMANTIC_CONTRACTS
from lifeos.core.insights.contracts import INSIGHT_CONTRACTS
from lifeos.core.insights.routing import resolve_routing
from lifeos.readmodels.projections import INSIGHT_FEED_CONTRACT, REVIEW_QUEUE_CONTRACT

pytestmark = pytest.mark.unit


def test_projection_contracts_reference_semantic_events():
    for contract in (INSIGHT_FEED_CONTRACT, REVIEW_QUEUE_CONTRACT):
        missing = [evt for evt in contract.consumed_events if evt not in EVENT_SEMANTIC_CONTRACTS]
        assert missing == []


def test_confidence_routing_is_valid_for_contracts():
    for name, contract in INSIGHT_CONTRACTS.items():
        for band in contract.confidence_bands.keys():
            routing = resolve_routing(band)
            assert routing in contract.allowed_actions, f"{name} does not allow routing {routing}"
