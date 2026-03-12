from __future__ import annotations

from datetime import date, datetime

import pytest

import lifeos.core.insights.timeline_ingestor as timeline_ingestor_module
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.schemas import InterpretationDecisionRequest
from lifeos.core.insights.substrate_models import Interpretation, TimelineEvent
from lifeos.core.insights.substrate_service import (
    _extract_person_name,
    _infer_interaction_method,
    _materialize_reversible_plan,
    _parse_date,
    _parse_datetime,
    _source_object_ref,
    _timeline_event_id,
    _match_person,
    generate_interpretations_for_timeline_event,
)
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.relationships.models.person_models import Person
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def test_interpretation_decision_request_validation():
    payload = InterpretationDecisionRequest.model_validate({"action": "corrected", "notes": "x"})
    assert payload.action == "corrected"
    with pytest.raises(ValueError):
        InterpretationDecisionRequest.model_validate({"action": "approve"})
    with pytest.raises(ValueError):
        InterpretationDecisionRequest.model_validate({"action": None})


def test_substrate_helpers_parse_and_methods():
    now = datetime.utcnow()
    today = date.today()

    assert _parse_datetime(now) == now
    assert _parse_datetime(today).date() == today
    assert _parse_datetime("not-a-date") is None
    assert _parse_date(today) == today
    assert _parse_date(now) == now.date()
    assert _parse_date("bad") is None

    assert _infer_interaction_method("Call with Ada") == "call"
    assert _infer_interaction_method("Dinner with Ada") == "meal"
    assert _infer_interaction_method("Meeting with Ada") == "meeting"

    assert _extract_person_name("Meeting with Ada Lovelace") == "Ada Lovelace"
    assert _extract_person_name("Call Grace Hopper") == "Grace Hopper"
    assert _extract_person_name("No name here") is None


def test_substrate_helpers_object_ref_and_event_id():
    assert _source_object_ref("calendar.event.created", {"event_id": "c1"}) == "calendar_event:c1"
    assert _source_object_ref("journal.entry.created", {"entry_id": "j1"}) == "journal_entry:j1"
    assert _source_object_ref("finance.journal.posted", {"entry_id": "f1"}) == "finance_journal_entry:f1"
    assert _source_object_ref("calendar.event.created", {}) is None
    assert _source_object_ref("", {}) is None

    event = EventRecord(id=12, event_type="calendar.event.created", payload={"event_id": "c1"})
    assert _timeline_event_id(event) == "12"
    event.id = None
    assert _timeline_event_id(event) == "calendar.event.created:c1"


def test_substrate_helpers_match_person_and_reversible_plan(app):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="phase5a-helper@example.com",
                password="secret123",
                full_name="Phase 5a Helper",
                timezone="UTC",
            )
        )
        ada = Person(user_id=user.id, name="Ada Lovelace")
        grace = Person(user_id=user.id, name="Grace Hopper")
        db.session.add_all([ada, grace])
        db.session.commit()

        assert _match_person(user.id, "Ada Lovelace").id == ada.id
        assert _match_person(user.id, "Grace").id == grace.id
        assert _match_person(user.id, "Unknown") is None
        assert _materialize_reversible_plan([]) == {}
        assert _materialize_reversible_plan([{"action": "relationships.log_interaction", "interaction_id": 9}]) == {
            "action": "relationships.delete_interaction",
            "interaction_id": 9,
        }


def test_generate_interpretations_non_calendar_is_empty(app):
    with app.app_context():
        timeline_event = TimelineEvent(
            user_id=1,
            event_id="j1",
            source_domain="journal",
            event_type="journal.entry.created",
            timestamp_start=datetime.utcnow(),
            raw_payload={"entry_id": "j1"},
        )
        db.session.add(timeline_event)
        db.session.commit()

        assert generate_interpretations_for_timeline_event(timeline_event) == []


def test_timeline_ingestor_runtime_paths(monkeypatch, app):
    ingestor = timeline_ingestor_module.TimelineIngestor()

    class _BadCurrentApp:
        @property
        def config(self):
            raise RuntimeError("no app context")

    monkeypatch.setattr(timeline_ingestor_module, "current_app", _BadCurrentApp())
    monkeypatch.setenv("ENABLE_TIMELINE_INGESTION", "false")
    monkeypatch.setenv("ENABLE_INTERPRETATION_RELATIONSHIP", "false")
    assert ingestor.enabled is False
    assert ingestor.interpretations_enabled is False

    with app.app_context():
        monkeypatch.setattr(timeline_ingestor_module, "current_app", app)
        app.config["ENABLE_TIMELINE_INGESTION"] = True
        app.config["ENABLE_INTERPRETATION_RELATIONSHIP"] = True
        assert ingestor.enabled is True
        assert ingestor.interpretations_enabled is True

    subscribed = []

    def _capture_subscribe(event_type, handler):
        subscribed.append((event_type, handler))

    monkeypatch.setattr(timeline_ingestor_module.event_bus, "subscribe", _capture_subscribe)
    ingestor.register_subscriptions()
    assert len(subscribed) == len(timeline_ingestor_module.TIMELINE_EVENT_TYPES)

    called = {"ingest": 0, "generate": 0}

    def _fake_ingest(event):
        called["ingest"] += 1
        return object()

    def _fake_generate(_):
        called["generate"] += 1

    monkeypatch.setattr(timeline_ingestor_module, "ingest_timeline_event", _fake_ingest)
    monkeypatch.setattr(timeline_ingestor_module, "generate_interpretations_for_timeline_event", _fake_generate)
    with app.app_context():
        app.config["ENABLE_TIMELINE_INGESTION"] = True
        app.config["ENABLE_INTERPRETATION_RELATIONSHIP"] = True
        ingestor.on_event(EventRecord(event_type="calendar.event.created", payload={"event_id": "c1"}, user_id=1))
    assert called == {"ingest": 1, "generate": 1}

    with app.app_context():
        app.config["ENABLE_TIMELINE_INGESTION"] = False
        ingestor.on_event(EventRecord(event_type="calendar.event.created", payload={"event_id": "c2"}, user_id=1))
    assert called == {"ingest": 1, "generate": 1}


def test_legacy_controller_proposals_endpoints(app, client):
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="phase5a-legacy@example.com",
                password="secret123",
                full_name="Phase 5a Legacy",
                timezone="UTC",
            )
        )
        person = Person(user_id=user.id, name="Ada Lovelace")
        db.session.add(person)
        db.session.commit()

        timeline_event = TimelineEvent(
            user_id=user.id,
            event_id="calendar.event.created:c1",
            source_domain="calendar",
            event_type="calendar.event.created",
            timestamp_start=datetime.utcnow(),
            raw_payload={"event_id": "c1", "title": "Meeting with Ada Lovelace"},
        )
        db.session.add(timeline_event)
        db.session.commit()
        interpretations = generate_interpretations_for_timeline_event(timeline_event)
        assert len(interpretations) == 1
        interpretation = interpretations[0]

    from lifeos.core.auth.auth_service import issue_tokens

    with app.app_context():
        from lifeos.core.users.models import User

        persisted_user = User.query.filter_by(email="phase5a-legacy@example.com").first()
        assert persisted_user is not None
        tokens = issue_tokens(persisted_user)

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    list_resp = client.get("/api/insights/proposals", headers=headers)
    assert list_resp.status_code == 200

    with client.session_transaction() as sess:
        sess["_csrf_token"] = "legacy-csrf"
    decide_resp = client.patch(
        f"/api/insights/proposals/{interpretation.id}",
        json={"action": "accepted"},
        headers={"Authorization": f"Bearer {tokens['access_token']}", "X-CSRF-Token": "legacy-csrf"},
    )
    assert decide_resp.status_code == 200
