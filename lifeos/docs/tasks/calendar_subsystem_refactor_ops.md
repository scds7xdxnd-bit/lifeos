# Calendar Subsystem Refactor — DevOps Runbook

## Purpose
Support the deterministic calendar view/ledger rollout with ops tooling and guardrails without changing pipelines.

## Feature flag
- `CALENDAR_VIEW_API_V2` (default true in `.env.example` / `.env.ci`, added to `docker-compose.yml` common env). Toggle to disable new view endpoints during staged rollout.

## Smoke test (manual/local)
- Script: `scripts/ops/calendar_view_smoketest.sh`
- Requires: `AUTH_TOKEN` (Bearer), optional `BASE_URL` (default `http://localhost:8000`), `TODAY`, `WEEK_START`, `MONTH`, `LEDGER_LIMIT`.
- Runs 200 checks against:
  - `GET /api/v1/calendar/day?date=YYYY-MM-DD`
  - `GET /api/v1/calendar/week?start=YYYY-MM-DD`
  - `GET /api/v1/calendar/month?year=YYYY&month=MM`
  - `GET /api/v1/calendar/ledger?anchor=YYYY-MM-DD&direction=backward&limit=N`
- Example:
  ```bash
  AUTH_TOKEN="$TOKEN" BASE_URL="https://staging.lifeos.example.com" scripts/ops/calendar_view_smoketest.sh
  ```

## Observability (what to watch)
- Latency by view: day/week/month/ledger HTTP latencies and error rates.
- Correctness warnings: overlap window count mismatches, ledger cursor errors, timezone normalization warnings (surface in app logs).
- Usage during cutover: legacy calendar endpoints vs new `/api/v1/calendar/{day,week,month,ledger}` traffic.

## Rollout guidance
- Keep legacy endpoints available during cutover; gate new views with `CALENDAR_VIEW_API_V2`.
- Deploy backend first, then switch frontend consumers; monitor error rates and latency.
- No CI/CD pipeline changes required; use the smoke script post-deploy. Move `calendar_subsystem_refactor.md` to `archive/` when complete.
