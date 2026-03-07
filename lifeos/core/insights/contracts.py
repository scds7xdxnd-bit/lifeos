"""Insight contracts and confidence vocabulary (Phase 2.5 freeze)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

CONFIDENCE_VOCABULARY = (
    "informational",
    "suggested",
    "needs_review",
    "confirmed",
)


@dataclass(frozen=True)
class InsightContract:
    name: str
    description: str
    required_evidence: list[str]
    disallowed_evidence: list[str]
    confidence_bands: dict[str, str]
    allowed_actions: list[str]


INSIGHT_CONTRACTS: dict[str, InsightContract] = {
    "finance_spend": InsightContract(
        name="finance_spend",
        description="A spending transaction was recorded; surfaced as informational.",
        required_evidence=["finance.transaction.created"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Echo the recorded transaction without recommendations.",
        },
        allowed_actions=["display"],
    ),
    "journal_posted": InsightContract(
        name="journal_posted",
        description="A journal entry was posted to the ledger.",
        required_evidence=["finance.journal.posted"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Confirm journal posting; no automation.",
        },
        allowed_actions=["display"],
    ),
    "habit_progress": InsightContract(
        name="habit_progress",
        description="A habit log was recorded and can be summarized.",
        required_evidence=["habits.habit.logged"],
        disallowed_evidence=["habits.habit.inferred"],
        confidence_bands={
            "informational": "Summarize logged habit activity.",
            "needs_review": "Only if inferred; do not auto-confirm.",
        },
        allowed_actions=["display", "review_only"],
    ),
    "project_task_done": InsightContract(
        name="project_task_done",
        description="A project task completion was recorded.",
        required_evidence=["projects.task.completed", "projects.task.logged"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Show completion confirmation.",
        },
        allowed_actions=["display"],
    ),
    "skill_practice": InsightContract(
        name="skill_practice",
        description="A skill practice session was logged.",
        required_evidence=["skills.practice.logged"],
        disallowed_evidence=["skills.practice.inferred"],
        confidence_bands={
            "informational": "Summarize practice session.",
            "needs_review": "Only if inferred; do not auto-confirm.",
        },
        allowed_actions=["display", "review_only"],
    ),
    "health_metric": InsightContract(
        name="health_metric",
        description="A health metric update was recorded.",
        required_evidence=["health.metric.updated", "health.biometric.logged"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Summarize recorded health metric.",
        },
        allowed_actions=["display"],
    ),
    "finance_sleep_spend": InsightContract(
        name="finance_sleep_spend",
        description="Cross-domain note linking finance and rest patterns.",
        required_evidence=["finance.transaction.created", "health.biometric.logged"],
        disallowed_evidence=["calendar.event.created"],
        confidence_bands={
            "needs_review": "Show as a review-only correlation.",
        },
        allowed_actions=["review_only"],
    ),
    "habit_project_synergy": InsightContract(
        name="habit_project_synergy",
        description="Cross-domain note linking habits to project outcomes.",
        required_evidence=["habits.habit.logged", "projects.task.completed"],
        disallowed_evidence=["calendar.event.created"],
        confidence_bands={
            "needs_review": "Show as a review-only correlation.",
        },
        allowed_actions=["review_only"],
    ),
    "skill_mood_uplift": InsightContract(
        name="skill_mood_uplift",
        description="Cross-domain note linking skill practice and mood signals.",
        required_evidence=["skills.practice.logged", "journal.entry.created"],
        disallowed_evidence=["calendar.event.created"],
        confidence_bands={
            "needs_review": "Show as a review-only correlation.",
        },
        allowed_actions=["review_only"],
    ),
    "finance_calendar_obligation_risk": InsightContract(
        name="finance_calendar_obligation_risk",
        description="Cross-domain note linking calendar obligations and recent spend.",
        required_evidence=["calendar.event.created", "finance.transaction.created"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Surface as a neutral heads-up with no recommendation.",
        },
        allowed_actions=["display"],
    ),
    "finance_journal_stress_spike": InsightContract(
        name="finance_journal_stress_spike",
        description="Cross-domain note linking journal stress signals and spending.",
        required_evidence=["journal.entry.created", "finance.transaction.created"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Surface as an observational note only.",
        },
        allowed_actions=["display"],
    ),
    "journal_habit_reflection_link": InsightContract(
        name="journal_habit_reflection_link",
        description="Cross-domain note linking journal reflection and habit adherence.",
        required_evidence=["journal.entry.created", "habits.habit.logged"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Summarize recent reflection and habit activity.",
        },
        allowed_actions=["display"],
    ),
    "calendar_relationship_gap": InsightContract(
        name="calendar_relationship_gap",
        description="Cross-domain note highlighting calendar activity without recent interactions.",
        required_evidence=["calendar.event.created", "relationships.interaction.logged"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Surface as a neutral reminder with no directive language.",
        },
        allowed_actions=["display"],
    ),
    "calendar_project_late_night_slippage": InsightContract(
        name="calendar_project_late_night_slippage",
        description="Cross-domain note linking late-night calendar activity and project completion gaps.",
        required_evidence=["calendar.event.created", "projects.task.completed"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Surface as an observational note only.",
        },
        allowed_actions=["display"],
    ),
    "habits_health_sleep_consistency": InsightContract(
        name="habits_health_sleep_consistency",
        description="Cross-domain note linking habit logs with low-sleep signals.",
        required_evidence=["habits.habit.logged", "health.metric.updated"],
        disallowed_evidence=[],
        confidence_bands={
            "informational": "Summarize recent habit and sleep signals.",
        },
        allowed_actions=["display"],
    ),
}


def get_insight_contract(name: str) -> InsightContract | None:
    return INSIGHT_CONTRACTS.get(name)


def list_insight_contracts() -> Iterable[InsightContract]:
    return INSIGHT_CONTRACTS.values()


__all__ = [
    "CONFIDENCE_VOCABULARY",
    "InsightContract",
    "INSIGHT_CONTRACTS",
    "get_insight_contract",
    "list_insight_contracts",
]
