"""Timeline adapter registry."""

from __future__ import annotations

from lifeos.core.timeline.adapters.base import TimelineAdapter
from lifeos.core.timeline.adapters.calendar import CALENDAR_TIMELINE_ADAPTER
from lifeos.core.timeline.adapters.finance import FINANCE_TIMELINE_ADAPTER
from lifeos.core.timeline.adapters.habits import HABITS_TIMELINE_ADAPTER
from lifeos.core.timeline.adapters.projects import PROJECTS_TIMELINE_ADAPTER
from lifeos.core.timeline.adapters.skills import SKILLS_TIMELINE_ADAPTER

TIMELINE_ADAPTERS: dict[str, TimelineAdapter] = {
    adapter.domain: adapter
    for adapter in (
        CALENDAR_TIMELINE_ADAPTER,
        FINANCE_TIMELINE_ADAPTER,
        HABITS_TIMELINE_ADAPTER,
        PROJECTS_TIMELINE_ADAPTER,
        SKILLS_TIMELINE_ADAPTER,
    )
}


def get_timeline_adapter(domain: str) -> TimelineAdapter | None:
    return TIMELINE_ADAPTERS.get(str(domain or "").strip().lower())


__all__ = ["TIMELINE_ADAPTERS", "TimelineAdapter", "get_timeline_adapter"]
