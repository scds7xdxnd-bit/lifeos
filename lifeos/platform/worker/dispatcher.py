"""Outbox dispatcher helpers and worker loop."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Callable, List, Optional

from sqlalchemy.exc import SQLAlchemyError

from lifeos.extensions import db
from lifeos.platform.outbox.models import OutboxMessage
from lifeos.platform.outbox.services import (
    STATUS_FAILED,
    STATUS_PENDING,
    STATUS_RETRY,
    STATUS_SENDING,
    STATUS_SENT,
    EventBusAdapter,
)
from lifeos.platform.worker.config import DispatchConfig

logger = logging.getLogger(__name__)


def _compute_backoff_seconds(attempts: int, config: DispatchConfig) -> float:
    """Exponential backoff based on attempt number (1-indexed)."""
    base = config.backoff_seconds
    factor = config.backoff_multiplier ** max(attempts - 1, 0)
    return base * factor


def claim_ready_messages(
    session,
    batch_size: int,
    now: Optional[datetime] = None,
) -> List[OutboxMessage]:
    """
    Lock and return ready messages using SKIP LOCKED, ordered by available_at.
    Moves claimed rows to 'sending' and increments attempts.
    """
    now = now or datetime.utcnow()
    query = (
        session.query(OutboxMessage)
        .filter(
            OutboxMessage.available_at <= now,
            OutboxMessage.status.in_((STATUS_PENDING, STATUS_RETRY)),
        )
        .order_by(OutboxMessage.available_at)
        .with_for_update(skip_locked=True)
        .limit(batch_size)
    )
    messages = query.all()
    for message in messages:
        message.status = STATUS_SENDING
        message.attempts = (message.attempts or 0) + 1
    return messages


def _apply_failure_backoff(message: OutboxMessage, exc: Exception, config: DispatchConfig) -> None:
    attempts = message.attempts or 1
    delay_seconds = _compute_backoff_seconds(attempts, config)
    next_available = datetime.utcnow() + timedelta(seconds=delay_seconds)

    message.last_error = str(exc)
    message.available_at = max(message.available_at or next_available, next_available)

    if attempts >= config.max_attempts:
        message.status = STATUS_FAILED
    else:
        message.status = STATUS_RETRY


def process_ready_batch(
    send_fn: Callable[[OutboxMessage], None],
    config: DispatchConfig,
    session=None,
) -> int:
    """
    Claim ready messages, dispatch via send_fn, and update statuses.
    Returns number of messages processed (sent or failed).
    """
    session = session or db.session
    try:
        messages = claim_ready_messages(session, batch_size=config.batch_size)
        if not messages:
            session.commit()
            return 0

        processed = 0
        for message in messages:
            # Idempotency guard: only dispatch if not already sent
            if message.status == STATUS_SENT:
                continue
            try:
                send_fn(message)
                message.status = STATUS_SENT
                message.last_error = None
            except Exception as exc:
                _apply_failure_backoff(message, exc, config)
            session.add(message)
            processed += 1

        session.commit()
        return processed
    except SQLAlchemyError:
        session.rollback()
        logger.exception("Database error while processing outbox batch")
        return 0
    except Exception:
        session.rollback()
        logger.exception("Unexpected error while processing outbox batch")
        return 0


def run_dispatcher(
    config: Optional[DispatchConfig] = None,
    send_fn: Optional[Callable[[OutboxMessage], None]] = None,
) -> None:
    """
    Run the dispatcher loop; defaults to publishing to the in-process bus via adapter.
    """
    cfg = config or DispatchConfig.from_env()
    adapter = EventBusAdapter()
    dispatch_callable = send_fn or adapter.dispatch

    logger.info(
        "Starting outbox dispatcher (batch_size=%s, poll_interval=%ss, max_attempts=%s, backoff=%ss x%s)",
        cfg.batch_size,
        cfg.poll_interval,
        cfg.max_attempts,
        cfg.backoff_seconds,
        cfg.backoff_multiplier,
    )

    try:
        while True:
            processed = process_ready_batch(dispatch_callable, cfg)
            if processed == 0:
                time.sleep(cfg.poll_interval)
            else:
                time.sleep(min(0.1, cfg.poll_interval))
    except KeyboardInterrupt:
        logger.info("Dispatcher stopped by user")
