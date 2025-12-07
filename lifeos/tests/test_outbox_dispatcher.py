from __future__ import annotations

from datetime import datetime, timedelta
import importlib

import pytest
from sqlalchemy.orm import Query

pytestmark = pytest.mark.integration

from lifeos.extensions import db
from lifeos.platform.outbox.models import OutboxMessage
from lifeos.platform.worker.config import DispatchConfig

# Expect the dispatcher module to exist; failing import should flag missing implementation.
try:
    dispatcher = importlib.import_module("lifeos.platform.worker.dispatcher")
except ImportError as exc:  # pragma: no cover - intentional hard failure to enforce presence
    raise AssertionError("Missing outbox dispatcher implementation at lifeos.platform.worker.dispatcher") from exc


def _config(**overrides) -> DispatchConfig:
    defaults = {
        "batch_size": 5,
        "poll_interval": 0,
        "max_attempts": 2,
        "backoff_seconds": 3,
        "backoff_multiplier": 2,
    }
    defaults.update(overrides)
    return DispatchConfig(**defaults)


def _enqueue(user_id: int = 1, event_type: str = "test.event", status: str = "pending", available_at: datetime | None = None) -> OutboxMessage:
    msg = OutboxMessage(
        user_id=user_id,
        event_type=event_type,
        payload={"hello": "world"},
        status=status,
        available_at=available_at or datetime.utcnow() - timedelta(seconds=1),
    )
    db.session.add(msg)
    db.session.commit()
    return msg


def test_successful_dispatch_marks_sent_and_increments_attempts(app):
    with app.app_context():
        msg = _enqueue()
        sent_ids: list[int] = []

        def _send(m: OutboxMessage):
            sent_ids.append(m.id)

        processed = dispatcher.process_ready_batch(_send, _config())

        db.session.refresh(msg)
        assert processed == 1
        assert sent_ids == [msg.id]
        assert msg.status == "sent"
        assert msg.attempts == 1
        assert msg.last_error is None


def test_claim_ready_messages_uses_skip_locked_and_reserves_once(app, monkeypatch):
    with app.app_context():
        first = _enqueue()
        second = _enqueue(event_type="another.event")

        skip_locked_flags: list[bool | None] = []
        original_with_for_update = Query.with_for_update

        def _wrapped_with_for_update(self, *args, **kwargs):
            skip_locked_flags.append(kwargs.get("skip_locked"))
            return original_with_for_update(self, *args, **kwargs)

        monkeypatch.setattr(Query, "with_for_update", _wrapped_with_for_update)

        claimed = dispatcher.claim_ready_messages(db.session, batch_size=1)
        db.session.commit()
        assert {m.id for m in claimed} == {first.id}
        assert claimed[0].status != "pending"  # moved to an in-flight state

        claimed_second = dispatcher.claim_ready_messages(db.session, batch_size=2)
        db.session.commit()
        claimed_ids = {m.id for m in claimed_second}
        assert first.id not in claimed_ids  # reserved via skip-locked claim
        assert second.id in claimed_ids
        assert True in skip_locked_flags  # dispatcher should request SKIP LOCKED


def test_failed_dispatch_applies_backoff_and_honors_max_attempts(app):
    with app.app_context():
        msg = _enqueue()
        cfg = _config(max_attempts=2, backoff_seconds=4, backoff_multiplier=2)

        def _send_fail(_):
            raise RuntimeError("boom")

        start = datetime.utcnow()
        dispatcher.process_ready_batch(_send_fail, cfg)
        db.session.refresh(msg)
        assert msg.attempts == 1
        assert msg.status in {"pending", "retry", "error"}
        assert msg.available_at >= start + timedelta(seconds=cfg.backoff_seconds)
        first_available = msg.available_at
        assert msg.last_error

        # Make available again to trigger final attempt
        msg.available_at = datetime.utcnow() - timedelta(seconds=1)
        db.session.commit()

        dispatcher.process_ready_batch(_send_fail, cfg)
        db.session.refresh(msg)
        assert msg.attempts == 2
        assert msg.status == "failed"
        assert msg.available_at >= first_available


def test_already_sent_message_is_not_dispatched_twice(app):
    with app.app_context():
        msg = _enqueue()
        sent_ids: list[int] = []

        dispatcher.process_ready_batch(lambda m: sent_ids.append(m.id), _config())
        db.session.refresh(msg)
        assert msg.status == "sent"
        assert sent_ids == [msg.id]

        def _should_not_run(_):
            raise AssertionError("duplicate dispatch attempted")

        dispatcher.process_ready_batch(_should_not_run, _config())
        db.session.refresh(msg)
        assert sent_ids == [msg.id]  # no additional dispatch
        assert msg.status == "sent"
