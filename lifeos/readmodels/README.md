# Read Models & Replay Orchestrator (Structure Only)

Purpose: host replayable, event-fed read models for queries the transactional model is not optimized for. Read models are derived exclusively from events and must be deterministically rebuildable via replay; no controllers/services write to them.

Scope (Phase 3b):
- Structure and contracts only; no schedulers, parallelism, broker integration, or auto-rebuilds.
- Replay orchestrator coordinates deterministic replays from immutable events into read models.

Placement:
- Top-level `lifeos/readmodels/` to avoid domain leakage; projections live under `readmodels/projections/<domain>/`.

Contracts:
- Each read model declares: `name`, `domain`, `consumed_events`, `replay_start_version`, `idempotency_key`, `type` (`snapshot | timeline | aggregate`), `rebuild_strategy` (full/partial/checkpoint notes).
- If a read model cannot be deterministically rebuilt from events, it is invalid.

Invariants / Forbidden:
- Read models ingest events only; no joins against transactional tables in builders.
- Controllers/services never write read models; replay-only writes via orchestrator.
- Read models never emit domain events or mutate confidence/inference status; FP/FN flags and inference status remain append-only/user-driven.
- Replay must be deterministic: same events → same rows.
- No permission logic inside read models.

Replay Orchestrator (interfaces only):
- Manual replay only (no schedulers): full or selective (by user/model/event range).
- Enforces ordering and idempotency using declared contracts.
- Writes to read model storage only; does not touch domain tables.

ML Integrity Invariants (training/label safety):
- Confidence is immutable: projections must carry confidence as emitted; no recompute/clamp during replay.
- FP/FN flags are passthrough: `is_false_positive` / `is_false_negative` from inference events must remain unchanged; projections never infer FP/FN.
- Status provenance: `status` (inferred/confirmed/rejected/ambiguous/ignored) must stay distinct; confirmed vs inferred must not be merged. Unknown status should be excluded from training by default.
- Version fidelity: `model_version` and `payload_version` must be preserved exactly in projections. Projection changes should use a separate `projection_version` (bumped when projection logic changes).
- Replay fidelity: replay must be bitwise faithful for inference-related fields; no backfilled defaults that alter labels. If fidelity cannot be guaranteed, training should source from the event log instead of projections.
- Label trust: only user-confirmed records should be treated as strong labels; inferred-only rows are weak labels and must be flagged as such in any training dataset.

ML Guardrail Checklist (pre-training on projections):
- Do projections copy through `status`, `confidence`, `model_version`, `payload_version`, FP/FN flags without mutation?
- Is `projection_version` defined and recorded for the data being exported?
- Are inferred vs confirmed rows clearly distinguishable (and filtered appropriately for the task)?
- Can replay reproduce the projection deterministically from the event log? If not, do not train on projections.
- Are weak labels (inferred-only) tagged or excluded per the training recipe?
