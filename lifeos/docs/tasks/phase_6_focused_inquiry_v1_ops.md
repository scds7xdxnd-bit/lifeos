# Phase 6 Focused Inquiry v1 - DevOps Operational Support

Date: 2026-03-12
Owner: DevOps / Platform

## SECTION 1 — Feature rollout

- Flag: `ENABLE_PHASE6_FOCUSED_INQUIRY`
- Expected migration head marker: `PHASE6_INQUIRY_MIGRATION_HEAD=20260312_phase6_inquiry_query_indexes`
- Defaults:
  - local-dev/development/testing: enabled
  - staging/production: disabled by default, explicit enable required
- Rollout: local-dev -> staging -> production canary -> production global
- Rollback: disable flag + redeploy web, then verify endpoint gating and metrics baseline

## SECTION 2 — Metrics

Added/verified metrics:
- `lifeos_inquiry_created_total`
- `lifeos_inquiry_generated_total`
- `lifeos_inquiry_viewed_total`
- `lifeos_inquiry_refined_total`
- `lifeos_inquiry_generation_latency_seconds`
- `lifeos_inquiry_errors_total`
- `lifeos_inquiry_error_rate`
- `lifeos_inquiry_empty_brief_total`
- `lifeos_inquiry_empty_brief_rate`
- `lifeos_inquiry_evidence_coverage_ratio`
- `lifeos_phase6_inquiry_migration_mismatch`

## SECTION 3 — Monitoring / alerts

Prometheus:
- Added rule file `deploy/monitoring/phase6-inquiry-alerts.yml`
- Wired in:
  - `deploy/monitoring/prometheus.yml`
  - `docker-compose.monitoring.yml`

Alert coverage:
- generation failures
- latency spikes
- empty-brief anomalies
- endpoint 5xx availability signal
- migration mismatch detection

Grafana:
- Added dashboard `deploy/monitoring/grafana/provisioning/dashboards/lifeos-inquiry-dashboard.json`

## SECTION 4 — Smoke checks

Added script:
- `scripts/ops/phase6_inquiry_rollout_check.sh`

Checks:
- build identity visibility (`/health`, `/api/bootstrap`)
- inquiry metrics presence (`/metrics`)
- inquiry endpoint behavior by feature flag state
- migration mismatch state
- active Phase 6 alert state in Prometheus

## SECTION 5 — Runbook

See:
- `lifeos/docs/ops/phase_6_focused_inquiry_v1_ops.md`

## SECTION 6 — Verification output

Expected operational confirmation statement:
- `Phase 6 Focused Inquiry v1 is deployable and observable under current platform constraints.`
