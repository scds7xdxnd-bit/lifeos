"""Deterministic inquiry productization layer (Phase 8.1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

ANSWERABILITY_CLASSES = (
    "strong_answerable",
    "partial_answerable",
    "weak_answerable",
)

CANONICAL_EVIDENCE_SOURCE_KINDS = {"event_record", "insight_record", "read_model"}
_GAP_ONLY_CATEGORIES = {"coverage_gap", "evidence_gap"}
_CONFIDENCE_RANK = {
    "confirmed": 3,
    "informational": 2,
    "suggested": 1,
    "needs_review": 0,
}
_CATEGORY_PRIORITY = {
    "approved_pair_alignment_persistence": 9,
    "baseline_relative_change": 8,
    "prior_window_comparison": 7,
    "recurrence_observation": 6,
    "continuity_or_break": 5,
    "trend_direction": 4,
    "volatility_description": 3,
    "episodic_vs_sustained": 2,
    "coverage_gap": 6,
    "inconsistency_flag": 5,
    "temporal_alignment": 4,
    "trend_alignment": 3,
    "co_occurrence_observation": 2,
    "structural_dependency_observation": 1,
}
_QUESTION_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "this",
    "that",
    "from",
    "into",
    "about",
    "what",
    "how",
    "when",
    "where",
    "which",
    "does",
    "did",
    "have",
    "has",
    "show",
    "look",
    "across",
}


@dataclass(frozen=True)
class ProductizedInquiryBrief:
    findings: list[dict]
    limits: list[str]
    uncertainty_note: str
    direct_answer: dict[str, object]
    answerability: dict[str, object]
    refine_guidance: list[str]
    bounded_patterns: list[dict[str, object]]
    metadata: dict[str, object]


def _tokens(value: str) -> list[str]:
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in str(value or ""))
    return [item for item in cleaned.split() if len(item) > 2 and item not in _QUESTION_STOPWORDS]


def _canonical_evidence_count(finding: Mapping[str, object]) -> int:
    refs = finding.get("evidence_refs")
    if not isinstance(refs, list):
        return 0
    count = 0
    for ref in refs:
        if not isinstance(ref, Mapping):
            continue
        if str(ref.get("source_kind") or "") in CANONICAL_EVIDENCE_SOURCE_KINDS:
            count += 1
    return count


def _finding_relevance_key(
    finding: Mapping[str, object],
    *,
    question_tokens: set[str],
    index: int,
) -> tuple[int, int, int, int, str, int]:
    claim = str(finding.get("claim") or "")
    overlap = len(question_tokens.intersection(set(_tokens(claim))))
    evidence_count = _canonical_evidence_count(finding)
    confidence_rank = _CONFIDENCE_RANK.get(str(finding.get("confidence_label") or ""), 0)
    category_rank = _CATEGORY_PRIORITY.get(str(finding.get("finding_category") or ""), 0)
    # Descending by relevance factors, ascending lexical as tie-break.
    return (
        -overlap,
        -evidence_count,
        -confidence_rank,
        -category_rank,
        claim.lower(),
        index,
    )


def _relevance_reason(*, overlap: int, evidence_count: int) -> str:
    if overlap > 0 and evidence_count > 0:
        return "High relevance: claim matches inquiry wording and has canonical evidence."
    if evidence_count > 0:
        return "Moderate relevance: claim is supported by canonical evidence."
    if overlap > 0:
        return "Moderate relevance: claim wording aligns with inquiry scope."
    return "Lower relevance: limited direct wording alignment or sparse canonical evidence."


def _answerability_from_findings(findings: list[dict]) -> dict[str, object]:
    total = len(findings)
    if total <= 0:
        return {
            "classification": "weak_answerable",
            "reason": "No findings were generated from canonical evidence.",
            "evidence_coverage_ratio": 0.0,
            "supporting_finding_count": 0,
        }
    with_evidence = sum(1 for finding in findings if _canonical_evidence_count(finding) > 0)
    high_confidence = sum(
        1
        for finding in findings
        if _CONFIDENCE_RANK.get(str(finding.get("confidence_label") or ""), 0) >= _CONFIDENCE_RANK["informational"]
    )
    only_gap_findings = all(str(finding.get("finding_category") or "") in _GAP_ONLY_CATEGORIES for finding in findings)
    coverage_ratio = round(with_evidence / total, 4) if total else 0.0
    if only_gap_findings and high_confidence <= 0:
        return {
            "classification": "weak_answerable",
            "reason": "Only coverage-gap findings were generated for the selected scope.",
            "evidence_coverage_ratio": coverage_ratio,
            "supporting_finding_count": with_evidence,
        }
    if coverage_ratio >= 0.85 and high_confidence >= 1:
        return {
            "classification": "strong_answerable",
            "reason": "Most findings are evidence-backed and at least one has informational-or-higher confidence.",
            "evidence_coverage_ratio": coverage_ratio,
            "supporting_finding_count": with_evidence,
        }
    if coverage_ratio >= 0.5:
        return {
            "classification": "partial_answerable",
            "reason": "Findings are partially evidence-backed, but coverage or confidence is mixed.",
            "evidence_coverage_ratio": coverage_ratio,
            "supporting_finding_count": with_evidence,
        }
    return {
        "classification": "weak_answerable",
        "reason": "Evidence coverage is limited for the selected scope.",
        "evidence_coverage_ratio": coverage_ratio,
        "supporting_finding_count": with_evidence,
    }


def _direct_answer_from_findings(
    *,
    findings: list[dict],
    answerability: Mapping[str, object],
) -> dict[str, object]:
    classification = str(answerability.get("classification") or "weak_answerable")
    supporting_claims = [
        str(item.get("claim") or "").strip() for item in findings if str(item.get("claim") or "").strip()
    ]
    top_claims = supporting_claims[:2]
    if not top_claims:
        text = "Canonical evidence is too sparse in the selected scope to provide a direct answer."
    elif classification == "strong_answerable":
        text = " ".join(top_claims)
    elif classification == "partial_answerable":
        text = f"Partial answer: {top_claims[0]}"
    else:
        text = f"Weak answer: {top_claims[0]}"
    return {
        "text": text,
        "supporting_claims": top_claims,
        "note": "Derived only from evidence-bounded findings; no new inference classes were introduced.",
    }


def _limitation_dedup_key(item: str, *, domains: list[str]) -> str:
    value = " ".join(str(item or "").strip().split())
    if not value:
        return ""
    if ":" in value:
        prefix, suffix = value.split(":", 1)
        if prefix.strip().lower() in {domain.lower() for domain in domains}:
            value = suffix.strip()
    return value.lower()


def _dedup_limits(limits: list[str], *, domains: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for item in limits:
        rendered = " ".join(str(item or "").strip().split())
        if not rendered:
            continue
        key = _limitation_dedup_key(rendered, domains=domains)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(rendered)
    return deduped


def _bounded_patterns(findings: list[dict]) -> list[dict[str, object]]:
    counts: dict[str, int] = {}
    for finding in findings:
        category = str(finding.get("finding_category") or "").strip()
        if not category:
            continue
        counts[category] = counts.get(category, 0) + 1
    rows = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    patterns: list[dict[str, object]] = []
    for category, count in rows[:3]:
        patterns.append(
            {
                "pattern_category": category,
                "finding_count": int(count),
                "note": "Descriptive pattern synthesized from canonical findings only.",
            }
        )
    return patterns


def _improve_refine_guidance(
    *,
    incoming_guidance: list[str],
    answerability: Mapping[str, object],
    findings: list[dict],
    question_tokens: set[str],
) -> list[str]:
    classification = str(answerability.get("classification") or "weak_answerable")
    improved: list[str] = []
    for item in incoming_guidance:
        value = str(item or "").strip()
        if not value:
            continue
        improved.append(value)
        if "Likely gain:" in value:
            continue
        improved.append(f"{value} Likely gain: improve evidence relevance or answerability clarity.")

    if classification == "weak_answerable":
        improved.append(
            "Refine by narrowing to a shorter timeframe with known activity. "
            "Likely gain: move from weak to partial answerability."
        )
    elif classification == "partial_answerable":
        improved.append(
            "Refine by tightening scope to one dominant pattern category. "
            "Likely gain: reduce mixed evidence and improve directness."
        )
    else:
        improved.append(
            "Refine by isolating one sub-question in the same scope. "
            "Likely gain: improve precision without broadening inference scope."
        )

    has_gap = any(str(item.get("finding_category") or "") == "coverage_gap" for item in findings)
    if has_gap:
        improved.append(
            "Refine by removing missing-coverage domains or extending the window. "
            "Likely gain: reduce coverage gaps and increase answerability."
        )

    if question_tokens:
        finding_tokens = set()
        for finding in findings:
            finding_tokens.update(_tokens(str(finding.get("claim") or "")))
        if question_tokens.isdisjoint(finding_tokens):
            improved.append(
                "Refine by rephrasing the question with explicit domain terms seen in findings. "
                "Likely gain: higher relevance alignment."
            )

    deduped: list[str] = []
    for item in improved:
        if item not in deduped:
            deduped.append(item)
    return deduped


def productize_inquiry_brief(
    *,
    question: str,
    domains: list[str],
    findings: list[dict],
    limits: list[str],
    incoming_refine_guidance: list[str],
) -> ProductizedInquiryBrief:
    question_tokens = set(_tokens(question))

    indexed_findings = [(idx, dict(item)) for idx, item in enumerate(findings)]
    ranked_findings = [
        item
        for _, item in sorted(
            indexed_findings,
            key=lambda row: _finding_relevance_key(row[1], question_tokens=question_tokens, index=row[0]),
        )
    ]
    for idx, finding in enumerate(ranked_findings, start=1):
        overlap = len(question_tokens.intersection(set(_tokens(str(finding.get("claim") or "")))))
        evidence_count = _canonical_evidence_count(finding)
        finding["relevance_rank"] = idx
        finding["relevance_reason"] = _relevance_reason(overlap=overlap, evidence_count=evidence_count)

    answerability = _answerability_from_findings(ranked_findings)
    direct_answer = _direct_answer_from_findings(findings=ranked_findings, answerability=answerability)
    deduped_limits = _dedup_limits([str(item) for item in limits], domains=domains)
    uncertainty_note = (
        "Evidence is bounded to selected scope and timeframe." if not deduped_limits else " ; ".join(deduped_limits)
    )
    refine_guidance = _improve_refine_guidance(
        incoming_guidance=incoming_refine_guidance,
        answerability=answerability,
        findings=ranked_findings,
        question_tokens=question_tokens,
    )
    bounded_patterns = _bounded_patterns(ranked_findings)
    metadata = {
        "version": "phase8_1_productization_v1",
        "limitation_count_before": len(limits),
        "limitation_count_after": len(deduped_limits),
        "limitation_redundancy_removed": max(0, len(limits) - len(deduped_limits)),
        "direct_answer_present": bool(str(direct_answer.get("text") or "").strip()),
    }
    return ProductizedInquiryBrief(
        findings=ranked_findings,
        limits=deduped_limits,
        uncertainty_note=uncertainty_note,
        direct_answer=direct_answer,
        answerability=answerability,
        refine_guidance=refine_guidance,
        bounded_patterns=bounded_patterns,
        metadata=metadata,
    )


__all__ = ["ANSWERABILITY_CLASSES", "ProductizedInquiryBrief", "productize_inquiry_brief"]
