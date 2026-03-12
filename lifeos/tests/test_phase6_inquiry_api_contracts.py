"""Phase 6 inquiry API contract freeze tests."""

from __future__ import annotations

import pytest

from lifeos.core.contracts.api_contracts import API_CONTRACTS, compute_schema_hash
from lifeos.core.contracts.api_dsd_mappings import DSD_FIELD_MAPPINGS

pytestmark = pytest.mark.unit


INQUIRY_CONTRACT_KEYS = {
    "inquiries.create.v1",
    "inquiries.list.v1",
    "inquiries.detail.v1",
    "inquiries.refine.v1",
}


def _contract_object_fields(contract_name: str) -> set[str]:
    contract = API_CONTRACTS[contract_name]
    fields: set[str] = set()
    for obj in contract.schema.objects:
        for field in obj.fields:
            fields.add(field.name)
    return fields


def test_inquiry_contracts_exist_with_expected_paths_and_methods():
    expected = {
        "inquiries.create.v1": ("POST", "/api/v1/inquiries"),
        "inquiries.list.v1": ("GET", "/api/v1/inquiries"),
        "inquiries.detail.v1": ("GET", "/api/v1/inquiries/<id>"),
        "inquiries.refine.v1": ("POST", "/api/v1/inquiries/<id>/refine"),
    }
    assert INQUIRY_CONTRACT_KEYS.issubset(API_CONTRACTS.keys())
    for name, (method, path) in expected.items():
        contract = API_CONTRACTS[name]
        assert contract.method == method
        assert contract.path == path
        assert contract.surface_key == "insights:inquiry"


def test_inquiry_routes_are_registered(app):
    rule_map: dict[str, set[str]] = {}
    for rule in app.url_map.iter_rules():
        methods = rule_map.setdefault(rule.rule, set())
        methods.update(rule.methods)
    base = "/api/v1/inquiries"
    base_slash = "/api/v1/inquiries/"
    assert any(path in rule_map for path in (base, base_slash))
    base_methods = rule_map.get(base) or rule_map.get(base_slash) or set()
    assert "GET" in base_methods
    assert "POST" in base_methods
    assert "GET" in (rule_map.get("/api/v1/inquiries/<int:inquiry_id>") or set())
    assert "POST" in (rule_map.get("/api/v1/inquiries/<int:inquiry_id>/refine") or set())


def test_inquiry_contract_schema_hashes_match():
    for name in INQUIRY_CONTRACT_KEYS:
        contract = API_CONTRACTS[name]
        assert compute_schema_hash(contract.schema) == contract.schema_hash


def test_inquiry_contracts_include_canonical_brief_fields():
    fields = set()
    for name in INQUIRY_CONTRACT_KEYS:
        fields.update(_contract_object_fields(name))
    required = {"claim", "evidence_refs", "confidence_label", "uncertainty_note", "context_non_evidence"}
    assert required.issubset(fields)


def test_inquiry_dsd_mappings_exist():
    mapping = DSD_FIELD_MAPPINGS.get("insights:inquiry")
    assert mapping
    required = {
        "InquiryFindingItem.claim",
        "InquiryFindingItem.evidence_refs",
        "InquiryFindingItem.confidence_label",
        "InquiryFindingItem.uncertainty_note",
        "InquiryBriefItem.context_non_evidence",
    }
    assert required.issubset(mapping.keys())
