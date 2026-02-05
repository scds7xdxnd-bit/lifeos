# Phase 5b Ops: Deterministic Cross-Domain Insights

## Feature Flags

Phase 5b runtime flags:

- `ENABLE_PHASE5B_INSIGHTS` (default: true)
- `PHASE5B_INSIGHT_TYPES` (comma-separated allowlist; empty means all)

Configure via `.env` or your runtime environment.

## Scheduled Jobs

### Features + Insights Runner (loop)

```bash
docker compose --profile phase5b up -d phase5b-runner
```

Tune via:

- `PHASE5B_RUN_INTERVAL` (seconds)
- `PHASE5B_RUN_SINCE_MINUTES`
- `PHASE5B_RUN_LIMIT`

### One-shot (local)

```bash
DATABASE_URL=postgresql://... \
python scripts/ops/phase5b_insight_runner.py --mode both --since-minutes 60 --limit 500
```

Run features only:

```bash
python scripts/ops/phase5b_insight_runner.py --mode features
```

Run insights only:

```bash
python scripts/ops/phase5b_insight_runner.py --mode insights
```

## Observability

Snapshot counts for insights + UI actions:

```bash
DATABASE_URL=postgresql://... \
python scripts/ops/phase5b_insight_observability.py --since-hours 24
```

Notes:

- Insight counts read from `insight_record.kind`.
- Action counts look for `event_record.event_type == "insights.action"`.
- If action counts are empty, ensure the telemetry ingestion endpoint is configured and persisting events.

## Verification Checklist

- Runner is gated by `ENABLE_PHASE5B_INSIGHTS`.
- Insight counts are non-zero for at least 5 types.
- No Phase 3/4 alert noise (determinism/projection/contract violation alerts remain green).

## Execution Checklist

- Phase 5b runner starts and loops without runtime errors.
- Feature aggregation executes for supported event types and persists to `features_daily`.
- Rule registry executes deterministically for the same input window.
- Insights persist to `insight_record` with confidence band + routing.
- Duplicate suppression blocks re-emitting the same insight window.
- `/api/v1/insights/feed` returns populated data with no contract changes.

## Notes on Fixes Applied

- Outbox dispatch now materializes `event_record` rows before publish to ensure feature aggregation and runner queries have data.
- Manual transaction creation now persists `finance_transaction` and emits `finance.transaction.created` via outbox.
