# Phase 6.1 Focused Inquiry Quality Hardening - Ops Runbook

Owner: DevOps / Platform
Scope: quality-SLO observability, rollout checks, staged release controls
Last updated: 2026-03-12

## 1) Scope

This runbook covers operational support for Phase 6.1 inquiry quality hardening only.
It does not change inquiry product semantics.

## 2) Metrics (quality hardening)

Runtime metrics:
- `lifeos_inquiry_low_coverage_total`
- `lifeos_inquiry_empty_brief_total`
- `lifeos_inquiry_refine_after_low_quality_total`
- `lifeos_inquiry_quality_state_total{state}`
- `lifeos_inquiry_generation_latency_seconds`

Recording rules:
- `lifeos:inquiry_low_coverage_rate:ratio`
- `lifeos:inquiry_empty_brief_rate:ratio`
- `lifeos:inquiry_refine_after_low_quality_rate:ratio`
- `lifeos:inquiry_quality_state_distribution:ratio`
- `lifeos:inquiry_error_rate:ratio`

## 3) Alerts

Prometheus rule file:
- `deploy/monitoring/phase6-inquiry-alerts.yml`

Phase 6.1 quality alerts:
- `Phase61InquiryLowCoverageHigh`
- `Phase61InquiryRefineAfterLowQualityHigh`
- `Phase61InquiryEmptyStateDominant`

Baseline quality guardrails retained:
- `Phase6InquiryGenerationFailures`
- `Phase6InquiryLatencyHigh`
- `Phase6InquiryEmptyBriefAnomaly`
- `Phase6InquiryEndpoint5xx`
- `Phase6InquiryMigrationMismatch`

## 4) Dashboard

Grafana dashboard:
- `deploy/monitoring/grafana/provisioning/dashboards/lifeos-inquiry-dashboard.json`

Quality panels:
- low coverage rate
- refine-after-low-quality rate
- quality state distribution
- empty brief rate
- generation latency

## 5) Staged rollout plan

1. Local-dev
- Ensure `ENABLE_PHASE6_FOCUSED_INQUIRY=true`.
- Validate quality metrics on `/metrics`.

2. Staging
- Enable flag for staging deployment.
- Verify recording rules and dashboard population.
- Ensure no sustained phase 6/6.1 alert firing.

3. Production canary
- Enable only on canary environment.
- Watch quality rates and latency for one full observation window.

4. Full production
- Expand rollout only when canary remains alert-quiet.

## 6) Rollback plan

Rollback trigger examples:
- sustained high low-coverage ratio
- sustained refine-after-low-quality ratio spike
- sustained latency regression or inquiry failures

Rollback steps:
1. Set `ENABLE_PHASE6_FOCUSED_INQUIRY=false`.
2. Redeploy web.
3. Run rollout check script.
4. Confirm endpoint gating and alert recovery.

## 7) Verification script

Use:
- `scripts/ops/phase6_inquiry_rollout_check.sh`

The script verifies:
- build identity visibility
- required inquiry and quality metrics
- inquiry endpoint behavior by flag state
- migration mismatch status
- recording rule queryability
- phase 6/6.1 alert state

## 8) Known blockers

- If `lifeos/docs/tasks/phase_6_1_focused_inquiry_quality_hardening.md` is absent in older clones, sync latest docs before sign-off.
- Historical inquiry versions generated pre-6.1 may not include `quality_metadata` fields.

Related:
- `lifeos/docs/ops/phase_7_domain_expert_briefs_ops.md` for domain expert quality rollout controls.
