"""Skills domain expert inquiry strategy profile."""

from __future__ import annotations

from lifeos.core.insights.inquiry_strategies.base import DomainStrategyProfile

SKILLS_STRATEGY = DomainStrategyProfile(
    domain="skills",
    profile="skills_domain_expert_brief",
    profile_version="1.0.0",
    strategy="skills_rules_v1",
    strategy_version="1.0.0",
    finding_categories=("practice_coverage", "progression_signal", "evidence_gap"),
    coverage_category="practice_coverage",
    signal_category="progression_signal",
    gap_category="evidence_gap",
    limitation_language=(
        "Skill practice evidence is sparse in this timeframe; progression interpretation is directional.",
        "Skill evidence is bounded to explicit practice/session records in selected scope.",
    ),
    refine_guidance=(
        "Refine by focusing on one skill and a tighter practice window.",
        "Refine by extending timeframe when practice records are sparse.",
    ),
    allowed_claim_prefixes=(
        "Skills evidence includes",
        "Skills derived signals are present",
        "No canonical skills records were found",
    ),
    forbidden_claim_tokens=("because", "caused", "guarantee", "always", "never", "must"),
    event_priority_prefixes=(
        "skills.practice.logged",
        "skills.practice.updated",
        "skills.skill.updated",
        "skills.skill.created",
    ),
    insight_priority_kinds=("skill_practice",),
)


__all__ = ["SKILLS_STRATEGY"]
