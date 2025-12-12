"""Central insights engine that consumes domain events."""

from __future__ import annotations

from time import perf_counter
from typing import List

from lifeos.core.events.event_bus import event_bus
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.rules import (
    cross_rules,
    finance_rules,
    habit_rules,
    health_rules,
    project_rules,
    skill_rules,
)
from lifeos.core.insights.services import persist_insights
from lifeos.core.insights.telemetry import insight_telemetry

RULES = [
    ("finance_rules", finance_rules.apply_rules),
    ("habit_rules", habit_rules.apply_rules),
    ("health_rules", health_rules.apply_rules),
    ("skill_rules", skill_rules.apply_rules),
    ("project_rules", project_rules.apply_rules),
    ("cross_rules", cross_rules.apply_rules),
]


def _count_fp_fn_flags(insights: List[dict]) -> tuple[int, int]:
    """Derive FP/FN counts from insight context flags when present."""
    fp = 0
    fn = 0
    for ins in insights:
        ctx = ins.get("context") or {}
        if ctx.get("is_false_positive"):
            fp += 1
        if ctx.get("is_false_negative"):
            fn += 1
    return fp, fn


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
        started = perf_counter()
        for rule_name, rule_fn in RULES:
            rule_started = perf_counter()
            produced = rule_fn(event) or []
            fp_count, fn_count = _count_fp_fn_flags(produced)
            insight_telemetry.record_rule(
                rule_name,
                len(produced),
                (perf_counter() - rule_started) * 1000,
                fp_count,
                fn_count,
            )
            if produced:
                insights.extend(produced)
        insight_telemetry.record_event(
            event.event_type,
            bool(insights),
            (perf_counter() - started) * 1000,
        )
        if insights:
            persist_insights(insights, event)
        return insights


# Global singleton
insights_engine = InsightsEngine()
