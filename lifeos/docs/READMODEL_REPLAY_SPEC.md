# Read Model Replay Orchestrator Spec (Structure Only)

## Purpose
Enable deterministic, replayable read models derived exclusively from events, without touching domain tables. Provide contracts and a minimal replay scaffold; no schedulers, no parallelism, no broker, no auto-rebuilds in this phase.

## Non-Goals (Phase 3b scope)
- No schedulers or cron triggers
- No parallel replay engine
- No broker dependency (stay on outbox + in-process bus)
- No auto-triggered rebuilds
- No implementation code (interfaces/structure only)

## Folder Structure (additive)
```
lifeos/
  readmodels/
    README.md                 # purpose, taxonomy, rules
    contracts.py              # read model contract definitions
    registry.py               # declarative registry of read models
    runners/
      replay_orchestrator.py  # interfaces for replay coordination
      replay_cli.py           # manual replay entrypoint (contract only)
    projections/
      __init__.py
      finance/
      calendar/
      insights/
      health/
      habits/
      projects/
      relationships/
      journal/
```

## Contracts (conceptual)
- Each read model declares:
  - `consumed_events`: list of event types
  - `replay_start_version`: event version boundary
  - `idempotency_key`: ensures deterministic upsert/append
  - `type`: snapshot | timeline | aggregate
  - `rebuild_strategy`: full/partial rules, checkpoints (if any)
- If a read model cannot be deterministically rebuilt from events, it is invalid.

## Registry
- `registry.py` exposes a registry of declared read models by name/domain; purely declarative.

## Replay Orchestrator (interfaces only)
- `runners/replay_orchestrator.py`:
  - Replays immutable events into read models
  - Supports full replay and selective replay (by user, event range, model)
  - Enforces ordering and idempotency
  - Does not depend on domain tables
- `runners/replay_cli.py`:
  - Manual command contract: “replay events X→Y into read model Z for user U”
  - No scheduling or parallelism

## Data Flow (textual)
- Source: immutable events (event_record/outbox pipeline)
- Input: ordered event stream + read model contract
- Output: read model storage (documented per projection; storage-agnostic)
- No writes from controllers/services; read models are fed by replay only.

## Invariants & Guardrails
- Event-fed only; no transactional table joins in builders
- Controllers/services never write read models
- Read models never emit domain events or mutate confidence/inference status
- Replay must be deterministic: same events → same rows
- Placement: top-level `lifeos/readmodels/` (not in domains)

## Future Extensions (not now)
- Schedulers/cron for batch replays
- Parallel replay execution
- Broker integration for high volume
- Projection versioning and migrations
- Storage-specific optimizations (materialized views, Redis, columnar)

## Database Expectations (DB View)
- Storage shape: default to ordinary tables in a dedicated schema (e.g., `readmodels.*`). Materialized views are allowed only when backed by deterministic SQL over replayed tables; ephemeral/scratch tables must live in the same schema and be cleaned per run.
- Idempotency: every projection must expose an idempotency key (e.g., `(model_version, entity_id, event_id)` or `(model_version, event_stream_id, event_version)`) with a unique index to guarantee deterministic upsert/append semantics under replay.
- Ordering: replayers must apply events in a globally deterministic order (e.g., `event_record.id`/`event_version` ASC). DB-side constraints should not depend on arrival order beyond that monotone sequence.
- Rebuild/delete semantics: full truncation + rebuild is supported and expected. Keep read models isolated from domain tables (no FKs to domain tables) so `TRUNCATE readmodels.*` is always safe. Overwrite/UPSERT only within the readmodel schema.
- Replay safety invariants:
  - Same event stream ⇒ same rows (idempotent writes enforced by unique keys).
  - No cross-schema FKs; intra-readmodel FK use is discouraged and must not block truncation.
  - All tables carry `model_version` (or equivalent) to allow side-by-side versions and safe cutover.
  - Optional `last_replayed_event_id`/`replay_run_id` columns are permitted for observability; they must not change semantics.

### DB Questions Answered
- **Full truncation + rebuild?** Yes—supported by isolating read models in their own schema and avoiding FKs to domain tables. Truncate or delete-all is the supported reset before replay.
- **Indexes for replay write patterns?** Yes—unique index on the idempotency key; supporting indexes on `(user_id, model_version)` or `(entity_id, model_version)` for fetch; avoid over-indexing until hotspots are known.
- **Foreign keys?** Forbidden to domain tables; intra-readmodel FKs strongly discouraged. If absolutely needed, they must tolerate truncate (i.e., same schema, no cascading outwards).
- **Versioning read models?** Include `model_version` (or `read_model_version`) in PK/unique keys and table name if needed. New versions deploy side-by-side; old versions can be dropped after cutover and replay.
