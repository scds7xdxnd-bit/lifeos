"""Journal domain expert inquiry strategy profile."""

from __future__ import annotations

from lifeos.core.insights.inquiry_strategies.base import DomainStrategyProfile

JOURNAL_STRATEGY = DomainStrategyProfile(
    domain="journal",
    profile="focused_inquiry_journal_expert_brief",
    profile_version="1.0.0",
    strategy="journal_rules_v1",
    strategy_version="1.0.0",
    finding_categories=("reflection_cadence", "mood_tag_pattern", "evidence_gap"),
    coverage_category="reflection_cadence",
    signal_category="mood_tag_pattern",
    gap_category="evidence_gap",
    limitation_language=(
        "Journal evidence is descriptive only and limited to explicit recorded entries.",
        "Journal summary is bounded to tags, mood fields, timestamps, and explicit text anchors.",
    ),
    refine_guidance=(
        "Refine by narrowing to a shorter reflection window for clearer cadence signals.",
        "Refine by specifying journal tags or mood filters in the inquiry question.",
    ),
    allowed_claim_prefixes=(
        "Journal evidence includes",
        "Journal derived signals are present",
        "No canonical journal records were found",
    ),
    forbidden_claim_tokens=(
        "diagnosis",
        "depression",
        "anxiety",
        "personality",
        "hidden intent",
        "therapeutic",
        "therapy",
        "trauma",
    ),
    event_priority_prefixes=("journal.entry.created", "journal.entry.updated"),
    insight_priority_kinds=("journal_habit_reflection_link",),
)


__all__ = ["JOURNAL_STRATEGY"]
