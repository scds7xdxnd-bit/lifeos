"""Central insights engine that consumes domain events."""

from __future__ import annotations

from typing import List

from lifeos.core.events.event_bus import event_bus
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.rules import finance_rules, habit_rules, health_rules, project_rules, skill_rules, cross_rules
from lifeos.core.insights.services import persist_insights


class InsightsEngine:
    def __init__(self) -> None:
        # Subscribe to high-value event streams
        for event_type in (
            "finance.transaction.created",
            "finance.journal.posted",
            "habits.habit.logged",
            "health.metric.updated",
            "skills.practice.logged",
            "projects.task.completed",
        ):
            event_bus.subscribe(event_type, self.ingest_event)

    def ingest_event(self, event: EventRecord) -> List[dict]:
        """Run rules and persist any generated insights."""
        insights: List[dict] = []
        for rule_fn in (
            finance_rules.apply_rules,
            habit_rules.apply_rules,
            health_rules.apply_rules,
            skill_rules.apply_rules,
            project_rules.apply_rules,
            cross_rules.apply_rules,
        ):
            insights.extend(rule_fn(event))
        if insights:
            persist_insights(insights, event)
        return insights


# Global singleton
insights_engine = InsightsEngine()
