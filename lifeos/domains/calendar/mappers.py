"""Calendar domain mappers: DTO ↔ model converters."""

from __future__ import annotations

from lifeos.domains.calendar.models.calendar_event import (
    CalendarEvent,
    CalendarEventInterpretation,
)
from lifeos.domains.calendar.schemas import (
    CalendarEventResponse,
    InterpretationResponse,
)


def calendar_event_to_response(event: CalendarEvent) -> CalendarEventResponse:
    """Convert CalendarEvent model to response DTO."""
    return CalendarEventResponse(
        id=event.id,
        user_id=event.user_id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        all_day=event.all_day,
        location=event.location,
        source=event.source,
        external_id=event.external_id,
        color=event.color,
        is_private=event.is_private,
        tags=event.tags,
        duration_minutes=event.duration_minutes,
        created_at=event.created_at,
        updated_at=event.updated_at,
        interpretations=(
            [interpretation_to_response(i) for i in event.interpretations]
            if event.interpretations
            else None
        ),
    )


def interpretation_to_response(
    interpretation: CalendarEventInterpretation,
) -> InterpretationResponse:
    """Convert CalendarEventInterpretation model to response DTO."""
    return InterpretationResponse(
        id=interpretation.id,
        calendar_event_id=interpretation.calendar_event_id,
        domain=interpretation.domain,
        record_type=interpretation.record_type,
        record_id=interpretation.record_id,
        confidence_score=float(interpretation.confidence_score),
        status=interpretation.status,
        classification_data=interpretation.classification_data,
        created_at=interpretation.created_at,
        updated_at=interpretation.updated_at,
    )
