# Phase 3b Interface Contract Hardening - DevOps Runbook

## Purpose
Provide operational checks for Phase 3b contract stability and read-only enforcement without changing CI/CD pipelines.

## Smoke tests (contracts + read-only guard)
- Script: `scripts/ops/phase3b_contract_smoketest.sh`
- Runs contract hash tests, read-only guard tests, and frontend contract error surfacing checks.

```bash
scripts/ops/phase3b_contract_smoketest.sh
```

## Monitoring focus
- Contract breakage: run the smoke test after deploys that touch API schema or projection code.
- Read-only violations: monitor app logs for read-only guard failures and unexpected rollbacks.
- Interface stability: treat any contract mismatch error from clients as a deployment incident.

## SLOs and alert thresholds (Phase 3b)
Explicit thresholds and metrics:
- Insight latency p95 <= 1.5s over 5m (metric: `lifeos_insight_latency_seconds_bucket`, alert: InsightLatencyHigh).
- Projection correctness error rate <= 1% over 5m (metrics: `lifeos_projection_correctness_errors_total`,
  `lifeos_projection_correctness_total`, alert: ProjectionCorrectnessErrors).
- Replay determinism failures: 0 over 30m (metric: `lifeos_replay_determinism_failures_total`, alert: ReplayDeterminismFailures).
- Contract violations: 0 over 10m (metric: `lifeos_contract_violations_total`, alert: ContractViolations).
- Metrics presence: all Phase 3b SLO metrics must be emitted (alert: Phase3bSLOMetricsMissing).

## Prometheus rules
Implemented in `deploy/monitoring/prometheus.rules.yml`:
- Insight latency p95: histogram quantile over `lifeos_insight_latency_seconds_bucket`.
- Projection correctness error rate: `rate(lifeos_projection_correctness_errors_total[5m]) /
  clamp_min(rate(lifeos_projection_correctness_total[5m]), 0.001)`.
- Replay determinism failures: `increase(lifeos_replay_determinism_failures_total[30m])`.
- Contract violations: `increase(lifeos_contract_violations_total[10m])`.
- Metric presence checks for all above counters/histograms.

## Metrics endpoint
- `/metrics` is exposed by the web app and includes Phase 3b counters/histograms.
- Prometheus scrapes `lifeos-web` at `/metrics` (configured in `deploy/monitoring/prometheus.yml`).

## Rollout guidance
- No pipeline changes required.
- Run in staging before promoting to production.
- Coordinate with QA for the Phase 3b contract error surfacing checks.
