# Phase 5a Ops: Insight Substrate & Proposal Infrastructure

## Feature Flags

These are the runtime toggles for Phase 5a interpretation behavior:

- `ENABLE_TIMELINE_INGESTION` (default: true)
- `ENABLE_INTERPRETATION_RELATIONSHIP` (default: true)
- `ENABLE_INTERPRETATION_OBLIGATION` (default: false)

They are wired through `docker-compose.yml` via `x-common-env`. Override in `.env` or your runtime environment.

## Background Job: Interpretation Runner

Run proposal generation against recent timeline events. This is idempotent because interpretations are fingerprinted.

One-shot run (local):

```bash
DATABASE_URL=postgresql://... \
python scripts/ops/phase5a_interpretation_runner.py \
  --since-minutes 60 \
  --limit 500
```

Looping background job (local):

```bash
DATABASE_URL=postgresql://... \
python scripts/ops/phase5a_interpretation_runner.py \
  --loop \
  --interval-seconds 60 \
  --since-minutes 60 \
  --limit 500
```

Docker Compose (optional profile):

```bash
docker compose --profile phase5a up -d interpretation-runner
```

Tune with:

- `INTERPRETATION_RUN_INTERVAL` (seconds)
- `INTERPRETATION_RUN_SINCE_MINUTES`
- `INTERPRETATION_RUN_LIMIT`

## Observability: Proposal Counts and Decision Rates

Use the DB-driven report script (no new metrics required):

```bash
DATABASE_URL=postgresql://... \
WINDOW_HOURS=24 \
scripts/ops/phase5a_proposal_observability.sh
```

This reports:

- total proposals + pending/accepted/rejected counts
- accept/reject/correct feedback counts
- accept/reject/correct rates for the window

## Notes

- If `/api/v1/insights/proposals` returns 404, it usually means the backend is running an older build. Restart the backend and confirm the v1 insights blueprint is registered. If the issue persists, send the error to QA.
