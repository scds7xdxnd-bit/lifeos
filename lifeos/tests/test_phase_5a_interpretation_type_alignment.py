"""Phase 5a interpretation type alignment tests."""

from __future__ import annotations

from datetime import datetime

import pytest

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.ml.phase5a_contracts import (
    INTERPRETATION_ACTIONS,
    INTERPRETATION_STATUSES,
    INTERPRETATION_TYPE_CONTRACTS,
)
from lifeos.core.insights.schemas import ALLOWED_INTERPRETATION_ACTIONS
from lifeos.core.insights.substrate_service import (
    generate_interpretations_for_timeline_event,
    ingest_timeline_event,
)
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.relationships.models.person_models import Person
from lifeos.extensions import db


def _calendar_payload(user_id: int, *, event_id: str, title: str) -> dict:
    return {
        "event_id": event_id,
        "title": title,
        "start_time": "2025-01-05T09:00:00",
        "end_time": "2025-01-05T10:00:00",
        "user_id": user_id,
    }


@pytest.mark.unit
def test_interpretation_actions_match_schema_constants():
    assert set(INTERPRETATION_ACTIONS) == set(ALLOWED_INTERPRETATION_ACTIONS)


@pytest.mark.unit
def test_required_interpretation_type_contract_exists():
    contract = INTERPRETATION_TYPE_CONTRACTS.get("calendar.relationship.interaction")
    assert contract is not None
    assert "relationships.log_interaction" in contract.proposed_write_actions
    assert "reversible_plan" in contract.required_fields
    assert contract.reversible_plan_required is True


@pytest.mark.unit
def test_optional_obligation_contract_has_no_writes():
    contract = INTERPRETATION_TYPE_CONTRACTS.get("calendar.obligation")
    if contract is None:
        pytest.skip("Optional obligation contract not present.")
    assert contract.proposed_write_actions == []
    assert contract.correction_fields == []


@pytest.mark.unit
def test_generated_interpretation_matches_contract(app):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="phase5a-alignment@example.com",
                password="secret123",
                full_name="Phase 5a Alignment",
                timezone="UTC",
            )
        )
        person = Person(user_id=user.id, name="Ada Lovelace")
        db.session.add(person)
        db.session.commit()

        payload = _calendar_payload(user.id, event_id="cal-123", title="Meeting with Ada Lovelace")
        timeline_event = ingest_timeline_event(
            EventRecord(
                event_type="calendar.event.created", payload=payload, user_id=user.id, created_at=datetime.utcnow()
            )
        )
        interpretations = generate_interpretations_for_timeline_event(timeline_event)

        assert len(interpretations) == 1
        interp = interpretations[0]
        contract = INTERPRETATION_TYPE_CONTRACTS[interp.interpretation_type]

        missing = [field for field in contract.required_fields if getattr(interp, field, None) in (None, "", [], {})]
        assert missing == []
        assert interp.status in INTERPRETATION_STATUSES
        assert contract.confidence_range[0] <= float(interp.confidence) <= contract.confidence_range[1]
        if contract.reversible_plan_required:
            assert interp.reversible_plan
            assert interp.reversible_plan.get("action") == "relationships.delete_interaction"
        assert interp.input_event_ids == [timeline_event.event_id]
        assert interp.proposed_writes
        for write in interp.proposed_writes:
            assert write.get("action") in contract.proposed_write_actions
