"""Calendar domain service: CRUD and interpretation management."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from lifeos.core.interpreter.inference_emitter import emit_inference_event
from lifeos.domains.calendar.events import (
    CALENDAR_EVENT_CREATED,
    CALENDAR_EVENT_DELETED,
    CALENDAR_EVENT_UPDATED,
    CALENDAR_INTERPRETATION_CONFIRMED,
    CALENDAR_INTERPRETATION_REJECTED,
)
from lifeos.domains.calendar.models.calendar_event import (
    CalendarEvent,
    CalendarEventInterpretation,
)
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox


def create_calendar_event(
    user_id: int,
    title: str,
    start_time: datetime,
    end_time: Optional[datetime] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    all_day: bool = False,
    source: str = "manual",
    external_id: Optional[str] = None,
    color: Optional[str] = None,
    is_private: bool = False,
    tags: Optional[list] = None,
    metadata: Optional[dict] = None,
) -> CalendarEvent:
    """
    Create a new calendar event.

    Emits calendar.event.created event for interpreter processing.
    """
    title = (title or "").strip()
    if not title:
        raise ValueError("invalid_title")
    if len(title) > 255:
        raise ValueError("title_too_long")

    event = CalendarEvent(
        user_id=user_id,
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time,
        all_day=all_day,
        location=location,
        source=source,
        external_id=external_id,
        color=color,
        is_private=is_private,
        tags=tags or [],
        metadata_=metadata or {},
    )

    db.session.add(event)
    db.session.flush()

    enqueue_outbox(
        CALENDAR_EVENT_CREATED,
        {
            "event_id": event.id,
            "user_id": user_id,
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat() if end_time else None,
            "source": source,
            "all_day": all_day,
            "created_at": event.created_at.isoformat(),
        },
        user_id=user_id,
    )

    db.session.commit()
    return event


def update_calendar_event(
    user_id: int,
    event_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    all_day: Optional[bool] = None,
    location: Optional[str] = None,
    color: Optional[str] = None,
    is_private: Optional[bool] = None,
    tags: Optional[list] = None,
    metadata: Optional[dict] = None,
) -> CalendarEvent:
    """
    Update an existing calendar event.

    Emits calendar.event.updated event for interpreter re-processing.
    """
    event = CalendarEvent.query.filter_by(id=event_id, user_id=user_id).first()
    if not event:
        raise ValueError("not_found")

    changed_fields: list[str] = []

    if title is not None:
        title = title.strip()
        if not title:
            raise ValueError("invalid_title")
        if title != event.title:
            event.title = title
            changed_fields.append("title")

    if description is not None and description != event.description:
        event.description = description
        changed_fields.append("description")

    if start_time is not None and start_time != event.start_time:
        event.start_time = start_time
        changed_fields.append("start_time")

    if end_time is not None and end_time != event.end_time:
        event.end_time = end_time
        changed_fields.append("end_time")

    if all_day is not None and all_day != event.all_day:
        event.all_day = all_day
        changed_fields.append("all_day")

    if location is not None and location != event.location:
        event.location = location
        changed_fields.append("location")

    if color is not None and color != event.color:
        event.color = color
        changed_fields.append("color")

    if is_private is not None and is_private != event.is_private:
        event.is_private = is_private
        changed_fields.append("is_private")

    if tags is not None and tags != event.tags:
        event.tags = tags
        changed_fields.append("tags")

    if metadata is not None and metadata != event.metadata_:
        event.metadata_ = metadata
        changed_fields.append("metadata")

    if changed_fields:
        db.session.add(event)
        db.session.flush()

        enqueue_outbox(
            CALENDAR_EVENT_UPDATED,
            {
                "event_id": event.id,
                "user_id": user_id,
                "title": event.title,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat() if event.end_time else None,
                "source": event.source,
                "updated_at": event.updated_at.isoformat(),
                "changed_fields": changed_fields,
            },
            user_id=user_id,
        )

        db.session.commit()

    return event


def delete_calendar_event(user_id: int, event_id: int) -> None:
    """
    Delete a calendar event and its interpretations.

    Emits calendar.event.deleted event.
    """
    event = CalendarEvent.query.filter_by(id=event_id, user_id=user_id).first()
    if not event:
        raise ValueError("not_found")

    enqueue_outbox(
        CALENDAR_EVENT_DELETED,
        {
            "event_id": event_id,
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )

    db.session.delete(event)
    db.session.commit()


def get_calendar_event(user_id: int, event_id: int) -> CalendarEvent | None:
    """Get a single calendar event by ID."""
    return CalendarEvent.query.filter_by(id=event_id, user_id=user_id).first()


def list_calendar_events(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    source: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[CalendarEvent]:
    """
    List calendar events with optional filters.

    Returns events ordered by start_time descending.
    """
    query = CalendarEvent.query.filter(CalendarEvent.user_id == user_id)

    if start_date:
        query = query.filter(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.start_time <= end_date)
    if source:
        query = query.filter(CalendarEvent.source == source)

    return query.order_by(CalendarEvent.start_time.desc()).offset(offset).limit(limit).all()


def get_pending_interpretations(
    user_id: int,
    domain: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[CalendarEventInterpretation]:
    """
    Get pending (inferred) interpretations for user review.
    """
    query = CalendarEventInterpretation.query.filter(
        CalendarEventInterpretation.user_id == user_id,
        CalendarEventInterpretation.status == "inferred",
    )

    if domain:
        query = query.filter(CalendarEventInterpretation.domain == domain)

    return query.order_by(CalendarEventInterpretation.created_at.desc()).offset(offset).limit(limit).all()


def update_interpretation_status(
    user_id: int,
    interpretation_id: int,
    status: str,
    record_id: Optional[int] = None,
) -> CalendarEventInterpretation:
    """
    Update interpretation status (confirm, reject, ignore, ambiguous).

    Emits appropriate event based on new status.
    """
    if status not in {"confirmed", "rejected", "ignored", "ambiguous"}:
        raise ValueError("invalid_status")

    interpretation = CalendarEventInterpretation.query.filter_by(id=interpretation_id, user_id=user_id).first()
    if not interpretation:
        raise ValueError("not_found")

    previous_record_id = interpretation.record_id
    interpretation.status = status
    if record_id is not None:
        interpretation.record_id = record_id

    db.session.add(interpretation)
    db.session.flush()

    if status == "confirmed":
        enqueue_outbox(
            CALENDAR_INTERPRETATION_CONFIRMED,
            {
                "interpretation_id": interpretation.id,
                "calendar_event_id": interpretation.calendar_event_id,
                "user_id": user_id,
                "domain": interpretation.domain,
                "record_type": interpretation.record_type,
                "record_id": record_id,
                "status": status,
                "payload_version": "v1",
                "confirmed_at": datetime.utcnow().isoformat(),
            },
            user_id=user_id,
        )
    elif status == "rejected":
        enqueue_outbox(
            CALENDAR_INTERPRETATION_REJECTED,
            {
                "interpretation_id": interpretation.id,
                "calendar_event_id": interpretation.calendar_event_id,
                "user_id": user_id,
                "domain": interpretation.domain,
                "record_type": interpretation.record_type,
                "status": status,
                "payload_version": "v1",
                "rejected_at": datetime.utcnow().isoformat(),
            },
            user_id=user_id,
        )
    elif status == "ambiguous":
        enqueue_outbox(
            CALENDAR_INTERPRETATION_REJECTED,
            {
                "interpretation_id": interpretation.id,
                "calendar_event_id": interpretation.calendar_event_id,
                "user_id": user_id,
                "domain": interpretation.domain,
                "record_type": interpretation.record_type,
                "status": status,
                "payload_version": "v1",
                "updated_at": datetime.utcnow().isoformat(),
            },
            user_id=user_id,
        )

    is_false_positive = status in {"rejected", "ambiguous"}
    is_false_negative = False
    if status == "confirmed" and record_id is not None:
        if previous_record_id and record_id != previous_record_id:
            is_false_negative = True  # model pointed to wrong entity; user corrected
        elif previous_record_id is None:
            is_false_negative = True  # model missed mapping; user supplied

    emit_inference_event(
        domain=interpretation.domain,
        record_type=interpretation.record_type,
        user_id=user_id,
        calendar_event_id=interpretation.calendar_event_id,
        confidence=float(interpretation.confidence_score),
        inferred_data=interpretation.classification_data or {},
        record_id=interpretation.record_id,
        status=status,
        model_version="calendar-interpreter-v1",
        context={"source": "user_review", "interpretation_id": interpretation.id},
        is_false_positive=is_false_positive,
        is_false_negative=is_false_negative,
    )

    db.session.commit()
    return interpretation
