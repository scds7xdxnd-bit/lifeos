# Phase 3b.1 - Stability Patch Verification (DevOps)

**Audience:** DevOps, QA, Architecture
**Scope:** Observability validation only. No app behavior changes.

## Goals
- Confirm Phase 3b metrics still emit after the stability fixes.
- Confirm Phase 3b alert rules are loaded and not firing.

## Preconditions
- LifeOS web app running (host or container).
- Prometheus running and able to scrape the LifeOS `/metrics` endpoint.
- Phase 3b alert rules loaded (`deploy/monitoring/phase3b-alerts.yml`).

## Quick checks

### 1) Verify /metrics contains Phase 3b SLO metrics
Run:
```bash
BASE_URL=http://localhost:5001 \
PROM_URL=http://localhost:9090 \
./scripts/ops/phase3b_1_stability_soak_check.sh
```

Expected output:
- `OK: Phase 3b metrics present at ...`
- `OK: No Phase 3b alerts firing`

If Prometheus is not reachable, the script prints a warning and exits successfully
after checking the metrics endpoint.

### 2) Prometheus UI confirmation
- Go to `http://localhost:9090/targets` and confirm `job="lifeos"` is **UP**.
- Go to `Status -> Rules` and confirm group `lifeos_phase3b_contracts` is loaded.

## What to watch during the mini soak
- `Phase3bSLOMetricsMissing` must never fire.
- `Phase3bProjectionErrors` must remain 0.
- `Phase3bReplayDeterminismFailure` must remain 0.
- `Phase3bContractViolation` must remain 0.
- `Phase3bInsightLatencyHigh` should remain green.

## Troubleshooting
- If metrics are missing: verify `/metrics` is reachable from Prometheus and that
  the LifeOS app is running with the Phase 3b metrics instrumentation enabled.
- If Prometheus cannot reach LifeOS on host: use `host.docker.internal:5001` in
  `deploy/monitoring/prometheus.yml` (Solution A) and restart Prometheus.
