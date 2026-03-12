"""Relationships domain expert inquiry strategy profile."""

from __future__ import annotations

from lifeos.core.insights.inquiry_strategies.base import DomainStrategyProfile

RELATIONSHIPS_STRATEGY = DomainStrategyProfile(
    domain="relationships",
    profile="focused_inquiry_relationships_expert_brief",
    profile_version="1.0.0",
    strategy="relationships_rules_v1",
    strategy_version="1.0.0",
    finding_categories=("interaction_cadence", "channel_distribution", "evidence_gap"),
    coverage_category="interaction_cadence",
    signal_category="channel_distribution",
    gap_category="evidence_gap",
    limitation_language=(
        "Relationships evidence is descriptive only and limited to explicit interaction logs and timestamps.",
        "Relationships summary is bounded to cadence and calendar-linked records without quality judgments.",
    ),
    refine_guidance=(
        "Refine by narrowing the timeframe to one relationship cadence cycle.",
        "Refine by focusing on one interaction channel when logs are mixed.",
    ),
    allowed_claim_prefixes=(
        "Relationships evidence includes",
        "Relationships derived signals are present",
        "No canonical relationships records were found",
    ),
    forbidden_claim_tokens=(
        "toxic",
        "healthy relationship",
        "unhealthy relationship",
        "good person",
        "bad person",
        "moral",
        "intent",
        "emotion of",
        "should",
    ),
    event_priority_prefixes=(
        "relationships.interaction.logged",
        "relationships.interaction.created",
        "relationships.person.created",
        "relationships.person.updated",
    ),
    insight_priority_kinds=("calendar_relationship_gap",),
)


__all__ = ["RELATIONSHIPS_STRATEGY"]
