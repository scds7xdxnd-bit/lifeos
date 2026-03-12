"""Verify inference events are emitted with typed payloads and status."""

from __future__ import annotations

from lifeos.core.events.event_bus import event_bus
from lifeos.core.interpreter.inference_emitter import emit_inference_event
from lifeos.core.insights.ml.feedback_store import fetch_flagged_inference_events
from lifeos.core.insights.telemetry import insight_telemetry
from lifeos.lifeos_platform.outbox.services import dispatch_ready
from lifeos.extensions import db


def test_emit_inference_event_dispatches_typed_payload(app):
    received = []

    def handler(event):
        received.append(event)

    event_bus.subscribe("finance.transaction.inferred", handler)

    with app.app_context():
        emit_inference_event(
            domain="finance",
            record_type="transaction",
            user_id=1,
            calendar_event_id=42,
            confidence=0.81,
            inferred_data={"amount": 25.5, "currency": "USD", "description": "Coffee"},
            record_id=321,
            status="rejected",
            model_version="calendar-interpreter-v1",
            context={"source": "test"},
            is_false_positive=True,
        )
        db.session.commit()
        dispatch_ready()

    assert received, "Expected dispatched inference event"
    event = received[0]
    payload = event.payload
    assert payload["event_name"] == "finance.transaction.inferred"
    assert payload["status"] == "rejected"
    assert payload["payload_version"] == "v1"
    assert payload["model_version"] == "calendar-interpreter-v1"
    assert payload["is_false_positive"] is True
    assert payload["confidence_score"] == 0.81
    assert payload["inferred_structure"]["amount"] == 25.5
    assert payload["inferred_structure"]["currency"] == "USD"


def test_inference_emitter_updates_telemetry_with_error_flags(app):
    with app.app_context():
        insight_telemetry.reset()
        emit_inference_event(
            domain="health",
            record_type="workout",
            user_id=2,
            calendar_event_id=77,
            confidence=0.6,
            inferred_data={"workout_type": "run"},
            status="rejected",
            is_false_positive=True,
            model_version="calendar-interpreter-v1",
        )
        db.session.commit()
        snapshot = insight_telemetry.snapshot()
        assert snapshot.false_positives == 1
        assert snapshot.per_domain_false_positives.get("health") == 1
        assert snapshot.per_model_false_positives.get("calendar-interpreter-v1") == 1
        flagged = fetch_flagged_inference_events(domain="health", model_version="calendar-interpreter-v1", limit=10)
        assert flagged, "expected flagged inference events for retraining"
        assert flagged[0]["is_false_positive"] is True
        assert flagged[0]["payload"]["inferred_structure"]["workout_type"] == "run"
