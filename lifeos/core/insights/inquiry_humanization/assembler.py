"""Deterministic assembler for Phase 10 inquiry humanization."""

from __future__ import annotations

import hashlib
import json
from typing import Mapping

from lifeos.core.insights.inquiry_humanization.adapters import resolve_adapter
from lifeos.core.insights.inquiry_humanization.contracts import (
    HUMANIZATION_VERSION,
    CanonicalFinding,
    CanonicalLimitation,
    HumanizationMetadata,
    HumanizationRequest,
    HumanizedAnswer,
    HumanizedBlock,
    HumanizedBrief,
    HumanizedSection,
)
from lifeos.core.insights.inquiry_humanization.duplication_reducer import dedupe_blocks
from lifeos.core.insights.inquiry_humanization.evidence_explainer import explain_evidence
from lifeos.core.insights.inquiry_humanization.phrasebook import (
    ANSWERABILITY_HELPERS,
    ANSWERABILITY_LABELS,
    CONFIDENCE_HELPERS,
    SECTION_TITLES,
)
from lifeos.core.insights.inquiry_humanization.section_prioritizer import prioritize_sections
from lifeos.core.insights.inquiry_humanization.structure_compressor import (
    compress_answer,
    compress_claim,
    compress_limit,
    compress_uncertainty,
)


def humanize_inquiry_brief(request: HumanizationRequest) -> HumanizedBrief:
    adapter = resolve_adapter(dict(request.canonical_brief))
    findings = _canonical_findings(request.canonical_brief)
    limitations = _canonical_limitations(request.canonical_brief)
    answer = _answer_block(request.canonical_brief, findings, limitations, adapter.replacements)
    sections = _sections(request.canonical_brief, findings, limitations, adapter.replacements, adapter)
    payload = {
        "answer": {
            "text": answer.text,
            "source_finding_ids": list(answer.source_finding_ids),
            "source_limitation_ids": list(answer.source_limitation_ids),
        },
        "sections": [
            {
                "section_id": section.section_id,
                "title": section.title,
                "blocks": [
                    {
                        "block_id": block.block_id,
                        "text": block.text,
                        "source_finding_ids": list(block.source_finding_ids),
                        "source_limitation_ids": list(block.source_limitation_ids),
                        "evidence_refs": list(block.evidence_refs),
                        "confidence_label": block.confidence_label,
                    }
                    for block in section.blocks
                ],
            }
            for section in sections
        ],
    }
    humanized_hash = hashlib.sha256(
        json.dumps(
            {
                "canonical_brief_hash": request.canonical_brief_hash,
                "humanization_version": HUMANIZATION_VERSION,
                "payload": payload,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return HumanizedBrief(
        metadata=HumanizationMetadata(
            canonical_brief_hash=request.canonical_brief_hash,
            humanization_version=HUMANIZATION_VERSION,
            humanized_brief_hash=humanized_hash,
            technical_view_available=True,
        ),
        answer=answer,
        sections=sections,
    )


def serialize_humanized_brief(brief: HumanizedBrief) -> dict[str, object]:
    return {
        "metadata": {
            "canonical_brief_hash": brief.metadata.canonical_brief_hash,
            "humanization_version": brief.metadata.humanization_version,
            "humanized_brief_hash": brief.metadata.humanized_brief_hash,
            "technical_view_available": brief.metadata.technical_view_available,
        },
        "answer": {
            "text": brief.answer.text,
            "source_finding_ids": list(brief.answer.source_finding_ids),
            "source_limitation_ids": list(brief.answer.source_limitation_ids),
        },
        "sections": [
            {
                "section_id": section.section_id,
                "title": section.title,
                "blocks": [
                    {
                        "block_id": block.block_id,
                        "text": block.text,
                        "source_finding_ids": list(block.source_finding_ids),
                        "source_limitation_ids": list(block.source_limitation_ids),
                        "evidence_refs": list(block.evidence_refs),
                        "confidence_label": block.confidence_label,
                    }
                    for block in section.blocks
                ],
            }
            for section in brief.sections
        ],
    }


def _canonical_findings(brief: Mapping[str, object]) -> tuple[CanonicalFinding, ...]:
    rows: list[CanonicalFinding] = []
    for item in list(brief.get("findings") or []):
        if not isinstance(item, Mapping):
            continue
        finding_id = str(item.get("finding_id") or "").strip()
        if not finding_id:
            continue
        rows.append(
            CanonicalFinding(
                finding_id=finding_id,
                claim=str(item.get("claim") or "").strip(),
                finding_category=str(item.get("finding_category") or "").strip(),
                confidence_label=str(item.get("confidence_label") or "").strip(),
                uncertainty_note=str(item.get("uncertainty_note") or "").strip(),
                source_domains=tuple(
                    str(value) for value in list(item.get("source_domains") or []) if str(value).strip()
                ),
                evidence_refs=tuple(
                    dict(ref) for ref in list(item.get("evidence_refs") or []) if isinstance(ref, Mapping)
                ),
            )
        )
    return tuple(rows)


def _canonical_limitations(brief: Mapping[str, object]) -> tuple[CanonicalLimitation, ...]:
    rows: list[CanonicalLimitation] = []
    for item in list(brief.get("limitation_items") or []):
        if not isinstance(item, Mapping):
            continue
        limitation_id = str(item.get("limitation_id") or "").strip()
        text = str(item.get("text") or "").strip()
        if limitation_id and text:
            rows.append(CanonicalLimitation(limitation_id=limitation_id, text=text))
    return tuple(rows)


def _answer_block(
    brief: Mapping[str, object],
    findings: tuple[CanonicalFinding, ...],
    limitations: tuple[CanonicalLimitation, ...],
    replacements: tuple[tuple[str, str], ...],
) -> HumanizedAnswer:
    direct_answer = brief.get("direct_answer") if isinstance(brief.get("direct_answer"), Mapping) else {}
    text = compress_answer(str(direct_answer.get("text") or ""), replacements=replacements)
    if not text:
        text = compress_answer(str(brief.get("summary") or ""), replacements=replacements)
    source_finding_ids = tuple(_supporting_finding_ids(direct_answer, findings))
    if not source_finding_ids:
        source_finding_ids = tuple(item.finding_id for item in findings[:2])
    source_limitation_ids: tuple[str, ...] = ()
    if not text and limitations:
        text = compress_limit(limitations[0].text, replacements=replacements)
        source_limitation_ids = (limitations[0].limitation_id,)
    return HumanizedAnswer(
        text=text,
        source_finding_ids=source_finding_ids,
        source_limitation_ids=source_limitation_ids,
    )


def _sections(
    brief: Mapping[str, object],
    findings: tuple[CanonicalFinding, ...],
    limitations: tuple[CanonicalLimitation, ...],
    replacements: tuple[tuple[str, str], ...],
    adapter,
) -> tuple[HumanizedSection, ...]:
    sections_by_id = {
        "what_stands_out": _what_stands_out(findings, replacements),
        "why_it_matters": _why_it_matters(findings, adapter),
        "how_sure_this_is": _how_sure(brief, findings, limitations, replacements),
        "what_to_review_next": _what_to_review(limitations, replacements),
    }
    ordered: list[HumanizedSection] = []
    for section_id in prioritize_sections(list(sections_by_id.keys())):
        section = sections_by_id[section_id]
        if section.blocks:
            ordered.append(section)
    return tuple(ordered)


def _what_stands_out(
    findings: tuple[CanonicalFinding, ...], replacements: tuple[tuple[str, str], ...]
) -> HumanizedSection:
    blocks = [
        HumanizedBlock(
            block_id=f"what_stands_out:{item.finding_id}",
            text=compress_claim(item.claim, replacements=replacements),
            source_finding_ids=(item.finding_id,),
            source_limitation_ids=(),
            evidence_refs=item.evidence_refs,
            confidence_label=item.confidence_label,
        )
        for item in findings
        if item.claim
    ]
    return HumanizedSection(
        section_id="what_stands_out",
        title=SECTION_TITLES["what_stands_out"],
        blocks=dedupe_blocks(blocks),
    )


def _why_it_matters(findings: tuple[CanonicalFinding, ...], adapter) -> HumanizedSection:
    blocks = [
        HumanizedBlock(
            block_id=f"why_it_matters:{item.finding_id}",
            text=explain_evidence(item, adapter),
            source_finding_ids=(item.finding_id,),
            source_limitation_ids=(),
            evidence_refs=item.evidence_refs,
            confidence_label=item.confidence_label,
        )
        for item in findings
    ]
    return HumanizedSection(
        section_id="why_it_matters",
        title=SECTION_TITLES["why_it_matters"],
        blocks=dedupe_blocks(blocks),
    )


def _how_sure(
    brief: Mapping[str, object],
    findings: tuple[CanonicalFinding, ...],
    limitations: tuple[CanonicalLimitation, ...],
    replacements: tuple[tuple[str, str], ...],
) -> HumanizedSection:
    answerability = brief.get("answerability") if isinstance(brief.get("answerability"), Mapping) else {}
    classification = str(answerability.get("classification") or "weak_answerable")
    blocks: list[HumanizedBlock] = [
        HumanizedBlock(
            block_id="how_sure:this_brief",
            text=(
                f"{ANSWERABILITY_LABELS.get(classification, 'Weakly answerable')}. "
                f"{ANSWERABILITY_HELPERS.get(classification, ANSWERABILITY_HELPERS['weak_answerable'])}"
            ),
            source_finding_ids=tuple(item.finding_id for item in findings),
            source_limitation_ids=tuple(item.limitation_id for item in limitations),
            evidence_refs=tuple(ref for item in findings for ref in item.evidence_refs)[:6],
            confidence_label=None,
        )
    ]
    for item in findings:
        note = compress_uncertainty(item.uncertainty_note, replacements=replacements)
        helper = CONFIDENCE_HELPERS.get(
            item.confidence_label, "Confidence remains at the canonical level shown in the technical brief."
        )
        blocks.append(
            HumanizedBlock(
                block_id=f"how_sure:{item.finding_id}",
                text=f"{helper} {note}".strip(),
                source_finding_ids=(item.finding_id,),
                source_limitation_ids=(),
                evidence_refs=item.evidence_refs,
                confidence_label=item.confidence_label,
            )
        )
    return HumanizedSection(
        section_id="how_sure_this_is",
        title=SECTION_TITLES["how_sure_this_is"],
        blocks=dedupe_blocks(blocks),
    )


def _what_to_review(
    limitations: tuple[CanonicalLimitation, ...], replacements: tuple[tuple[str, str], ...]
) -> HumanizedSection:
    blocks = [
        HumanizedBlock(
            block_id=f"what_to_review_next:{item.limitation_id}",
            text=compress_limit(item.text, replacements=replacements),
            source_finding_ids=(),
            source_limitation_ids=(item.limitation_id,),
            evidence_refs=(),
            confidence_label=None,
        )
        for item in limitations
    ]
    return HumanizedSection(
        section_id="what_to_review_next",
        title=SECTION_TITLES["what_to_review_next"],
        blocks=dedupe_blocks(blocks),
    )


def _supporting_finding_ids(direct_answer: Mapping[str, object], findings: tuple[CanonicalFinding, ...]) -> list[str]:
    supporting_claims = [
        str(item).strip() for item in list(direct_answer.get("supporting_claims") or []) if str(item).strip()
    ]
    ids: list[str] = []
    remaining = list(findings)
    for claim in supporting_claims:
        for index, finding in enumerate(remaining):
            if finding.claim == claim:
                ids.append(finding.finding_id)
                remaining.pop(index)
                break
    return ids


__all__ = ["humanize_inquiry_brief", "serialize_humanized_brief"]
