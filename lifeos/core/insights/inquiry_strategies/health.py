"""Health domain expert inquiry strategy profile."""

from __future__ import annotations

from lifeos.core.insights.inquiry_strategies.base import DomainStrategyProfile

HEALTH_STRATEGY = DomainStrategyProfile(
    domain="health",
    profile="focused_inquiry_health_expert_brief",
    profile_version="1.0.0",
    strategy="health_rules_v1",
    strategy_version="1.0.0",
    finding_categories=("metric_coverage", "trend_signal", "evidence_gap"),
    coverage_category="metric_coverage",
    signal_category="trend_signal",
    gap_category="evidence_gap",
    limitation_language=(
        "Health evidence is descriptive and limited to recorded metrics in the selected timeframe.",
        "Health summary is non-clinical and bounded to explicit baseline/trend records only.",
    ),
    refine_guidance=(
        "Refine by narrowing to one metric family and a tighter time window.",
        "Refine by extending timeframe when recorded metrics are sparse.",
    ),
    allowed_claim_prefixes=(
        "Health evidence includes",
        "Health derived signals are present",
        "No canonical health records were found",
    ),
    forbidden_claim_tokens=(
        "diagnosis",
        "treatment",
        "prescription",
        "clinical",
        "medical risk",
        "disease",
        "syndrome",
        "should take",
    ),
    event_priority_prefixes=(
        "health.metric.updated",
        "health.biometric.logged",
        "health.workout.logged",
        "health.nutrition.logged",
    ),
    insight_priority_kinds=("health_metric", "habits_health_sleep_consistency"),
)


__all__ = ["HEALTH_STRATEGY"]
