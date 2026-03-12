"""Habits domain expert inquiry strategy profile."""

from __future__ import annotations

from lifeos.core.insights.inquiry_strategies.base import DomainStrategyProfile

HABITS_STRATEGY = DomainStrategyProfile(
    domain="habits",
    profile="habits_domain_expert_brief",
    profile_version="1.0.0",
    strategy="habits_rules_v1",
    strategy_version="1.0.0",
    finding_categories=("adherence_coverage", "consistency_signal", "evidence_gap"),
    coverage_category="adherence_coverage",
    signal_category="consistency_signal",
    gap_category="evidence_gap",
    limitation_language=(
        "Habit log evidence is sparse in this timeframe; treat adherence interpretation as partial.",
        "Habit log evidence is bounded to explicit logs in the selected timeframe.",
    ),
    refine_guidance=(
        "Refine by narrowing scope to one habit and a tighter week window.",
        "Refine by extending timeframe when logs are sparse for selected habits.",
    ),
    allowed_claim_prefixes=(
        "Habits evidence includes",
        "Habits derived signals are present",
        "No canonical habits records were found",
    ),
    forbidden_claim_tokens=("because", "caused", "guarantee", "always", "never", "must"),
    event_priority_prefixes=("habits.habit.logged", "habits.habit.updated", "habits.habit.created"),
    insight_priority_kinds=("habit_progress",),
)


__all__ = ["HABITS_STRATEGY"]
