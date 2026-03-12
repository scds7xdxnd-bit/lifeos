"""Cross-domain pair profile: relationships + journal."""

from __future__ import annotations

from lifeos.core.insights.inquiry_cross_domain.pairs.base import CrossDomainPairProfile

RELATIONSHIPS_JOURNAL_V1 = CrossDomainPairProfile(
    profile="relationships_journal_v1",
    profile_version="1.0.0",
    strategy="cross_domain_pair_rules_v1",
    strategy_version="1.0.0",
    domains=("relationships", "journal"),
    limitation_language=(
        "Cross-domain synthesis is descriptive and bounded to explicit relationships and journal records.",
        "No relationship quality judgment or intent inference is applied.",
    ),
    refine_guidance=(
        "Refine by narrowing to a shorter social interaction cadence window.",
        "Refine by focusing journal scope on explicit entries linked to selected timeframe.",
    ),
    forbidden_claim_tokens=("toxic", "moral", "intent", "emotion of", "personality"),
)


__all__ = ["RELATIONSHIPS_JOURNAL_V1"]
