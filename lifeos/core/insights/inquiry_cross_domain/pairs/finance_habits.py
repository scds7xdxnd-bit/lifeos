"""Cross-domain pair profile: finance + habits."""

from __future__ import annotations

from lifeos.core.insights.inquiry_cross_domain.pairs.base import CrossDomainPairProfile

FINANCE_HABITS_V1 = CrossDomainPairProfile(
    profile="finance_habits_v1",
    profile_version="1.0.0",
    strategy="cross_domain_pair_rules_v1",
    strategy_version="1.0.0",
    domains=("finance", "habits"),
    limitation_language=(
        "Cross-domain synthesis is descriptive and bounded to explicit finance and habits records.",
        "No causal interpretation is applied across domains.",
    ),
    refine_guidance=(
        "Refine by tightening timeframe to check co-occurrence windows.",
        "Refine by clarifying whether spend or adherence cadence is primary.",
    ),
    forbidden_claim_tokens=("caused", "because", "diagnosis", "treatment", "therapy"),
)


__all__ = ["FINANCE_HABITS_V1"]
