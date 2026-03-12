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

## Stability Soak (Phase 3b confirmation gate)
Objective: verify contracts, projections, and observability stay quiet and deterministic under normal use.

Duration:
- 3-7 days
- Must include at least one cold deploy, one restart, and one replay/backfill run (if applicable)

Operating assumptions:
- Normal developer/admin usage
- No synthetic load tests
- No schema changes
- No new features

Good outcome definition:
- Alerts do not flap
- Metrics present at all times
- Zero unexplained determinism failures
- Zero contract violations
- No projection correctness errors
- Insight latency stable (no upward drift)

Metrics to observe:
- lifeos_projection_correctness_total / lifeos_projection_correctness_errors_total
  - Errors must be zero or extremely rare; rate <= 0.1%
- lifeos_replay_determinism_failures_total
  - Must remain zero except during intentional replay testing
- lifeos_insight_latency_seconds_bucket (p50/p95/p99)
  - p95 stable; no unexplained long-tail spikes
- lifeos_contract_violations_total
  - Must remain zero
- Phase3bSLOMetricsMissing
  - Must never fire; /metrics must always expose all Phase 3b metrics

Manual checks (once per soak):
- Restart check: restart app; confirm /metrics exposes all metrics immediately and no alerts fire.
- Replay check: run a controlled replay; determinism failures stay zero; projection correctness errors stay zero.
- Frontend smoke: load insight feed, review queue, calendar view, finance read surfaces; no schema-mismatch errors or undefined fields.

Soak log (minimal):
- Day 1: deploy ok; metrics present; alerts green
- Day 3: restart performed; no determinism failures
- Day 6: replay test; counters behaved as expected

Exit criteria:
- Zero unexplained determinism failures
- Zero contract violations
- Zero projection correctness errors
- Metrics-missing alert never fired
- Insight latency stable
- Alerts trusted (no unexplained flaps)

## Metrics endpoint
- `/metrics` is exposed by the web app and includes Phase 3b counters/histograms.
- Prometheus scrapes `lifeos-web` at `/metrics` (configured in `deploy/monitoring/prometheus.yml`).

## Rollout guidance
- No pipeline changes required.
- Run in staging before promoting to production.
- Coordinate with QA for the Phase 3b contract error surfacing checks.
