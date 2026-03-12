# Phase 6/6.1 Focused Inquiry Ops Runbook

Owner: DevOps / Platform
Scope: rollout, observability, runtime verification for Focused Inquiry v1
Last updated: 2026-03-12

## SECTION 1 — Feature rollout

Feature flags:
- `ENABLE_PHASE6_FOCUSED_INQUIRY`
- `PHASE6_INQUIRY_MIGRATION_HEAD` (expected DB revision marker for runtime mismatch metric)

Default state:
- `BaseConfig`: `ENABLE_PHASE6_FOCUSED_INQUIRY=false`
- `DevelopmentConfig`: `ENABLE_PHASE6_FOCUSED_INQUIRY=true`
- `TestingConfig`: `ENABLE_PHASE6_FOCUSED_INQUIRY=true`
- `ProductionConfig`: `ENABLE_PHASE6_FOCUSED_INQUIRY=false`

Staged rollout approach:
1. Local-dev: enabled for endpoint/UI smoke and metrics verification.
2. Staging: enable via env (`ENABLE_PHASE6_FOCUSED_INQUIRY=true`) after migration and alert baselines are green.
3. Production canary window: enable on selected environment only after staging checks pass.
4. Full production: enable globally only when no sustained Phase 6 alerts are firing.

Rollback trigger:
- sustained `Phase6InquiryGenerationFailures`
- sustained `Phase6InquiryLatencyHigh`
- sustained `Phase6InquiryEndpoint5xx`
- `Phase6InquiryMigrationMismatch` firing

Rollback method:
1. Set `ENABLE_PHASE6_FOCUSED_INQUIRY=false`.
2. Redeploy web containers.
3. Verify `/api/v1/inquiries` returns `404`.
4. Confirm Phase 3b/3c metrics remain healthy.

## SECTION 2 — Metrics

Implemented metrics:
- `lifeos_inquiry_created_total`
- `lifeos_inquiry_generated_total`
- `lifeos_inquiry_viewed_total`
- `lifeos_inquiry_refined_total`
- `lifeos_inquiry_generation_latency_seconds` (histogram)
- `lifeos_inquiry_errors_total{stage,error_type}`
- `lifeos_inquiry_empty_brief_total`
- `lifeos_inquiry_low_coverage_total`
- `lifeos_inquiry_refine_after_low_quality_total`
- `lifeos_inquiry_quality_state_total{state}`
- `lifeos_inquiry_findings_total`
- `lifeos_inquiry_findings_with_evidence_total`
- `lifeos_inquiry_error_rate` (runtime gauge)
- `lifeos_inquiry_empty_brief_rate` (runtime gauge)
- `lifeos_inquiry_evidence_coverage_ratio` (runtime gauge)
- `lifeos_inquiry_low_coverage_rate` (runtime gauge)
- `lifeos_inquiry_refine_after_low_quality_rate` (runtime gauge)
- `lifeos_phase6_inquiry_migration_mismatch{expected_head}`

Prometheus recording rules (Phase 6):
- `lifeos:inquiry_error_rate:ratio`
- `lifeos:inquiry_empty_brief_rate:ratio`
- `lifeos:inquiry_evidence_coverage_ratio`
- `lifeos:inquiry_low_coverage_rate:ratio`
- `lifeos:inquiry_refine_after_low_quality_rate:ratio`
- `lifeos:inquiry_quality_state_distribution:ratio`

## SECTION 3 — Monitoring / alerts

Prometheus rule file:
- `deploy/monitoring/phase6-inquiry-alerts.yml`

Alert coverage:
- `Phase6InquiryMetricsMissing`: required metrics absent.
- `Phase6InquiryGenerationFailures`: internal inquiry generation errors detected.
- `Phase6InquiryLatencyHigh`: p95 generation latency > 2s for 10m.
- `Phase6InquiryEmptyBriefAnomaly`: empty brief ratio > 0.6 for 15m.
- `Phase6InquiryEndpoint5xx`: sustained 5xx on `/api/v1/inquiries*` routes.
- `Phase6InquiryMigrationMismatch`: runtime migration head mismatch.
- `Phase61InquiryLowCoverageHigh`: low coverage ratio > 0.4 for 15m.
- `Phase61InquiryRefineAfterLowQualityHigh`: refine-after-low-quality ratio > 0.5 for 15m.
- `Phase61InquiryEmptyStateDominant`: quality state `empty` ratio > 0.3 for 15m.

Dashboard coverage:
- `deploy/monitoring/grafana/provisioning/dashboards/lifeos-inquiry-dashboard.json`
- Panels include lifecycle counts, generation latency, error rate, empty brief rate, evidence coverage ratio, 5xx endpoint signal, migration mismatch state.

## SECTION 4 — Smoke checks

Script:
- `scripts/ops/phase6_inquiry_rollout_check.sh`

Checks covered:
- build identity visible on `/health` and `/api/bootstrap`
- required inquiry metrics exposed on `/metrics`
- inquiry endpoint availability according to feature flag state
- migration-applied state via `lifeos_phase6_inquiry_migration_mismatch`
- Phase 6/6.1 alert state from Prometheus API (if reachable)

Usage:
```bash
BASE_URL=http://localhost:8000 \
PROM_URL=http://localhost:9090 \
INQUIRY_FEATURE_ENABLED=true \
EXPECT_MIGRATION_MATCH=true \
bash scripts/ops/phase6_inquiry_rollout_check.sh
```

## SECTION 5 — Runbook

Deploy checklist:
1. Confirm migration chain head is `20260312_phase7_domain_expert_brief_metadata` (or the explicitly configured `PHASE6_INQUIRY_MIGRATION_HEAD`).
2. Deploy web image with `BUILD_ID`/`LIFEOS_BUILD_ID` set.
3. Set feature flag explicitly for target environment.
4. Ensure Prometheus loads `phase6-inquiry-alerts.yml`.
5. Ensure Grafana provisions inquiry dashboard JSON.

Post-deploy verification:
1. Run `scripts/ops/phase6_inquiry_rollout_check.sh`.
2. Verify `/metrics` includes all inquiry metrics.
3. Verify no Phase 6/6.1 alerts firing.
4. Verify `lifeos_phase6_inquiry_migration_mismatch == 0`.

Rollback checklist:
1. Disable flag (`ENABLE_PHASE6_FOCUSED_INQUIRY=false`).
2. Redeploy web.
3. Re-run smoke check with `INQUIRY_FEATURE_ENABLED=false`.
4. Confirm endpoint is gated and baseline platform alerts remain green.

Known failure modes:
- Missing migration scripts or DB ahead/behind image (`Phase6InquiryMigrationMismatch`).
- Elevated generation failures (`Phase6InquiryGenerationFailures`).
- Latency regressions under load (`Phase6InquiryLatencyHigh`).
- Data sparsity causing excessive empty briefs (`Phase6InquiryEmptyBriefAnomaly`).
- Quality degradation spikes (`Phase61InquiryLowCoverageHigh`).
- Excessive refinement loops after weak quality (`Phase61InquiryRefineAfterLowQualityHigh`).
- Endpoint instability (`Phase6InquiryEndpoint5xx`).

## SECTION 6 — Verification output

Operational confirmation criteria:
- Focused Inquiry endpoint is feature-gated and reversible without schema rollback.
- Build identity remains visible (`/health`, `/api/bootstrap`).
- Required inquiry metrics are emitted from runtime.
- Phase 6/6.1 alerts and dashboard cover failures, latency, quality rates/distribution, and migration mismatch.
- Rollout smoke checks exist and are executable from ops shell.

Status statement template:
- `Phase 6 Focused Inquiry v1 is deployable and observable under current platform constraints.`

Related:
- `lifeos/docs/ops/phase_7_domain_expert_briefs_ops.md` (first-wave domain expert rollout)
