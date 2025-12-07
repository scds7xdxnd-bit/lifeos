"""Simple in-process event bus."""

from __future__ import annotations

from typing import Callable, Dict, List

from lifeos.core.events.event_models import EventRecord

EventHandler = Callable[[EventRecord], None]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._subscribers.setdefault(event_type, [])
        handlers.append(handler)

    def publish(self, event: EventRecord) -> None:
        for handler in self._subscribers.get(event.event_type, []):
            handler(event)


# Global singleton
event_bus = EventBus()

