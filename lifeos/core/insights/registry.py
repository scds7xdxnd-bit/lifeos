"""Phase 5b insight type registry (rules-only)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Mapping

FeatureSnapshot = Mapping[str, float]


@dataclass(frozen=True)
class InsightTypeDefinition:
    insight_type: str
    required_features: tuple[str, ...]
    window_days: int
    delivery_policy: str
    severity: str
    summary_template: str
    detail_template: str
    trigger: Callable[[FeatureSnapshot], bool]
    confidence: Callable[[FeatureSnapshot], float]
    priority: Callable[[FeatureSnapshot], int]
    context_builder: Callable[[FeatureSnapshot], Dict[str, object]]


def _confidence_from_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.4
    ratio = numerator / denominator
    return max(0.4, min(0.9, 0.4 + (ratio * 0.5)))


def _fixed_confidence(value: float) -> Callable[[FeatureSnapshot], float]:
    return lambda _: value


def _fixed_priority(value: int) -> Callable[[FeatureSnapshot], int]:
    return lambda _: value


def _context_calendar_finance(snapshot: FeatureSnapshot) -> Dict[str, object]:
    return {
        "obligation_count": int(snapshot.get("calendar.obligation.count", 0)),
        "spend_total": round(snapshot.get("finance.spend.total", 0.0), 2),
    }


def _trigger_calendar_finance(snapshot: FeatureSnapshot) -> bool:
    return snapshot.get("calendar.obligation.count", 0.0) >= 1 and snapshot.get("finance.spend.total", 0.0) >= 500.0


def _confidence_calendar_finance(snapshot: FeatureSnapshot) -> float:
    return _confidence_from_ratio(snapshot.get("finance.spend.total", 0.0), 1000.0)


def _context_finance_journal(snapshot: FeatureSnapshot) -> Dict[str, object]:
    return {
        "stress_entries": int(snapshot.get("journal.stress.count", 0)),
        "spend_total": round(snapshot.get("finance.spend.total", 0.0), 2),
    }


def _trigger_finance_journal(snapshot: FeatureSnapshot) -> bool:
    return snapshot.get("journal.stress.count", 0.0) >= 1 and snapshot.get("finance.spend.total", 0.0) >= 200.0


def _confidence_finance_journal(snapshot: FeatureSnapshot) -> float:
    return _confidence_from_ratio(snapshot.get("journal.stress.count", 0.0), 3.0)


def _context_journal_habits(snapshot: FeatureSnapshot) -> Dict[str, object]:
    return {
        "journal_entries": int(snapshot.get("journal.entry.count", 0)),
        "habit_logs": int(snapshot.get("habits.log.count", 0)),
    }


def _trigger_journal_habits(snapshot: FeatureSnapshot) -> bool:
    return snapshot.get("journal.entry.count", 0.0) >= 2 and snapshot.get("habits.log.count", 0.0) >= 4


def _context_calendar_relationships(snapshot: FeatureSnapshot) -> Dict[str, object]:
    return {
        "calendar_events": int(snapshot.get("calendar.event.count", 0)),
        "interaction_count": int(snapshot.get("relationships.interaction.count", 0)),
    }


def _trigger_calendar_relationships(snapshot: FeatureSnapshot) -> bool:
    return snapshot.get("calendar.event.count", 0.0) >= 5 and snapshot.get("relationships.interaction.count", 0.0) == 0


def _context_calendar_projects(snapshot: FeatureSnapshot) -> Dict[str, object]:
    return {
        "late_night_events": int(snapshot.get("calendar.event.late_night.count", 0)),
        "tasks_completed": int(snapshot.get("projects.task.completed.count", 0)),
    }


def _trigger_calendar_projects(snapshot: FeatureSnapshot) -> bool:
    return (
        snapshot.get("calendar.event.late_night.count", 0.0) >= 3
        and snapshot.get(
            "projects.task.completed.count",
            0.0,
        )
        == 0
    )


def _context_habits_health(snapshot: FeatureSnapshot) -> Dict[str, object]:
    return {
        "habit_logs": int(snapshot.get("habits.log.count", 0)),
        "low_sleep_events": int(snapshot.get("health.sleep_low.count", 0)),
    }


def _trigger_habits_health(snapshot: FeatureSnapshot) -> bool:
    return snapshot.get("habits.log.count", 0.0) >= 5 and snapshot.get("health.sleep_low.count", 0.0) <= 1


PHASE5B_INSIGHT_DEFINITIONS = [
    InsightTypeDefinition(
        insight_type="finance_calendar_obligation_risk",
        required_features=("calendar.obligation.count", "finance.spend.total"),
        window_days=30,
        delivery_policy="feed",
        severity="info",
        summary_template="Payment-related events are scheduled and recent spend is {spend_total}.",
        detail_template=(
            "You have {obligation_count} payment-related calendar items in the next window. "
            "Recent spend totals {spend_total}. This is a neutral heads-up."
        ),
        trigger=_trigger_calendar_finance,
        confidence=_confidence_calendar_finance,
        priority=_fixed_priority(70),
        context_builder=_context_calendar_finance,
    ),
    InsightTypeDefinition(
        insight_type="finance_journal_stress_spike",
        required_features=("journal.stress.count", "finance.spend.total"),
        window_days=7,
        delivery_policy="feed",
        severity="info",
        summary_template="Spending rose during {stress_entries} stress-tagged journal entries.",
        detail_template=(
            "You logged {stress_entries} stress-related journal entries while spending {spend_total} "
            "in the last 7 days."
        ),
        trigger=_trigger_finance_journal,
        confidence=_confidence_finance_journal,
        priority=_fixed_priority(65),
        context_builder=_context_finance_journal,
    ),
    InsightTypeDefinition(
        insight_type="journal_habit_reflection_link",
        required_features=("journal.entry.count", "habits.log.count"),
        window_days=7,
        delivery_policy="feed",
        severity="info",
        summary_template="Journal entries and habit logs both increased this week.",
        detail_template="You logged {journal_entries} journal entries and {habit_logs} habit check-ins recently.",
        trigger=_trigger_journal_habits,
        confidence=_fixed_confidence(0.55),
        priority=_fixed_priority(55),
        context_builder=_context_journal_habits,
    ),
    InsightTypeDefinition(
        insight_type="calendar_relationship_gap",
        required_features=("calendar.event.count", "relationships.interaction.count"),
        window_days=30,
        delivery_policy="feed",
        severity="info",
        summary_template="Busy calendar, but no logged interactions in the last 30 days.",
        detail_template=(
            "You scheduled {calendar_events} calendar events and logged {interaction_count} interactions recently. "
            "If interactions happened, consider logging them."
        ),
        trigger=_trigger_calendar_relationships,
        confidence=_fixed_confidence(0.5),
        priority=_fixed_priority(60),
        context_builder=_context_calendar_relationships,
    ),
    InsightTypeDefinition(
        insight_type="calendar_project_late_night_slippage",
        required_features=("calendar.event.late_night.count", "projects.task.completed.count"),
        window_days=14,
        delivery_policy="feed",
        severity="info",
        summary_template="Late-night events coincided with zero project completions.",
        detail_template=(
            "There were {late_night_events} late-night calendar events and no completed tasks in this window."
        ),
        trigger=_trigger_calendar_projects,
        confidence=_fixed_confidence(0.5),
        priority=_fixed_priority(60),
        context_builder=_context_calendar_projects,
    ),
    InsightTypeDefinition(
        insight_type="habits_health_sleep_consistency",
        required_features=("habits.log.count", "health.sleep_low.count"),
        window_days=7,
        delivery_policy="feed",
        severity="info",
        summary_template="Habit streaks held while low-sleep events stayed low.",
        detail_template=(
            "You logged {habit_logs} habit check-ins and only {low_sleep_events} low-sleep signals recently."
        ),
        trigger=_trigger_habits_health,
        confidence=_fixed_confidence(0.55),
        priority=_fixed_priority(55),
        context_builder=_context_habits_health,
    ),
]


def enabled_insight_types(config: Mapping[str, object] | None = None) -> set[str]:
    default = {definition.insight_type for definition in PHASE5B_INSIGHT_DEFINITIONS}
    raw = None
    if config:
        raw = config.get("PHASE5B_INSIGHT_TYPES")
        if isinstance(raw, (list, tuple, set)):
            normalized = {str(item).strip() for item in raw if str(item).strip()}
            return normalized or default
        if isinstance(raw, str):
            normalized = {part.strip() for part in raw.split(",") if part.strip()}
            return normalized or default
    raw_env = os.environ.get("PHASE5B_INSIGHT_TYPES", "")
    if raw_env.strip():
        return {part.strip() for part in raw_env.split(",") if part.strip()}
    return default


def get_enabled_insight_definitions(config: Mapping[str, object] | None = None) -> Iterable[InsightTypeDefinition]:
    enabled = enabled_insight_types(config)
    return [definition for definition in PHASE5B_INSIGHT_DEFINITIONS if definition.insight_type in enabled]


__all__ = [
    "InsightTypeDefinition",
    "PHASE5B_INSIGHT_DEFINITIONS",
    "enabled_insight_types",
    "get_enabled_insight_definitions",
]
