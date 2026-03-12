# Phase 7.1 Later-Wave Domain Expert Briefs - Ops Runbook

Owner: DevOps / Platform
Scope: rollout, observability, and rollback safety for later-wave domain expert inquiry briefs (`journal`, `relationships`, `health`)
Last updated: 2026-03-12

## 1) Rollout controls

Primary feature gate:
- `ENABLE_PHASE6_FOCUSED_INQUIRY`

Operational rollout controls:
- `PHASE7_1_LATER_WAVE_ENABLED` (enables later-wave rollout/version checks in smoke script)
- `PHASE7_1_LATER_WAVE_DOMAINS` (default: `journal,relationships,health`)
- `PHASE7_1_EXPECT_PROFILE_VERSION` (default: `1.0.0`)
- `PHASE7_1_EXPECT_STRATEGY_VERSION` (default: `1.0.0`)

Staged rollout approach:
1. Local-dev: validate later-wave metrics/labels and dashboard queries.
2. Staging: validate later-wave alert baseline stays quiet for one full observation window.
3. Canary by domain: verify `journal` first, then `relationships`, then `health` using rollout checks and alert quietness.
4. Production: complete only after all three domains show expected profile/strategy labels with no sustained warning alerts.

## 2) Metrics

Later-wave signals are derived from existing inquiry metric families with domain/profile labels:
- `lifeos_inquiry_generated_by_domain_total{domain,profile,profile_version,strategy,strategy_version,expert_mode}`
- `lifeos_inquiry_generation_latency_seconds_by_domain_bucket{...}`
- `lifeos_inquiry_errors_by_domain_total{stage,error_type,domain,profile,profile_version,strategy,strategy_version,expert_mode}`
- `lifeos_inquiry_empty_brief_by_domain_total{...}`
- `lifeos_inquiry_low_coverage_by_domain_total{...}`
- `lifeos_inquiry_refine_after_low_quality_by_domain_total{...}`
- `lifeos_inquiry_quality_state_by_domain_total{...,state}`
- `lifeos_inquiry_findings_by_domain_total{...}`
- `lifeos_inquiry_findings_with_evidence_by_domain_total{...}`

Derived recording rules (queryable per later-wave domain/profile):
- `lifeos:inquiry_error_rate_by_domain_profile:ratio`
- `lifeos:inquiry_generation_latency_p95_by_domain_profile:seconds`
- `lifeos:inquiry_empty_brief_rate_by_domain_profile:ratio`
- `lifeos:inquiry_low_coverage_rate_by_domain_profile:ratio`
- `lifeos:inquiry_refine_after_low_quality_rate_by_domain_profile:ratio`
- `lifeos:inquiry_quality_state_distribution_by_domain_profile:ratio`
- `lifeos:inquiry_evidence_coverage_ratio_by_domain_profile`

Optional metric (if backend emits it):
- `lifeos_inquiry_forbidden_claim_block_total{domain,...}`

## 3) Dashboard and alert coverage

Prometheus rule file:
- `deploy/monitoring/phase6-inquiry-alerts.yml`

Later-wave alerts:
- `Phase71LaterWaveInquiryErrorRateHigh`
- `Phase71LaterWaveInquiryLatencyHigh`
- `Phase71LaterWaveInquiryEmptyBriefHigh`
- `Phase71LaterWaveInquiryLowCoverageHigh`
- `Phase71LaterWaveRefineAfterLowQualityHigh`
- `Phase71LaterWaveProfileVersionUnexpected`

Grafana dashboard:
- `deploy/monitoring/grafana/provisioning/dashboards/lifeos-inquiry-dashboard.json`
- Later-wave panels are grouped under `Phase 7.1` titles.

## 4) Smoke checks

Script:
- `scripts/ops/phase6_inquiry_rollout_check.sh`

Later-wave usage:
```bash
BASE_URL=http://localhost:8000 \
PROM_URL=http://localhost:9090 \
INQUIRY_FEATURE_ENABLED=true \
EXPECT_MIGRATION_MATCH=true \
PHASE7_1_LATER_WAVE_ENABLED=true \
PHASE7_1_LATER_WAVE_DOMAINS=journal,relationships,health \
PHASE7_1_EXPECT_PROFILE_VERSION=1.0.0 \
PHASE7_1_EXPECT_STRATEGY_VERSION=1.0.0 \
bash scripts/ops/phase6_inquiry_rollout_check.sh
```

Checks include:
- build identity visibility (`/health`, `/api/bootstrap`)
- required inquiry metrics exposed on `/metrics`
- endpoint state by feature gate (`401` when enabled, `404` when disabled)
- migration mismatch state
- recording rule queryability
- no firing phase `6/6.1/7/7.1` inquiry alerts
- later-wave profile/strategy version drift check by observed traffic labels

## 5) Deploy and rollback

Deploy checklist:
1. Confirm DB head is applied (`20260312_phase7_domain_expert_brief_metadata`).
2. Deploy runtime with explicit `BUILD_ID`.
3. Confirm Prometheus loads `phase6-inquiry-alerts.yml`.
4. Confirm Grafana provisions inquiry dashboard with Phase 7.1 panels.
5. Run rollout smoke checks with `PHASE7_1_LATER_WAVE_ENABLED=true`.

Post-deploy verification:
1. Confirm later-wave domain labels appear in `lifeos_inquiry_generated_by_domain_total`.
2. Confirm later-wave alert queries are returning series or empty baseline (not errors).
3. Confirm no sustained phase `7.1` alert firing under baseline traffic.
4. Confirm profile/strategy versions match expected labels.

Rollback checklist:
1. Immediate hard rollback: set `ENABLE_PHASE6_FOCUSED_INQUIRY=false`, redeploy web, verify inquiry endpoints return `404`.
2. Preferred later-wave rollback: redeploy previous runtime image (pre-7.1 strategies), keep migration schema intact.
3. Re-run smoke checks with expected feature-gate state.
4. Confirm inquiry alerts return to baseline.

## 6) Known failure modes

- Mixed runtime versions causing profile/strategy version drift.
- Later-wave latency degradation hidden when only global p95 is watched.
- Later-wave domain-specific low-coverage spikes from sparse evidence windows.
- Refine loops rising for one later-wave domain while others remain healthy.
- Optional forbidden-claim counter not emitted by backend (treat as non-blocking observability gap until metric is introduced).
