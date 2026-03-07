"""Phase 3b DSD alignment tests for API contracts."""

from __future__ import annotations

import pytest

from lifeos.core.contracts.api_contracts import API_CONTRACTS
from lifeos.core.contracts.api_dsd_mappings import DSD_FIELD_MAPPINGS
from lifeos.core.ux.domain_surface_contracts import DOMAIN_SURFACE_CONTRACTS

pytestmark = pytest.mark.unit

SOURCE_MAP = {
    "user": "user_entered",
    "system": "system_derived",
    "imported": "imported",
}

STABILITY_MAP = {
    "stable": "stable",
    "conditional": "likely_to_change",
}


def _contract_object_fields(contract):
    for obj in contract.schema.objects:
        for field in obj.fields:
            yield obj.name, field


def _contract_response_fields(contract):
    for field in contract.schema.fields:
        yield "Response", field


def _contract_response_fields(contract):
    for field in contract.schema.fields:
        yield "Response", field


def _surface_dsd_field_map(surface_key: str) -> dict[str, tuple[str, str]]:
    surface = DOMAIN_SURFACE_CONTRACTS[surface_key]
    return {field.label: (field.source, field.stability) for field in surface.data_fields}


def test_contract_fields_map_to_dsd_fields():
    for contract in API_CONTRACTS.values():
        if not contract.surface_key:
            continue
        surface_key = contract.surface_key
        mapping = DSD_FIELD_MAPPINGS.get(surface_key, {})
        assert mapping, f"missing DSD mapping for {surface_key}"
        dsd_fields = _surface_dsd_field_map(surface_key)
        for obj_name, field in _contract_response_fields(contract):
            map_key = f"{obj_name}.{field.name}"
            assert map_key in mapping, f"{contract.name} missing mapping for {map_key}"
            dsd_label = mapping[map_key]
            assert dsd_label in dsd_fields, f"{contract.name} mapped label missing in DSD: {dsd_label}"
        for obj_name, field in (*_contract_response_fields(contract), *_contract_object_fields(contract)):
            map_key = f"{obj_name}.{field.name}"
            assert map_key in mapping, f"{contract.name} missing mapping for {map_key}"
            dsd_label = mapping[map_key]
            assert dsd_label in dsd_fields, f"{contract.name} mapped label missing in DSD: {dsd_label}"


def test_contract_authority_matches_dsd():
    for contract in API_CONTRACTS.values():
        if not contract.surface_key:
            continue
        surface_key = contract.surface_key
        mapping = DSD_FIELD_MAPPINGS.get(surface_key, {})
        dsd_fields = _surface_dsd_field_map(surface_key)
        for obj_name, field in _contract_response_fields(contract):
            map_key = f"{obj_name}.{field.name}"
            dsd_label = mapping[map_key]
            dsd_source, dsd_stability = dsd_fields[dsd_label]
            expected_source = SOURCE_MAP[field.source]
            expected_stability = STABILITY_MAP[field.stability]
            assert expected_source == dsd_source, f"{contract.name} source mismatch for {map_key}"
            assert expected_stability == dsd_stability, f"{contract.name} stability mismatch for {map_key}"
        for obj_name, field in (*_contract_response_fields(contract), *_contract_object_fields(contract)):
            map_key = f"{obj_name}.{field.name}"
            dsd_label = mapping[map_key]
            dsd_source, dsd_stability = dsd_fields[dsd_label]
            expected_source = SOURCE_MAP[field.source]
            expected_stability = STABILITY_MAP[field.stability]
            assert expected_source == dsd_source, f"{contract.name} source mismatch for {map_key}"
            assert expected_stability == dsd_stability, f"{contract.name} stability mismatch for {map_key}"
