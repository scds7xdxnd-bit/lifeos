# Phase 10 Insight Humanization Layer - Ops Runbook

Owner: DevOps / Platform
Scope: rollout safety, observability, and rollback for humanized-by-default inquiry rendering
Last updated: 2026-03-14

## 1) Rollout controls

Primary inquiry gates:
- `ENABLE_PHASE6_FOCUSED_INQUIRY`
- `ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES`
- `ENABLE_PHASE9_TIMELINE_INTELLIGENCE`
- `ENABLE_PHASE10_INQUIRY_HUMANIZATION`

Phase 10 rollout check controls:
- `PHASE10_HUMANIZATION_ENABLED`
- `PHASE10_EXPECT_HUMANIZATION_VERSION` (default: `phase10_humanization_v1`)
- `PHASE10_CANARY_PROFILE` (optional)
- `PHASE10_CANARY_MAX_FALLBACK_RATE` (default: `0.20`)
- `PHASE10_CANARY_MAX_FAILURE_RATE` (default: `0.08`)
- `PHASE10_CANARY_MAX_LATENCY_P95` (default: `0.25`)
- `PHASE10_CANARY_MAX_EQUIVALENCE_VIOLATION_COUNT` (default: `0`)
- `PHASE10_CANARY_MAX_REFINE_AFTER_VIEW_RATE` (default: `0.70`)

## 2) Metrics and recording rules

Raw Phase 10 metrics:
- `lifeos_inquiry_humanization_render_total`
- `lifeos_inquiry_humanization_render_by_domain_total`
- `lifeos_inquiry_humanization_render_latency_seconds_bucket`
- `lifeos_inquiry_humanization_render_latency_seconds_by_domain_bucket`
- `lifeos_inquiry_humanization_failure_total`
- `lifeos_inquiry_humanization_failure_by_domain_total`
- `lifeos_inquiry_humanization_fallback_total{reason}`
- `lifeos_inquiry_humanization_fallback_by_domain_total{reason,...}`
- `lifeos_inquiry_humanization_equivalence_violation_total`
- `lifeos_inquiry_humanization_equivalence_violation_by_domain_total`
- `lifeos_inquiry_humanized_output_total`
- `lifeos_inquiry_humanized_output_by_domain_total`
- `lifeos_inquiry_humanized_view_total`
- `lifeos_inquiry_humanized_view_by_domain_total`
- `lifeos_inquiry_technical_brief_expanded_total`
- `lifeos_inquiry_technical_brief_expanded_by_domain_total`
- `lifeos_inquiry_refine_after_humanized_view_total`
- `lifeos_inquiry_refine_after_humanized_view_by_domain_total`
- `lifeos_inquiry_humanization_version_total{humanization_version,canonical_version,...}`

Derived recordings:
- `lifeos:inquiry_humanization_render_latency_p95:seconds`
- `lifeos:inquiry_humanization_render_latency_p95_by_domain_profile:seconds`
- `lifeos:inquiry_humanization_failure_rate:ratio`
- `lifeos:inquiry_humanization_failure_rate_by_domain_profile:ratio`
- `lifeos:inquiry_humanization_fallback_rate:ratio`
- `lifeos:inquiry_humanization_fallback_rate_by_domain_profile:ratio`
- `lifeos:inquiry_humanization_equivalence_violation_count`
- `lifeos:inquiry_humanization_equivalence_violation_count_by_domain_profile`
- `lifeos:inquiry_humanized_output_presence_rate:ratio`
- `lifeos:inquiry_humanized_output_presence_rate_by_domain_profile:ratio`
- `lifeos:inquiry_technical_brief_expansion_rate:ratio`
- `lifeos:inquiry_technical_brief_expansion_rate_by_domain_profile:ratio`
- `lifeos:inquiry_refine_after_humanized_view_rate:ratio`
- `lifeos:inquiry_refine_after_humanized_view_rate_by_domain_profile:ratio`

## 3) Dashboard and alerts

Dashboard:
- `deploy/monitoring/grafana/provisioning/dashboards/lifeos-inquiry-dashboard.json`

Phase 10 alerts:
- `Phase10HumanizationRenderLatencyHigh`
- `Phase10HumanizationFailureRateHigh`
- `Phase10HumanizationFallbackRateHigh`
- `Phase10HumanizationEquivalenceViolationDetected`
- `Phase10HumanizedOutputPresenceLow`
- `Phase10HumanizationVersionUnexpected`

Prometheus rule file:
- `deploy/monitoring/phase6-inquiry-alerts.yml`

## 4) Staged rollout policy

1. Staging validation
- Enable `ENABLE_PHASE10_INQUIRY_HUMANIZATION=true` in staging.
- Keep `EXPECT_MIGRATION_MATCH=true` (strict).
- Run `scripts/ops/phase10_humanization_rollout_check.sh`.
- Confirm no phase `10` alerts fire across one full observation window.

2. Canary on selected inquiry profiles
- Set `PHASE10_CANARY_PROFILE` to one active profile.
- Validate canary thresholds for fallback/failure/latency/equivalence/refine-after-view.
- Confirm `humanization_version == PHASE10_EXPECT_HUMANIZATION_VERSION`.

3. Production staged enablement
- Gradually expand profile traffic.
- Track baseline vs canary snapshots with `phase10_humanization_snapshot.sh`.
- Advance only if phase `10` alerts are quiet and canary thresholds remain satisfied.

## 5) Rollback

Primary rollback:
1. Set `ENABLE_PHASE10_INQUIRY_HUMANIZATION=false`.
2. Redeploy web.
3. Re-run rollout checks with `PHASE10_HUMANIZATION_ENABLED=false`.

Safety invariants:
- Inquiry generation remains online (`ENABLE_PHASE6_FOCUSED_INQUIRY=true`).
- Canonical brief path remains available and authoritative.
- No DB rollback is required for Phase 10.

Rollback triggers:
- sustained `Phase10HumanizationFailureRateHigh`
- sustained `Phase10HumanizationFallbackRateHigh`
- any `Phase10HumanizationEquivalenceViolationDetected`
- sustained `Phase10HumanizedOutputPresenceLow`

## 6) Verification commands

Strict rollout check:

```bash
BASE_URL=http://localhost:8000 \
PROM_URL=http://localhost:9090 \
INQUIRY_FEATURE_ENABLED=true \
EXPECT_MIGRATION_MATCH=true \
PHASE8_CROSS_DOMAIN_ENABLED=true \
PHASE8_1_PRODUCTIZATION_ENABLED=true \
PHASE9_TIMELINE_ENABLED=true \
PHASE10_HUMANIZATION_ENABLED=true \
PHASE10_EXPECT_HUMANIZATION_VERSION=phase10_humanization_v1 \
PHASE10_CANARY_PROFILE=finance_expert_brief \
PHASE10_CANARY_MAX_FALLBACK_RATE=0.20 \
PHASE10_CANARY_MAX_FAILURE_RATE=0.08 \
PHASE10_CANARY_MAX_LATENCY_P95=0.25 \
PHASE10_CANARY_MAX_EQUIVALENCE_VIOLATION_COUNT=0 \
PHASE10_CANARY_MAX_REFINE_AFTER_VIEW_RATE=0.70 \
bash scripts/ops/phase10_humanization_rollout_check.sh
```

Snapshot capture:

```bash
PROM_URL=http://localhost:9090 SNAPSHOT_LABEL=baseline bash scripts/ops/phase10_humanization_snapshot.sh
PROM_URL=http://localhost:9090 SNAPSHOT_LABEL=canary bash scripts/ops/phase10_humanization_snapshot.sh
```

## 7) Known rollout blockers

- Runtime flag enabled but no humanization render traffic present yet.
- `humanization_version` label drift from expected value.
- High fallback/failure rates with active render traffic.
- Any equivalence violation counter increase.
- Humanized output presence below threshold under sustained traffic.
