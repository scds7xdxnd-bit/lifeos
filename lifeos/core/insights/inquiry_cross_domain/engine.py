"""Deterministic cross-domain synthesis engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from lifeos.core.insights.inquiry_cross_domain.aggregator import (
    NormalizedCrossDomainEvidence,
    aggregate_cross_domain_evidence,
)
from lifeos.core.insights.inquiry_cross_domain.pairs.base import (
    ALLOWED_CROSS_DOMAIN_CLAIM_CATEGORIES,
    CrossDomainPairProfile,
)


@dataclass(frozen=True)
class CrossDomainSynthesisResult:
    findings: list[dict]
    limits: list[str]
    refine_guidance: list[str]
    provenance_refs: list[dict]
    blocked_claim_count: int


def _to_evidence_ref(item: NormalizedCrossDomainEvidence) -> dict:
    return {
        "source_kind": item.source_kind,
        "source_id": item.source_id,
        "source_ref": item.source_ref,
        "event_type": item.event_type,
        "domain": item.source_domain,
        "created_at": item.event_ts,
        "event_count": item.event_count,
        "insight_count": item.insight_count,
    }


def _has_forbidden_token(claim: str, forbidden_tokens: tuple[str, ...]) -> bool:
    lowered = claim.lower()
    return any(token.lower() in lowered for token in forbidden_tokens)


def _category_allowed(category: str, profile: CrossDomainPairProfile) -> bool:
    return category in set(profile.allowed_claim_categories) and category in set(ALLOWED_CROSS_DOMAIN_CLAIM_CATEGORIES)


def _domain_activity_counts(evidence: list[NormalizedCrossDomainEvidence], domain: str) -> tuple[int, int]:
    events = sum(1 for item in evidence if item.source_domain == domain and item.source_kind == "event_record")
    insights = sum(1 for item in evidence if item.source_domain == domain and item.source_kind == "insight_record")
    return events, insights


def _domain_first_ts(evidence: list[NormalizedCrossDomainEvidence], domain: str) -> str | None:
    timestamps = [
        item.event_ts
        for item in evidence
        if item.source_domain == domain and item.source_kind in {"event_record", "insight_record"} and item.event_ts
    ]
    if not timestamps:
        return None
    return sorted(timestamps)[0]


def _append_finding(
    *,
    findings: list[dict],
    profile: CrossDomainPairProfile,
    category: str,
    claim: str,
    evidence_refs: list[dict],
    source_domains: list[str],
    confidence_label: str,
    uncertainty_note: str,
) -> bool:
    if not _category_allowed(category, profile):
        return False
    if _has_forbidden_token(claim, profile.forbidden_claim_tokens):
        return False
    findings.append(
        {
            "claim": claim,
            "finding_category": category,
            "evidence_refs": evidence_refs,
            "confidence_label": confidence_label,
            "uncertainty_note": uncertainty_note,
            "source_domains": source_domains,
        }
    )
    return True


def synthesize_cross_domain_brief(
    *,
    profile: CrossDomainPairProfile,
    timeframe_start: datetime,
    timeframe_end: datetime,
    as_of_ts: datetime,
    events_by_domain: dict[str, list],
    insights_by_domain: dict[str, list],
) -> CrossDomainSynthesisResult:
    domain_a, domain_b = tuple(sorted(profile.domains))
    normalized = aggregate_cross_domain_evidence(
        domains=(domain_a, domain_b),
        timeframe_start=timeframe_start,
        timeframe_end=timeframe_end,
        as_of_ts=as_of_ts,
        events_by_domain=events_by_domain,
        insights_by_domain=insights_by_domain,
    )
    provenance_refs = [_to_evidence_ref(item) for item in normalized]
    evidence_refs = provenance_refs[:6] if provenance_refs else []

    findings: list[dict] = []
    limits = [
        f"{domain_a}+{domain_b}: {profile.limitation_language[0]}",
        f"{domain_a}+{domain_b}: {profile.limitation_language[1]}",
    ]
    blocked_claim_count = 0

    events_a, insights_a = _domain_activity_counts(normalized, domain_a)
    events_b, insights_b = _domain_activity_counts(normalized, domain_b)
    total_a = events_a + insights_a
    total_b = events_b + insights_b
    both_present = total_a > 0 and total_b > 0

    if both_present:
        if not _append_finding(
            findings=findings,
            profile=profile,
            category="co_occurrence_observation",
            claim=f"{domain_a.title()} and {domain_b.title()} both have canonical records in the selected timeframe.",
            evidence_refs=evidence_refs,
            source_domains=[domain_a, domain_b],
            confidence_label="informational" if min(total_a, total_b) >= 2 else "needs_review",
            uncertainty_note=profile.limitation_language[0],
        ):
            blocked_claim_count += 1
    else:
        missing = [domain for domain, total in ((domain_a, total_a), (domain_b, total_b)) if total == 0]
        if not _append_finding(
            findings=findings,
            profile=profile,
            category="coverage_gap",
            claim=f"Coverage gap detected: {', '.join(missing)} lacks canonical records in this timeframe.",
            evidence_refs=evidence_refs,
            source_domains=[domain_a, domain_b],
            confidence_label="needs_review",
            uncertainty_note=profile.limitation_language[0],
        ):
            blocked_claim_count += 1

    ts_a = _domain_first_ts(normalized, domain_a)
    ts_b = _domain_first_ts(normalized, domain_b)
    if ts_a and ts_b:
        dt_a = datetime.fromisoformat(ts_a)
        dt_b = datetime.fromisoformat(ts_b)
        delta_days = abs((dt_a - dt_b).days)
        if delta_days <= 2:
            if not _append_finding(
                findings=findings,
                profile=profile,
                category="temporal_alignment",
                claim=(
                    f"{domain_a.title()} and {domain_b.title()} evidence timestamps are "
                    "temporally aligned in this window."
                ),
                evidence_refs=evidence_refs,
                source_domains=[domain_a, domain_b],
                confidence_label="informational",
                uncertainty_note=profile.limitation_language[1],
            ):
                blocked_claim_count += 1
        else:
            if not _append_finding(
                findings=findings,
                profile=profile,
                category="inconsistency_flag",
                claim=(
                    f"{domain_a.title()} and {domain_b.title()} evidence timestamps are not "
                    "tightly aligned in this window."
                ),
                evidence_refs=evidence_refs,
                source_domains=[domain_a, domain_b],
                confidence_label="needs_review",
                uncertainty_note=profile.limitation_language[1],
            ):
                blocked_claim_count += 1

    if both_present:
        ratio = max(total_a, total_b) / max(min(total_a, total_b), 1)
        if ratio <= 2.0:
            if not _append_finding(
                findings=findings,
                profile=profile,
                category="trend_alignment",
                claim=f"{domain_a.title()} and {domain_b.title()} show aligned evidence volume in this timeframe.",
                evidence_refs=evidence_refs,
                source_domains=[domain_a, domain_b],
                confidence_label="informational",
                uncertainty_note=profile.limitation_language[1],
            ):
                blocked_claim_count += 1
        else:
            if not _append_finding(
                findings=findings,
                profile=profile,
                category="inconsistency_flag",
                claim=f"{domain_a.title()} and {domain_b.title()} evidence volume is uneven in this timeframe.",
                evidence_refs=evidence_refs,
                source_domains=[domain_a, domain_b],
                confidence_label="needs_review",
                uncertainty_note=profile.limitation_language[1],
            ):
                blocked_claim_count += 1

    if not _append_finding(
        findings=findings,
        profile=profile,
        category="structural_dependency_observation",
        claim=f"Cross-domain synthesis is structurally bounded to explicit {domain_a} and {domain_b} records only.",
        evidence_refs=evidence_refs,
        source_domains=[domain_a, domain_b],
        confidence_label="needs_review",
        uncertainty_note=profile.limitation_language[1],
    ):
        blocked_claim_count += 1

    if not findings:
        findings = [
            {
                "claim": "Coverage gap detected in selected cross-domain scope.",
                "finding_category": "coverage_gap",
                "evidence_refs": evidence_refs,
                "confidence_label": "needs_review",
                "uncertainty_note": profile.limitation_language[0],
                "source_domains": [domain_a, domain_b],
            }
        ]

    findings = sorted(
        findings,
        key=lambda item: (
            str(item.get("finding_category") or ""),
            str(item.get("claim") or ""),
        ),
    )
    return CrossDomainSynthesisResult(
        findings=findings,
        limits=limits,
        refine_guidance=list(profile.refine_guidance),
        provenance_refs=provenance_refs,
        blocked_claim_count=blocked_claim_count,
    )


__all__ = ["CrossDomainSynthesisResult", "synthesize_cross_domain_brief"]
