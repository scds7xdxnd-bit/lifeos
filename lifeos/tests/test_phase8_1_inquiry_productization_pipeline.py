"""Phase 8.1 productization pipeline unit tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lifeos.core.insights.inquiry_productization import productize_inquiry_brief

pytestmark = pytest.mark.unit

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "phase8_1_inquiry_productization_golden.json"


def _load_golden() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _finding(
    *,
    claim: str,
    category: str,
    confidence: str = "informational",
    domain: str = "finance",
    source_kind: str = "event_record",
    source_id: int = 1,
) -> dict:
    return {
        "claim": claim,
        "finding_category": category,
        "evidence_refs": [
            {
                "source_kind": source_kind,
                "source_id": source_id,
                "event_type": f"{domain}.event",
                "domain": domain,
                "created_at": "2026-03-01T09:00:00",
            }
        ],
        "confidence_label": confidence,
        "uncertainty_note": "Bounded to selected scope.",
        "source_domains": [domain],
    }


def _fixture_findings(rows: list[dict]) -> list[dict]:
    rendered: list[dict] = []
    for idx, row in enumerate(rows, start=1):
        rendered.append(
            _finding(
                claim=row["claim"],
                category=row["finding_category"],
                confidence=row.get("confidence_label", "informational"),
                domain=row.get("domain", "finance"),
                source_kind=row.get("source_kind", "event_record"),
                source_id=int(row.get("source_id", idx)),
            )
        )
    return rendered


@pytest.mark.parametrize("fixture_key", ["single_domain_finance", "cross_domain_finance_habits"])
def test_productization_golden_outputs_for_required_fields(fixture_key: str):
    fixture = _load_golden()[fixture_key]
    result = productize_inquiry_brief(
        question=fixture["input"]["question"],
        domains=list(fixture["input"]["domains"]),
        findings=_fixture_findings(list(fixture["input"]["findings"])),
        limits=list(fixture["input"]["limits"]),
        incoming_refine_guidance=list(fixture["input"]["incoming_refine_guidance"]),
    )

    expected = fixture["expected"]
    assert result.answerability["classification"] == expected["answerability"]["classification"]
    assert result.direct_answer["text"] == expected["direct_answer"]["text"]
    assert result.direct_answer["supporting_claims"] == expected["direct_answer"]["supporting_claims"]
    assert result.limits == expected["limits"]
    assert result.metadata["limitation_count_before"] == expected["metadata"]["limitation_count_before"]
    assert result.metadata["limitation_count_after"] == expected["metadata"]["limitation_count_after"]
    assert result.metadata["limitation_redundancy_removed"] == expected["metadata"]["limitation_redundancy_removed"]
    assert result.metadata["version"] == expected["metadata"]["version"]
    assert result.findings[0]["claim"] == expected["top_finding"]["claim"]
    assert result.findings[0]["relevance_rank"] == expected["top_finding"]["relevance_rank"]
    assert expected["top_finding"]["relevance_reason_contains"] in result.findings[0]["relevance_reason"]
    for guidance in expected["required_refine_guidance"]:
        assert guidance in result.refine_guidance


def test_productization_is_byte_stable_for_same_input():
    findings = [
        _finding(claim="Finance evidence includes canonical spend records.", category="coverage"),
        _finding(claim="Finance derived signals are present in scope.", category="signal", source_id=2),
    ]
    limits = [
        "finance: Bounded to selected scope.",
        "finance: bounded to selected scope.",
        "Bounded to selected scope.",
    ]
    first = productize_inquiry_brief(
        question="What does finance show this week?",
        domains=["finance"],
        findings=findings,
        limits=limits,
        incoming_refine_guidance=["Narrow timeframe."],
    )
    second = productize_inquiry_brief(
        question="What does finance show this week?",
        domains=["finance"],
        findings=findings,
        limits=limits,
        incoming_refine_guidance=["Narrow timeframe."],
    )
    assert json.dumps(first.__dict__, sort_keys=True) == json.dumps(second.__dict__, sort_keys=True)


def test_productization_baseline_comparison_reduces_redundancy_and_improves_decision_fields():
    result = productize_inquiry_brief(
        question="How do finance and habits align?",
        domains=["finance", "habits"],
        findings=[
            _finding(
                claim="Finance and Habits both have canonical records in scope.",
                category="co_occurrence_observation",
                domain="finance",
            ),
            _finding(
                claim="Coverage gap detected for habits in this window.",
                category="coverage_gap",
                confidence="needs_review",
                domain="habits",
                source_id=3,
            ),
        ],
        limits=[
            "finance: Evidence is bounded to selected scope.",
            "habits: Evidence is bounded to selected scope.",
            "Evidence is bounded to selected scope.",
        ],
        incoming_refine_guidance=["Adjust scope."],
    )
    # Baseline (Phase 8) behavior has no direct answer/answerability/ranked findings and preserves duplicate limits.
    assert result.metadata["limitation_count_before"] == 3
    assert result.metadata["limitation_count_after"] <= 2
    assert result.metadata["limitation_redundancy_removed"] >= 1
    assert result.direct_answer["text"]
    assert result.answerability["classification"] in {
        "strong_answerable",
        "partial_answerable",
        "weak_answerable",
    }
    assert result.refine_guidance
    assert any("Likely gain:" in item for item in result.refine_guidance)
    assert all(item.get("relevance_rank", 0) >= 1 for item in result.findings)
    assert all(item.get("relevance_reason") for item in result.findings)


def test_productization_does_not_remove_required_provenance_refs():
    findings = [
        _finding(
            claim="Coverage gap detected for habits in this window.",
            category="coverage_gap",
            confidence="needs_review",
            domain="habits",
            source_id=31,
        ),
        _finding(
            claim="Finance and Habits both have canonical records in scope.",
            category="co_occurrence_observation",
            confidence="informational",
            domain="finance",
            source_id=17,
        ),
    ]
    baseline_refs_by_claim = {item["claim"]: json.dumps(item["evidence_refs"], sort_keys=True) for item in findings}
    result = productize_inquiry_brief(
        question="How do finance and habits align?",
        domains=["finance", "habits"],
        findings=findings,
        limits=["finance: Bounded to selected scope."],
        incoming_refine_guidance=["Adjust scope."],
    )
    for finding in result.findings:
        claim = finding["claim"]
        assert claim in baseline_refs_by_claim
        assert json.dumps(finding["evidence_refs"], sort_keys=True) == baseline_refs_by_claim[claim]


def test_weak_answerability_remains_bounded_and_non_overstated():
    result = productize_inquiry_brief(
        question="How do finance and habits align?",
        domains=["finance", "habits"],
        findings=[
            {
                "claim": "Coverage gap detected in selected scope.",
                "finding_category": "coverage_gap",
                "evidence_refs": [],
                "confidence_label": "needs_review",
                "uncertainty_note": "Evidence is sparse.",
                "source_domains": ["finance", "habits"],
            }
        ],
        limits=["Cross-domain coverage is incomplete."],
        incoming_refine_guidance=["Adjust scope."],
    )
    assert result.answerability["classification"] == "weak_answerable"
    lower = str(result.direct_answer["text"]).lower()
    for token in ("always", "never", "guarantee", "definitely", "certainly", "caused", "because"):
        assert token not in lower


def test_evidence_backed_gap_only_findings_remain_weak_answerable():
    result = productize_inquiry_brief(
        question="Did my habit pattern persist?",
        domains=["habits"],
        findings=[
            _finding(
                claim="No canonical habits records were found in the selected inquiry timeframe.",
                category="evidence_gap",
                confidence="needs_review",
                domain="habits",
                source_kind="read_model",
                source_id=0,
            )
        ],
        limits=["Habit log evidence is sparse in this timeframe; treat adherence interpretation as partial."],
        incoming_refine_guidance=["Refine by extending timeframe when logs are sparse for selected habits."],
    )
    assert result.answerability["classification"] == "weak_answerable"
    assert result.answerability["supporting_finding_count"] == 1
