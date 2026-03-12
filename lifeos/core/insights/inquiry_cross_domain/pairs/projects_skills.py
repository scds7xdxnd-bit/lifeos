"""Cross-domain pair profile: projects + skills."""

from __future__ import annotations

from lifeos.core.insights.inquiry_cross_domain.pairs.base import CrossDomainPairProfile

PROJECTS_SKILLS_V1 = CrossDomainPairProfile(
    profile="projects_skills_v1",
    profile_version="1.0.0",
    strategy="cross_domain_pair_rules_v1",
    strategy_version="1.0.0",
    domains=("projects", "skills"),
    limitation_language=(
        "Cross-domain synthesis is descriptive and bounded to explicit projects and skills records.",
        "No causal interpretation is applied across domains.",
    ),
    refine_guidance=(
        "Refine by narrowing to one project interval and matching skill practice window.",
        "Refine by extending timeframe when either domain has sparse evidence.",
    ),
    forbidden_claim_tokens=("caused", "because", "guarantee", "always", "never"),
)


__all__ = ["PROJECTS_SKILLS_V1"]
