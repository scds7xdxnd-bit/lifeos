"""Cross-domain pair profile: projects + calendar."""

from __future__ import annotations

from lifeos.core.insights.inquiry_cross_domain.pairs.base import CrossDomainPairProfile

PROJECTS_CALENDAR_V1 = CrossDomainPairProfile(
    profile="projects_calendar_v1",
    profile_version="1.0.0",
    strategy="cross_domain_pair_rules_v1",
    strategy_version="1.0.0",
    domains=("projects", "calendar"),
    limitation_language=(
        "Cross-domain synthesis is descriptive and bounded to explicit projects and calendar records.",
        "No causal interpretation is applied across domains.",
    ),
    refine_guidance=(
        "Refine by narrowing to one project delivery window and matching calendar period.",
        "Refine by extending timeframe when either domain has sparse records.",
    ),
    forbidden_claim_tokens=("caused", "because", "guarantee", "always", "never"),
)


__all__ = ["PROJECTS_CALENDAR_V1"]
