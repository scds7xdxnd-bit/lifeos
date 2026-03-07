"""Phase 2.5 semantic and insight contract freeze tests."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Set

import pytest

from lifeos.core.events.semantic_contracts import DOMAIN_SEMANTIC_CONTRACTS, EVENT_SEMANTIC_CONTRACTS
from lifeos.core.insights.contracts import CONFIDENCE_VOCABULARY, INSIGHT_CONTRACTS
from lifeos.core.insights.ml.contracts import ML_ATTACHMENT_CONTRACTS, REQUIRED_ML_LOGGING_FIELDS
from lifeos.core.insights.ml.event_schemas import INFERENCE_EVENT_MODELS

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
LIFEOS_ROOT = REPO_ROOT / "lifeos"


def _event_catalog_files() -> list[Path]:
    events_files = list(LIFEOS_ROOT.glob("domains/*/events.py"))
    auth_events = LIFEOS_ROOT / "core" / "auth" / "events.py"
    if auth_events.exists():
        events_files.append(auth_events)
    return events_files


def _load_catalog_event_types() -> Set[str]:
    catalog_events: Set[str] = set()
    for events_file in _event_catalog_files():
        namespace: dict = {}
        exec(events_file.read_text(), namespace)  # nosec: event catalogs only
        catalog = namespace.get("EVENT_CATALOG") or {}
        catalog_events.update(catalog.keys())
    return catalog_events


def _collect_insight_types() -> Set[str]:
    types: Set[str] = set()
    rules_path = LIFEOS_ROOT / "core" / "insights" / "rules"
    for path in rules_path.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            key_values = zip(node.keys, node.values)
            for key, value in key_values:
                if isinstance(key, ast.Constant) and key.value == "type":
                    if isinstance(value, ast.Constant) and isinstance(value.value, str):
                        types.add(value.value)
    return types


def test_domain_semantic_contracts_present():
    required_domains = {
        "auth",
        "calendar",
        "finance",
        "habits",
        "health",
        "skills",
        "projects",
        "relationships",
        "journal",
        "system",
    }
    assert required_domains.issubset(DOMAIN_SEMANTIC_CONTRACTS.keys())


def test_domain_semantic_contracts_have_meaningful_text():
    for contract in DOMAIN_SEMANTIC_CONTRACTS.values():
        assert contract.purpose.strip()
        assert contract.asserts.strip()
        assert contract.must_not_infer.strip()


def test_event_semantic_contracts_cover_catalog():
    catalog_events = _load_catalog_event_types()
    missing = {evt for evt in catalog_events if evt not in EVENT_SEMANTIC_CONTRACTS}
    assert missing == set()


def test_event_catalog_and_semantic_contracts_match_bidirectionally():
    catalog_events = _load_catalog_event_types()
    contract_events = set(EVENT_SEMANTIC_CONTRACTS.keys())
    assert catalog_events == contract_events


def test_event_catalog_has_no_duplicate_event_types():
    duplicates = []
    seen: dict[str, Path] = {}
    for events_file in _event_catalog_files():
        namespace: dict = {}
        exec(events_file.read_text(), namespace)  # nosec: event catalogs only
        catalog = namespace.get("EVENT_CATALOG") or {}
        for event_type in catalog.keys():
            if event_type in seen:
                duplicates.append((event_type, seen[event_type], events_file))
            else:
                seen[event_type] = events_file
    assert duplicates == []


def test_event_semantic_contracts_use_confidence_vocabulary():
    for contract in EVENT_SEMANTIC_CONTRACTS.values():
        assert contract.certainty in CONFIDENCE_VOCABULARY


def test_event_semantic_contracts_match_keys_and_domains():
    for event_type, contract in EVENT_SEMANTIC_CONTRACTS.items():
        assert event_type == contract.event_type
        domain = event_type.split(".")[0]
        assert domain in DOMAIN_SEMANTIC_CONTRACTS


def test_insight_contracts_cover_rule_types():
    rule_types = _collect_insight_types()
    missing = {ins for ins in rule_types if ins not in INSIGHT_CONTRACTS}
    assert missing == set()


def test_insight_contracts_use_confidence_vocabulary():
    for contract in INSIGHT_CONTRACTS.values():
        for band in contract.confidence_bands.keys():
            assert band in CONFIDENCE_VOCABULARY


def test_insight_contracts_have_required_fields():
    for contract in INSIGHT_CONTRACTS.values():
        assert contract.description.strip()
        assert contract.required_evidence
        assert contract.confidence_bands
        assert contract.allowed_actions


def test_insight_contracts_reference_event_semantics():
    for contract in INSIGHT_CONTRACTS.values():
        for evidence in contract.required_evidence:
            assert evidence in EVENT_SEMANTIC_CONTRACTS
        for evidence in contract.disallowed_evidence:
            assert evidence in EVENT_SEMANTIC_CONTRACTS


def test_insight_contracts_disallow_overlap():
    for contract in INSIGHT_CONTRACTS.values():
        required = set(contract.required_evidence)
        disallowed = set(contract.disallowed_evidence)
        assert required.isdisjoint(disallowed)


def test_insight_contracts_require_review_only_for_needs_review_band():
    for contract in INSIGHT_CONTRACTS.values():
        if "needs_review" in contract.confidence_bands:
            assert "review_only" in contract.allowed_actions


def test_insight_contracts_require_review_only_for_uncertain_evidence():
    for contract in INSIGHT_CONTRACTS.values():
        has_uncertain_required = any(
            EVENT_SEMANTIC_CONTRACTS[evidence].certainty == "needs_review" for evidence in contract.required_evidence
        )
        if has_uncertain_required:
            assert "review_only" in contract.allowed_actions


def test_confidence_vocabulary_is_ordered_and_unique():
    assert isinstance(CONFIDENCE_VOCABULARY, tuple)
    assert len(set(CONFIDENCE_VOCABULARY)) == len(CONFIDENCE_VOCABULARY)


def test_ml_attachment_contracts_cover_inference_events():
    inference_events = set(INFERENCE_EVENT_MODELS.keys())
    allowed_events = set()
    for contract in ML_ATTACHMENT_CONTRACTS.values():
        allowed_events.update(contract.allowed_event_types)
    missing = inference_events - allowed_events
    assert missing == set()


def test_ml_attachment_contracts_limit_to_inference_events():
    inference_events = set(INFERENCE_EVENT_MODELS.keys())
    for contract in ML_ATTACHMENT_CONTRACTS.values():
        assert set(contract.allowed_event_types).issubset(inference_events)


def test_ml_attachment_contracts_require_logging_fields():
    for contract in ML_ATTACHMENT_CONTRACTS.values():
        for field_name in REQUIRED_ML_LOGGING_FIELDS:
            assert field_name in contract.required_logging_fields
