"""Calendar Interpreter: classifies events and creates inferred domain records."""

from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

from flask import current_app

from lifeos.core.events.event_bus import event_bus
from lifeos.core.interpreter.classification_rules import classify_event
from lifeos.core.interpreter.constants import (
    MINIMUM_CONFIDENCE_THRESHOLD,
    STATUS_INFERRED,
)
from lifeos.core.interpreter.domain_adapters import get_adapter
from lifeos.domains.calendar.events import CALENDAR_INTERPRETATION_CREATED
from lifeos.domains.calendar.models.calendar_event import (
    CalendarEvent,
    CalendarEventInterpretation,
)
from lifeos.extensions import db
from lifeos.platform.outbox import enqueue as enqueue_outbox


class CalendarInterpreter:
    """
    Subscribes to calendar events, classifies them, and creates inferred domain records.

    The interpreter uses rule-based classification to analyze calendar event titles,
    descriptions, locations, and timing to determine which domain(s) the event
    may relate to. It creates CalendarEventInterpretation records for each
    potential match and optionally creates inferred records in the target domains.
    """

    def __init__(self):
        self._enabled = True

    @property
    def enabled(self) -> bool:
        """Check if interpreter is enabled via config."""
        try:
            return current_app.config.get("ENABLE_CALENDAR_INTERPRETER", True)
        except RuntimeError:
            # Outside app context, check env directly
            return os.environ.get("ENABLE_CALENDAR_INTERPRETER", "true").lower() in (
                "1",
                "true",
            )

    def register_subscriptions(self) -> None:
        """Register event bus subscriptions for calendar events."""
        event_bus.subscribe("calendar.event.created", self.on_calendar_event)
        event_bus.subscribe("calendar.event.updated", self.on_calendar_event)

    def on_calendar_event(self, event: dict) -> None:
        """
        Handle calendar event creation/update.

        Classifies the event and creates interpretations.
        """
        if not self.enabled:
            return

        payload = event.get("payload", {})
        event_id = payload.get("event_id")
        user_id = payload.get("user_id")

        if not event_id or not user_id:
            return

        # Fetch the full event
        calendar_event = CalendarEvent.query.get(event_id)
        if not calendar_event:
            return

        # Classify the event
        self.interpret_event(calendar_event)

    def interpret_event(self, event: CalendarEvent) -> List[CalendarEventInterpretation]:
        """
        Classify a calendar event and create interpretation records.

        Returns list of created interpretations.
        """
        if not self.enabled:
            return []

        # Clear existing inferred interpretations for this event on re-interpretation
        CalendarEventInterpretation.query.filter(
            CalendarEventInterpretation.calendar_event_id == event.id,
            CalendarEventInterpretation.status == STATUS_INFERRED,
        ).delete(synchronize_session=False)

        # Classify the event
        classifications = classify_event(
            title=event.title,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
        )

        interpretations: List[CalendarEventInterpretation] = []

        for classification in classifications:
            if classification["confidence_score"] < MINIMUM_CONFIDENCE_THRESHOLD:
                continue

            interpretation = self._create_interpretation(
                event=event,
                domain=classification["domain"],
                record_type=classification["record_type"],
                confidence_score=classification["confidence_score"],
                extracted_data=classification["extracted_data"],
            )

            if interpretation:
                interpretations.append(interpretation)

        db.session.commit()
        return interpretations

    def _create_interpretation(
        self,
        event: CalendarEvent,
        domain: str,
        record_type: str,
        confidence_score: float,
        extracted_data: dict,
    ) -> Optional[CalendarEventInterpretation]:
        """
        Create a CalendarEventInterpretation record.

        Optionally creates an inferred record in the target domain if confidence is high.
        """
        interpretation = CalendarEventInterpretation(
            calendar_event_id=event.id,
            user_id=event.user_id,
            domain=domain,
            record_type=record_type,
            confidence_score=confidence_score,
            status=STATUS_INFERRED,
            classification_data=extracted_data,
        )

        db.session.add(interpretation)
        db.session.flush()

        # Emit interpretation created event
        enqueue_outbox(
            CALENDAR_INTERPRETATION_CREATED,
            {
                "interpretation_id": interpretation.id,
                "calendar_event_id": event.id,
                "user_id": event.user_id,
                "domain": domain,
                "record_type": record_type,
                "confidence_score": confidence_score,
                "created_at": interpretation.created_at.isoformat(),
            },
            user_id=event.user_id,
        )

        # If high confidence, create inferred record in target domain
        if confidence_score >= 0.7:
            record_id = self._create_domain_record(
                user_id=event.user_id,
                calendar_event_id=event.id,
                domain=domain,
                record_type=record_type,
                confidence_score=confidence_score,
                extracted_data=extracted_data,
                event_start_time=event.start_time,
            )
            if record_id:
                interpretation.record_id = record_id

        return interpretation

    def _create_domain_record(
        self,
        user_id: int,
        calendar_event_id: int,
        domain: str,
        record_type: str,
        confidence_score: float,
        extracted_data: dict,
        event_start_time: datetime,
    ) -> Optional[int]:
        """
        Create an inferred record in the target domain via adapter.

        Returns record ID or None if adapter not found or creation failed.
        """
        adapter = get_adapter(domain, record_type)
        if not adapter:
            return None

        try:
            return adapter.create_inferred_record(
                user_id=user_id,
                calendar_event_id=calendar_event_id,
                confidence_score=confidence_score,
                extracted_data=extracted_data,
                event_start_time=event_start_time,
            )
        except Exception as exc:
            # Log but don't fail interpretation creation
            try:
                current_app.logger.warning(f"Failed to create inferred {domain}.{record_type} record: {exc}")
            except RuntimeError:
                pass
            return None


# Global singleton (initialized in app factory)
calendar_interpreter = CalendarInterpreter()
