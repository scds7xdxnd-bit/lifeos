"""Cross-domain pair strategy profile definitions."""

from __future__ import annotations

from dataclasses import dataclass

ALLOWED_CROSS_DOMAIN_CLAIM_CATEGORIES = (
    "co_occurrence_observation",
    "temporal_alignment",
    "trend_alignment",
    "coverage_gap",
    "structural_dependency_observation",
    "inconsistency_flag",
)


@dataclass(frozen=True)
class CrossDomainPairProfile:
    profile: str
    profile_version: str
    strategy: str
    strategy_version: str
    domains: tuple[str, str]
    limitation_language: tuple[str, str]
    refine_guidance: tuple[str, ...]
    forbidden_claim_tokens: tuple[str, ...]
    allowed_claim_categories: tuple[str, ...] = ALLOWED_CROSS_DOMAIN_CLAIM_CATEGORIES

    @property
    def pair_key(self) -> str:
        return "__".join(sorted(self.domains))

    @property
    def domain(self) -> str:
        return "+".join(sorted(self.domains))


__all__ = ["ALLOWED_CROSS_DOMAIN_CLAIM_CATEGORIES", "CrossDomainPairProfile"]
