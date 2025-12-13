"""Guardrails for read model replay determinism and interfaces."""

from __future__ import annotations

import pytest

from lifeos.readmodels.contracts import ReadModelContract
from lifeos.readmodels.registry import ReadModelRegistry
from lifeos.readmodels.runners.replay_cli import replay_command
from lifeos.readmodels.runners.replay_orchestrator import ReplayOrchestrator


def _sample_contract() -> ReadModelContract:
    return ReadModelContract(
        name="finance.trial_balance_projection",
        domain="finance",
        consumed_events=["finance.journal.posted"],
        replay_start_version=None,
        idempotency_key="entry_id",
        type="aggregate",
        rebuild_strategy="full",
    )


def test_readmodel_contract_shape():
    """Contract should expose required fields for replay metadata."""
    contract = _sample_contract()
    assert contract.name == "finance.trial_balance_projection"
    assert contract.domain == "finance"
    assert contract.consumed_events == ["finance.journal.posted"]
    assert contract.idempotency_key == "entry_id"
    assert contract.type == "aggregate"


def test_registry_interface_raises_not_implemented():
    """Registry is interface-only until concrete implementation is provided."""
    registry = ReadModelRegistry()
    with pytest.raises(NotImplementedError):
        list(registry.list())
    with pytest.raises(NotImplementedError):
        registry.get("anything")


def test_replay_orchestrator_interface_raises_not_implemented():
    """Replay orchestrator interface should clearly signal missing implementation."""
    orchestrator = ReplayOrchestrator()
    contract = _sample_contract()
    with pytest.raises(NotImplementedError):
        orchestrator.replay_all(contract)
    with pytest.raises(NotImplementedError):
        orchestrator.replay_range(contract, start_event_id=1, end_event_id=10, user_ids=[1])


def test_contract_declares_required_invariants():
    """Contract must declare deterministic replay invariants (idempotency key and consumed events)."""
    contract = _sample_contract()
    assert contract.idempotency_key, "idempotency key is required for deterministic upsert/append"
    assert contract.consumed_events, "at least one consumed event is required"


@pytest.mark.xfail(reason="Replay CLI not implemented; should invoke orchestrator deterministically once added.")
def test_replay_cli_invokes_orchestrator():
    """Once implemented, CLI should delegate to orchestrator without side effects."""
    contract = _sample_contract()
    replay_command(contract, start_event_id=1, end_event_id=5, user_id=42)


@pytest.mark.xfail(reason="Replay determinism enforcement pending implementation.")
def test_replay_twice_same_result(monkeypatch):
    """
    Guardrail: the same replay run twice should yield identical projection state.

    When implementation exists, capture projection hashes before/after and assert equality.
    """
    contract = _sample_contract()
    orchestrator = ReplayOrchestrator()
    orchestrator.replay_all(contract)
    orchestrator.replay_all(contract)


@pytest.mark.xfail(reason="Replay should fail fast on out-of-order or missing events once implemented.")
def test_replay_fails_on_sequence_gap():
    """Guardrail: replay must detect sequence gaps and stop rather than silently skip."""
    contract = _sample_contract()
    orchestrator = ReplayOrchestrator()
    # Expectation: implementation should raise on gap; placeholder xfail until logic exists.
    orchestrator.replay_range(contract, start_event_id=10, end_event_id=5)


@pytest.mark.xfail(reason="Idempotency enforcement pending implementation; duplicate events must not double-apply.")
def test_replay_is_idempotent_on_duplicate_events():
    """
    Guardrail: applying the same event range twice should not change the projection after the first pass.

    Expected behavior once implemented: a second replay of identical events is a no-op due to idempotency keys.
    """
    contract = _sample_contract()
    orchestrator = ReplayOrchestrator()
    orchestrator.replay_range(contract, start_event_id=1, end_event_id=3, user_ids=[7])
    orchestrator.replay_range(contract, start_event_id=1, end_event_id=3, user_ids=[7])


@pytest.mark.xfail(reason="Partial replay failure handling to be implemented; replay should abort on errors.")
def test_replay_aborts_on_projection_failure():
    """
    Guardrail: a failure while applying an event should abort the replay and surface an error.

    When implemented, expect a raised exception and no partial projection writes committed past the failure point.
    """
    contract = _sample_contract()
    orchestrator = ReplayOrchestrator()
    orchestrator.replay_range(contract, start_event_id=100, end_event_id=110, user_ids=[99])
