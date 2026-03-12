"""Cross-domain pair profile: journal + habits."""

from __future__ import annotations

from lifeos.core.insights.inquiry_cross_domain.pairs.base import CrossDomainPairProfile

JOURNAL_HABITS_V1 = CrossDomainPairProfile(
    profile="journal_habits_v1",
    profile_version="1.0.0",
    strategy="cross_domain_pair_rules_v1",
    strategy_version="1.0.0",
    domains=("journal", "habits"),
    limitation_language=(
        "Cross-domain synthesis is descriptive and bounded to explicit journal and habits records.",
        "No psychological interpretation is applied across domains.",
    ),
    refine_guidance=(
        "Refine by narrowing to specific journal reflection windows.",
        "Refine by clarifying which habit cadence to compare against journal records.",
    ),
    forbidden_claim_tokens=("diagnosis", "personality", "hidden intent", "therapy", "trauma"),
)


__all__ = ["JOURNAL_HABITS_V1"]
