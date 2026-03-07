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
