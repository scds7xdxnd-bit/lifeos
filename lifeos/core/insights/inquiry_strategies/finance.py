"""Finance domain expert inquiry strategy profile."""

from __future__ import annotations

from lifeos.core.insights.inquiry_strategies.base import DomainStrategyProfile

FINANCE_STRATEGY = DomainStrategyProfile(
    domain="finance",
    profile="finance_domain_expert_brief",
    profile_version="1.0.0",
    strategy="finance_rules_v1",
    strategy_version="1.0.0",
    finding_categories=("cashflow_coverage", "ledger_signal", "evidence_gap"),
    coverage_category="cashflow_coverage",
    signal_category="ledger_signal",
    gap_category="evidence_gap",
    limitation_language=(
        "Finance evidence is partial in this timeframe; treat totals as directional.",
        "Finance evidence is bounded to this timeframe and account activity scope.",
    ),
    refine_guidance=(
        "Refine by narrowing timeframe around posting days for higher finance evidence density.",
        "Refine by focusing on one account scope if the brief spans mixed finance activity.",
    ),
    allowed_claim_prefixes=(
        "Finance evidence includes",
        "Finance derived signals are present",
        "No canonical finance records were found",
    ),
    forbidden_claim_tokens=("because", "caused", "guarantee", "always", "never", "must"),
    event_priority_prefixes=(
        "finance.journal.posted",
        "finance.transaction.created",
        "finance.schedule.",
        "finance.receivable.",
    ),
    insight_priority_kinds=("journal_posted", "finance_spend"),
)


__all__ = ["FINANCE_STRATEGY"]
