"""Projects domain expert inquiry strategy profile."""

from __future__ import annotations

from lifeos.core.insights.inquiry_strategies.base import DomainStrategyProfile

PROJECTS_STRATEGY = DomainStrategyProfile(
    domain="projects",
    profile="projects_domain_expert_brief",
    profile_version="1.0.0",
    strategy="projects_rules_v1",
    strategy_version="1.0.0",
    finding_categories=("execution_coverage", "completion_signal", "evidence_gap"),
    coverage_category="execution_coverage",
    signal_category="completion_signal",
    gap_category="evidence_gap",
    limitation_language=(
        "Project evidence is partial in this timeframe; completion interpretation is directional.",
        "Project evidence is bounded to explicit task and activity records in scope.",
    ),
    refine_guidance=(
        "Refine by limiting to a narrower project delivery window.",
        "Refine by reducing domain scope to project execution only when activity is sparse.",
    ),
    allowed_claim_prefixes=(
        "Projects evidence includes",
        "Projects derived signals are present",
        "No canonical projects records were found",
    ),
    forbidden_claim_tokens=("because", "caused", "guarantee", "always", "never", "must"),
    event_priority_prefixes=(
        "projects.task.completed",
        "projects.task.logged",
        "projects.task.updated",
        "projects.task.created",
    ),
    insight_priority_kinds=("project_task_done",),
)


__all__ = ["PROJECTS_STRATEGY"]
