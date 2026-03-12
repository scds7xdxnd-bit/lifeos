"""Cross-domain pair profile: health + habits."""

from __future__ import annotations

from lifeos.core.insights.inquiry_cross_domain.pairs.base import CrossDomainPairProfile

HEALTH_HABITS_V1 = CrossDomainPairProfile(
    profile="health_habits_v1",
    profile_version="1.0.0",
    strategy="cross_domain_pair_rules_v1",
    strategy_version="1.0.0",
    domains=("health", "habits"),
    limitation_language=(
        "Cross-domain synthesis is descriptive and bounded to explicit health and habits records.",
        "No diagnosis, treatment, or medical risk scoring is applied.",
    ),
    refine_guidance=(
        "Refine by narrowing to one metric family and one habit cadence window.",
        "Refine by extending timeframe when health metric coverage is sparse.",
    ),
    forbidden_claim_tokens=("diagnosis", "treatment", "clinical", "medical risk", "prescription"),
)


__all__ = ["HEALTH_HABITS_V1"]
