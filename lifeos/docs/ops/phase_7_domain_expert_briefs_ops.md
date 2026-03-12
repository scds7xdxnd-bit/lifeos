# Phase 7 Domain Expert Briefs - Ops Runbook (First-Wave)

Owner: DevOps / Platform
Scope: rollout, observability, and rollback safety for first-wave domain expert inquiry briefs (`finance`, `habits`, `projects`, `skills`)
Last updated: 2026-03-12

For later-wave rollout (`journal`, `relationships`, `health`), use:
- `lifeos/docs/ops/phase_7_1_later_wave_domain_expert_briefs_ops.md`

## 1) Rollout controls

Primary feature gate:
- `ENABLE_PHASE6_FOCUSED_INQUIRY`

Operational rollout controls:
- `PHASE7_DOMAIN_EXPERT_ENABLED` (ops check mode switch for Phase 7 checks)
- `PHASE7_FIRST_WAVE_DOMAINS` (default: `finance,habits,projects,skills`)
- `PHASE7_EXPECT_PROFILE_VERSION` (default: `1.0.0`)
- `PHASE7_EXPECT_STRATEGY_VERSION` (default: `1.0.0`)

Rollout stages:
1. Local-dev: verify Phase 7 metrics and labels are emitted.
2. Staging: verify domain/profile/version recording rules and alert quiet baseline.
3. Canary: verify first-wave domain labels and version drift checks under real traffic.
4. Production: complete only after canary remains alert-quiet across one observation window.

## 2) Metrics

Global (retained):
- `lifeos_inquiry_created_total`
- `lifeos_inquiry_generated_total`
- `lifeos_inquiry_viewed_total`
- `lifeos_inquiry_refined_total`
- `lifeos_inquiry_generation_latency_seconds`
- `lifeos_inquiry_errors_total{stage,error_type}`
- `lifeos_inquiry_empty_brief_total`
- `lifeos_inquiry_low_coverage_total`
- `lifeos_inquiry_refine_after_low_quality_total`
- `lifeos_inquiry_quality_state_total{state}`

Phase 7 per-domain/profile metrics:
- `lifeos_inquiry_generated_by_domain_total{domain,profile,profile_version,strategy,strategy_version,expert_mode}`
- `lifeos_inquiry_refined_by_domain_total{domain,profile,profile_version,strategy,strategy_version,expert_mode}`
- `lifeos_inquiry_generation_latency_seconds_by_domain{...}`
- `lifeos_inquiry_errors_by_domain_total{stage,error_type,domain,profile,profile_version,strategy,strategy_version,expert_mode}`
- `lifeos_inquiry_empty_brief_by_domain_total{...}`
- `lifeos_inquiry_findings_by_domain_total{...}`
- `lifeos_inquiry_findings_with_evidence_by_domain_total{...}`
- `lifeos_inquiry_low_coverage_by_domain_total{...}`
- `lifeos_inquiry_refine_after_low_quality_by_domain_total{...}`
- `lifeos_inquiry_quality_state_by_domain_total{...,state}`

## 3) Dashboard and alert coverage

Prometheus rules file:
- `deploy/monitoring/phase6-inquiry-alerts.yml` (includes Phase 6, 6.1, and 7 rules)

Phase 7 recording rules:
- `lifeos:inquiry_error_rate_by_domain_profile:ratio`
- `lifeos:inquiry_empty_brief_rate_by_domain_profile:ratio`
- `lifeos:inquiry_low_coverage_rate_by_domain_profile:ratio`
- `lifeos:inquiry_refine_after_low_quality_rate_by_domain_profile:ratio`
- `lifeos:inquiry_evidence_coverage_ratio_by_domain_profile`
- `lifeos:inquiry_generation_latency_p95_by_domain_profile:seconds`
- `lifeos:inquiry_quality_state_distribution_by_domain_profile:ratio`

Phase 7 alerts:
- `Phase7DomainInquiryErrorRateHigh`
- `Phase7DomainInquiryLatencyHigh`
- `Phase7DomainInquiryEmptyBriefHigh`
- `Phase7DomainInquiryLowCoverageHigh`
- `Phase7DomainRefineAfterLowQualityHigh`
- `Phase7DomainProfileVersionUnexpected`

Grafana dashboard:
- `deploy/monitoring/grafana/provisioning/dashboards/lifeos-inquiry-dashboard.json`
- Includes global and Phase 7 domain/profile panels.

## 4) Smoke checks

Script:
- `scripts/ops/phase6_inquiry_rollout_check.sh`

Phase 7 first-wave usage:
```bash
BASE_URL=http://localhost:8000 \
PROM_URL=http://localhost:9090 \
INQUIRY_FEATURE_ENABLED=true \
EXPECT_MIGRATION_MATCH=true \
PHASE7_DOMAIN_EXPERT_ENABLED=true \
PHASE7_FIRST_WAVE_DOMAINS=finance,habits,projects,skills \
PHASE7_EXPECT_PROFILE_VERSION=1.0.0 \
PHASE7_EXPECT_STRATEGY_VERSION=1.0.0 \
bash scripts/ops/phase6_inquiry_rollout_check.sh
```

Checks include:
- build identity visibility (`/health`, `/api/bootstrap`)
- required global + Phase 7 metric family presence
- inquiry endpoint health by feature-gate state
- migration mismatch state
- recording-rule queryability
- phase 6/6.1/7/7.1 alert firing state
- profile/strategy version drift check for observed Phase 7 traffic

## 5) Deploy and rollback

Deploy checklist:
1. Confirm migration head is applied and runtime image includes migration files.
2. Deploy web image with `BUILD_ID` set.
3. Ensure Prometheus loads `phase6-inquiry-alerts.yml`.
4. Ensure Grafana provisions `lifeos-inquiry-dashboard.json` version `2`.
5. Run rollout smoke checks with Phase 7 mode enabled.

Post-deploy verification:
1. Confirm domain/profile-version metrics are present on `/metrics`.
2. Confirm per-domain recording rules are queryable.
3. Confirm Phase 7 alerts are quiet under baseline traffic.
4. Confirm no profile/strategy version drift alert.

Rollback checklist:
1. Set `ENABLE_PHASE6_FOCUSED_INQUIRY=false`.
2. Redeploy web runtime.
3. Re-run smoke checks with `INQUIRY_FEATURE_ENABLED=false`.
4. Confirm `/api/v1/inquiries` is gated (`404`) and baseline platform alerts remain healthy.

## 6) Known failure modes

- Domain/profile-version drift due mixed runtime versions.
- Elevated domain-specific error rates with otherwise normal global rates.
- Domain-specific latency regression hidden by global averages.
- Sparse evidence windows causing high empty or low-coverage rates.
- Refine loops after low-quality briefs for one domain strategy.
- Migration mismatch between runtime image and DB head.
