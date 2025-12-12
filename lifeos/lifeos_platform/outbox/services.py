"""Outbox dispatcher service and bus adapter."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Sequence, Set

from sqlalchemy import or_

from lifeos.core.events.event_bus import event_bus
from lifeos.core.events.event_models import EventRecord
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox.models import OutboxMessage

STATUS_PENDING = "pending"
STATUS_SENDING = "sending"
STATUS_SENT = "sent"
STATUS_RETRY = "retry"
STATUS_FAILED = "failed"
STATUS_DEAD = "dead"

MAX_DISPATCH_ATTEMPTS = 5
DEFAULT_RETRY_IN = timedelta(minutes=5)


class EventBusAdapter:
    """Adapter to publish outbox messages to the in-process bus (swap for broker later)."""

    def __init__(self, bus=None) -> None:
        self.bus = bus or event_bus
        self._delivered: Set[int] = set()

    def dispatch(self, message: OutboxMessage) -> None:
        external_id = f"{message.event_type}:{message.id}"
        payload = dict(message.payload or {})
        payload.setdefault("external_id", external_id)
        payload.setdefault("event_id", message.id)

        event = EventRecord(
            event_type=message.event_type,
            payload=payload,
            user_id=message.user_id,
        )
        event.id = message.id
        event.created_at = message.created_at

        if event.id in self._delivered:
            return
        self.bus.publish(event)
        self._delivered.add(event.id)


def enqueue(
    event_name: str,
    payload: dict,
    user_id: Optional[int],
    available_at: Optional[datetime] = None,
) -> OutboxMessage:
    """
    Stage an event in the outbox. Caller should commit alongside domain changes.
    """
    message = OutboxMessage(
        event_type=event_name,
        payload=payload or {},
        user_id=user_id,
        available_at=available_at or datetime.utcnow(),
        status=STATUS_PENDING,
        attempts=0,
    )
    db.session.add(message)
    return message


def dequeue_batch(
    limit: int = 50, user_id: Optional[int] = None
) -> List[OutboxMessage]:
    """
    Lock and return ready messages (pending or retryable failed). Marks them as sending.
    """
    now = datetime.utcnow()
    query = OutboxMessage.query.filter(
        OutboxMessage.available_at <= now,
        or_(
            OutboxMessage.status == STATUS_PENDING,
            OutboxMessage.status == STATUS_RETRY,
        ),
    )
    if user_id is not None:
        query = query.filter(OutboxMessage.user_id == user_id)
    ready = (
        query.order_by(OutboxMessage.available_at)
        .with_for_update(skip_locked=True)
        .limit(limit)
        .all()
    )

    for message in ready:
        message.status = STATUS_SENDING
        message.attempts += 1
    db.session.commit()
    return ready


def mark_sent(ids: Sequence[int], user_id: Optional[int] = None) -> int:
    if not ids:
        return 0
    query = OutboxMessage.query.filter(
        OutboxMessage.id.in_(list(ids)),
        OutboxMessage.status == STATUS_SENDING,
    )
    if user_id is not None:
        query = query.filter(OutboxMessage.user_id == user_id)
    updated = query.update(
        {"status": STATUS_SENT, "last_error": None},
        synchronize_session=False,
    )
    db.session.commit()
    return updated


def mark_failed(
    message_id: int,
    err: Exception | str,
    retry_in: timedelta = DEFAULT_RETRY_IN,
    user_id: Optional[int] = None,
) -> Optional[OutboxMessage]:
    query = OutboxMessage.query.filter(
        OutboxMessage.id == message_id,
        OutboxMessage.status == STATUS_SENDING,
    )
    if user_id is not None:
        query = query.filter(OutboxMessage.user_id == user_id)
    message = query.with_for_update().one_or_none()
    if not message:
        return None

    message.last_error = str(err)
    next_available = datetime.utcnow() + retry_in
    message.available_at = max(message.available_at or next_available, next_available)

    if message.attempts >= MAX_DISPATCH_ATTEMPTS:
        message.status = STATUS_DEAD
    else:
        message.status = STATUS_RETRY
    db.session.commit()
    return message


def dispatch_ready(
    limit: int = 50,
    retry_in: timedelta = DEFAULT_RETRY_IN,
    bus_adapter: Optional[EventBusAdapter] = None,
    user_id: Optional[int] = None,
) -> List[int]:
    adapter = bus_adapter or EventBusAdapter()
    messages = dequeue_batch(limit=limit, user_id=user_id)
    sent_ids: List[int] = []

    for message in messages:
        try:
            adapter.dispatch(message)
            sent_ids.append(message.id)
        except Exception as err:
            mark_failed(message.id, err, retry_in=retry_in, user_id=message.user_id)

    if sent_ids:
        mark_sent(sent_ids, user_id=user_id if user_id is not None else None)

    return sent_ids
