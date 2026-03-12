# Phase 5c Backend Ops: Feature Store & Personalization Scaffolding

## Backend Implementation Notes (module-level)

- Feature store model and service:
  - `lifeos/core/feature_store/models.py` (features_v1 table mapping)
  - `lifeos/core/feature_store/service.py` (write/read helpers with invariants)
- Feature store migration:
  - `lifeos/migrations/versions/20260205_phase5c_feature_store_v1.py`
- Feature computation runners:
  - `scripts/ops/phase5c_feature_runner.py` (daily/window compute + verify)
- Insight feedback ingestion:
  - `lifeos/core/insights/api_v1.py` (`POST /api/v1/insights/feedback`)
  - `lifeos/core/insights/schemas.py` (feedback schema + action/reason enums)
- Personalization hook (no-op by default):
  - `lifeos/core/insights/personalization.py`
  - `lifeos/core/insights/services.py` (feed uses rank_insights)
  - `lifeos/core/insights/api_v1.py` (cache key includes personalization flag)
- Config:
  - `lifeos/config.py` (`PERSONALIZATION_ENABLED=false` by default)

## Proof Artifacts

### No-op personalization (default)

```bash
python scripts/ops/phase5c_personalization_noop_check.py --user-id <id>
```

Expected: `phase5c: personalization no-op verified (PASS)`

### Feature rebuild determinism

```bash
python scripts/ops/phase5c_feature_runner.py --window-days 30 --start-date 2026-01-01 --end-date 2026-01-30 --verify
```

Expected: `phase5c: verification mismatches=0`

## Backend Phase 5c Handoff (QA + DevOps)

- Feature store table: `features_v1`
- Feedback endpoint: `POST /api/v1/insights/feedback`
  - Actions: viewed, dismissed, saved, shared, feedback_positive, feedback_negative, reported_issue
  - Legacy actions accepted: dismiss, snooze, act (mapped to canonical events)
- Event audit: feedback events stored in `event_record` with event_type `insight_*`
- Idempotency: enforced via `idempotency_key` + feedback fingerprint
- Personalization: `PERSONALIZATION_ENABLED=false` default (no feed order change)
- Runner: `scripts/ops/phase5c_feature_runner.py` (daily/window compute, verify mode)
