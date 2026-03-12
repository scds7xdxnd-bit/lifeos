"""Deterministic inquiry brief quality evaluation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Mapping

CANONICAL_EVIDENCE_SOURCE_KINDS = {"event_record", "insight_record", "read_model"}


def _as_findings(brief_payload: Mapping[str, object]) -> list[dict]:
    raw = brief_payload.get("findings")
    if not isinstance(raw, list):
        return []
    findings: list[dict] = []
    for item in raw:
        if isinstance(item, Mapping):
            findings.append(dict(item))
    return findings


def _finding_has_canonical_evidence(finding: Mapping[str, object]) -> bool:
    refs = finding.get("evidence_refs")
    if not isinstance(refs, list) or not refs:
        return False
    for ref in refs:
        if not isinstance(ref, Mapping):
            continue
        source_kind = str(ref.get("source_kind") or "")
        if source_kind in CANONICAL_EVIDENCE_SOURCE_KINDS:
            return True
    return False


def _domains_from_findings(findings: list[dict]) -> set[str]:
    domains: set[str] = set()
    for finding in findings:
        source_domains = finding.get("source_domains")
        if not isinstance(source_domains, list):
            continue
        for domain in source_domains:
            if isinstance(domain, str) and domain:
                domains.add(domain)
    return domains


def _domains_with_observed_activity(findings: list[dict]) -> set[str]:
    observed: set[str] = set()
    for finding in findings:
        refs = finding.get("evidence_refs")
        if not isinstance(refs, list):
            continue
        for ref in refs:
            if not isinstance(ref, Mapping):
                continue
            domain = str(ref.get("domain") or "")
            if not domain:
                continue
            source_kind = str(ref.get("source_kind") or "")
            if source_kind in {"event_record", "insight_record"}:
                observed.add(domain)
                continue
            if source_kind == "read_model":
                event_count = int(ref.get("event_count") or 0)
                insight_count = int(ref.get("insight_count") or 0)
                if event_count + insight_count > 0:
                    observed.add(domain)
    return observed


def evaluate_inquiry_brief_quality(
    brief_payload: Mapping[str, object],
    *,
    preferred_refine_guidance: Sequence[str] | None = None,
) -> dict[str, object]:
    """Return deterministic quality metadata based on brief evidence structure."""
    findings = _as_findings(brief_payload)
    findings_total = len(findings)
    findings_with_evidence = sum(1 for finding in findings if _finding_has_canonical_evidence(finding))
    evidence_coverage_ratio = round(findings_with_evidence / findings_total, 4) if findings_total > 0 else 0.0

    structure_gaps: list[str] = []
    if findings_total == 0:
        structure_gaps.append("missing_findings")
    if findings_with_evidence < findings_total:
        structure_gaps.append("incomplete_evidence_coverage")

    for idx, finding in enumerate(findings, start=1):
        claim = str(finding.get("claim") or "").strip()
        if not claim:
            structure_gaps.append(f"finding_{idx}_missing_claim")
        if not _finding_has_canonical_evidence(finding):
            structure_gaps.append(f"finding_{idx}_missing_evidence")
        confidence_label = str(finding.get("confidence_label") or "").strip()
        if not confidence_label:
            structure_gaps.append(f"finding_{idx}_missing_confidence_label")
        finding_category = str(finding.get("finding_category") or "").strip()
        if not finding_category:
            structure_gaps.append(f"finding_{idx}_missing_finding_category")

    uncertainty_note = str(brief_payload.get("uncertainty_note") or "").strip()
    if not uncertainty_note:
        structure_gaps.append("missing_uncertainty_note")

    context_block = brief_payload.get("context_non_evidence")
    if not isinstance(context_block, Mapping):
        structure_gaps.append("invalid_context_non_evidence_block")
    else:
        context_label = str(context_block.get("label") or "").strip()
        if context_label != "Context (not evidence)":
            structure_gaps.append("invalid_context_non_evidence_label")

    all_domains = sorted(_domains_from_findings(findings))
    observed_domains = _domains_with_observed_activity(findings)
    sparse_domains = sorted([domain for domain in all_domains if domain not in observed_domains])

    refine_guidance: list[str] = []
    if preferred_refine_guidance:
        for item in preferred_refine_guidance:
            value = str(item or "").strip()
            if value:
                refine_guidance.append(value)
    if findings_total == 0:
        refine_guidance.append("Narrow timeframe or adjust domain scope to include canonical records.")
    if "incomplete_evidence_coverage" in structure_gaps:
        refine_guidance.append("Refine question scope so each finding maps to explicit canonical evidence.")
    if sparse_domains:
        refine_guidance.append("Consider removing sparse domains or extending timeframe for better coverage.")
    if not refine_guidance:
        refine_guidance.append("Current brief structure has sufficient evidence coverage for this scope.")
    # Preserve deterministic order and uniqueness.
    deduped_guidance: list[str] = []
    for item in refine_guidance:
        if item not in deduped_guidance:
            deduped_guidance.append(item)

    return {
        "findings_total": findings_total,
        "findings_with_evidence": findings_with_evidence,
        "evidence_coverage_ratio": evidence_coverage_ratio,
        "structure_gaps": sorted(set(structure_gaps)),
        "sparse_domains": sparse_domains,
        "refine_guidance": deduped_guidance,
    }


__all__ = ["evaluate_inquiry_brief_quality"]
