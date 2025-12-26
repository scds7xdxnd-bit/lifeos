# Phase 3c-1 - Read Throughput Scaling (DevOps)

**Audience:** DevOps, QA, Architecture
**Scope:** Observability and load characterization only.

## Goals
- Confirm read-path latency and cache metrics are visible.
- Provide a safe synthetic load harness for read surfaces.

## Metrics and dashboards
- `/metrics` must expose:
  - `lifeos_read_cache_hits_total`
  - `lifeos_read_cache_misses_total`
- Grafana dashboard includes:
  - Read API latency (GET p95/p99)
  - Read cache hit rate and hit/miss rates

## Load harness (read-only)
Script: `scripts/ops/phase3c1_read_load_harness.sh`

Environment variables:
- `AUTH_TOKEN` (required): Bearer token for authenticated reads.
- `BASE_URL` (default: `http://localhost:5001`)
- `ITERATIONS` (default: `10`)
- `CONCURRENCY` (default: `4`)
- `SLEEP_SECONDS` (default: `0.2`)

Run:
```bash
AUTH_TOKEN="..." \
BASE_URL="http://localhost:5001" \
ITERATIONS=20 \
CONCURRENCY=6 \
SLEEP_SECONDS=0.2 \
./scripts/ops/phase3c1_read_load_harness.sh
```

Expected outcome:
- No write operations are performed.
- Read cache hit/miss metrics increment.
- Prometheus targets remain UP and alerts stay green.

## Prometheus checks
- `http://localhost:9090/targets` -> job `lifeos` is UP.
- `up{job="lifeos"}` returns 1.
- `lifeos_read_cache_hits_total` and `lifeos_read_cache_misses_total` increase during load.

## Cache invalidation audit (Phase 3c-1)
Calendar reads (scope: `calendar.views`)
- [x] Event create/update/delete -> cache bump in `calendar_service`.
- [x] Sync/import updates/deletes -> cache bump in Google/Apple sync services.
- [x] Interpreter classification -> cache bump after interpretation commit.
- [x] Review status changes -> cache bump after interpretation status update.
- [x] Interpretation cleanup -> cache bump for affected users.

Finance reads (scope: `finance.reads`)
- [x] Journal writes -> cache bump in `post_journal_entry`.
- [x] Import flows -> covered via journal writes.
- [x] Schedule create/update/delete -> cache bump in `schedule_service`.
- [x] Receivable create/update/delete/entry -> cache bump in `receivable_service`.
- [x] Account/category writes -> cache bump in `accounting_service`.

Insights reads (scope: `insights.reads`)
- [x] Insight persistence -> cache bump in `persist_insights`.
- [ ] Review status changes -> N/A (no mutable review endpoint in Phase 3c-1).

Verification
- [ ] Re-run `scripts/ops/phase3c1_read_load_harness.sh` after deploying cache invalidation patches (DevOps).

## Troubleshooting
- If metrics are missing, verify `/metrics` is reachable from Prometheus.
- If Prometheus is in Docker and LifeOS is on host, use `host.docker.internal:5001`
  in `deploy/monitoring/prometheus.yml` and restart Prometheus.
