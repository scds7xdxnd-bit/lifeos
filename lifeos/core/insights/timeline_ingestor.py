"""Timeline ingestion subscriber for Phase 5a."""

from __future__ import annotations

import os

from flask import current_app

from lifeos.core.events.event_bus import event_bus
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.substrate_service import (
    TIMELINE_EVENT_TYPES,
    generate_interpretations_for_timeline_event,
    ingest_timeline_event,
)


class TimelineIngestor:
    def __init__(self) -> None:
        self._enabled = True

    @property
    def enabled(self) -> bool:
        try:
            return current_app.config.get("ENABLE_TIMELINE_INGESTION", True)
        except RuntimeError:
            return os.environ.get("ENABLE_TIMELINE_INGESTION", "true").lower() in ("1", "true", "yes")

    @property
    def interpretations_enabled(self) -> bool:
        try:
            return current_app.config.get("ENABLE_INTERPRETATION_RELATIONSHIP", True)
        except RuntimeError:
            return os.environ.get("ENABLE_INTERPRETATION_RELATIONSHIP", "true").lower() in ("1", "true", "yes")

    def register_subscriptions(self) -> None:
        for event_type in TIMELINE_EVENT_TYPES:
            event_bus.subscribe(event_type, self.on_event)

    def on_event(self, event: EventRecord) -> None:
        if not self.enabled:
            return
        timeline_event = ingest_timeline_event(event)
        if not timeline_event:
            return
        if self.interpretations_enabled:
            generate_interpretations_for_timeline_event(timeline_event)


timeline_ingestor = TimelineIngestor()

__all__ = ["timeline_ingestor"]
