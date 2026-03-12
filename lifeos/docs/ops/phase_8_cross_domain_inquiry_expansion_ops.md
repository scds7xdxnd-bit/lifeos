# Phase 8 Cross-Domain Inquiry Expansion - Ops Runbook

Owner: DevOps / Platform
Scope: rollout, observability, and rollback safety for cross-domain pair inquiry profiles
Last updated: 2026-03-12

## 1) Rollout controls

Primary inquiry gate:
- `ENABLE_PHASE6_FOCUSED_INQUIRY`

Phase 8 pair-profile controls:
- `ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES`
- `PHASE8_ENABLED_PAIR_PROFILES` (comma-separated profile allowlist; empty means all approved profiles)

Rollout smoke-check controls:
- `PHASE8_CROSS_DOMAIN_ENABLED`
- `PHASE8_PAIR_PROFILES` (default: `finance_habits_v1,projects_skills_v1,journal_habits_v1,health_habits_v1,projects_calendar_v1,relationships_journal_v1`)
- `PHASE8_EXPECT_PROFILE_VERSION` (default: `1.0.0`)
- `PHASE8_EXPECT_STRATEGY_VERSION` (default: `1.0.0`)

Approved pair profiles:
- `finance_habits_v1`
- `projects_skills_v1`
- `journal_habits_v1`
- `health_habits_v1`
- `projects_calendar_v1`
- `relationships_journal_v1`

## 2) Metrics

Required counters/gauges for Phase 8 observability:
- `lifeos_inquiry_generated_by_domain_total`
- `lifeos_inquiry_generation_latency_seconds_by_domain_bucket`
- `lifeos_inquiry_errors_by_domain_total`
- `lifeos_inquiry_empty_brief_by_domain_total`
- `lifeos_inquiry_low_coverage_by_domain_total`
- `lifeos_inquiry_refine_after_low_coverage_total`
- `lifeos_inquiry_refine_after_low_coverage_by_domain_total`
- `lifeos_inquiry_blocked_claims_total`
- `lifeos_inquiry_blocked_claims_by_domain_total`
- `lifeos_inquiry_replay_mismatch_total`
- `lifeos_inquiry_replay_mismatch_by_domain_total`

Derived recordings:
- `lifeos:inquiry_refine_after_low_coverage_rate:ratio`
- `lifeos:inquiry_refine_after_low_coverage_rate_by_domain_profile:ratio`
- `lifeos:inquiry_blocked_claims_rate_by_domain_profile:ratio`
- `lifeos:inquiry_replay_mismatch_rate_by_domain_profile:ratio`

## 3) Dashboard and alerts

Files:
- `deploy/monitoring/grafana/provisioning/dashboards/lifeos-inquiry-dashboard.json`
- `deploy/monitoring/phase6-inquiry-alerts.yml`

Phase 8 alerts:
- `Phase8CrossDomainPairErrorRateHigh`
- `Phase8CrossDomainPairLatencyHigh`
- `Phase8CrossDomainPairEmptyBriefHigh`
- `Phase8CrossDomainPairLowCoverageHigh`
- `Phase8CrossDomainPairRefineAfterLowCoverageHigh`
- `Phase8CrossDomainPairBlockedClaimsSpike`
- `Phase8CrossDomainPairReplayMismatchDetected`
- `Phase8CrossDomainPairProfileVersionUnexpected`

## 4) Staged rollout

1. Staging validation
- Set `ENABLE_PHASE6_FOCUSED_INQUIRY=true`
- Set `ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES=true`
- Set `PHASE8_ENABLED_PAIR_PROFILES` to one canary profile
- Run rollout check with `PHASE8_CROSS_DOMAIN_ENABLED=true`

2. Single-pair canary
- Keep exactly one profile in `PHASE8_ENABLED_PAIR_PROFILES`
- Confirm no phase `8` alerts fire for at least one observation window
- Confirm expected profile/strategy version labels only

3. Gradual production enablement
- Add profiles incrementally to `PHASE8_ENABLED_PAIR_PROFILES`
- Verify metrics and dashboard panels for each added pair
- Keep strict migration match checks enabled

## 5) Rollback

Fast rollback:
1. Set `ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES=false`
2. Redeploy web service
3. Re-run rollout checks

Partial rollback:
1. Remove affected profile(s) from `PHASE8_ENABLED_PAIR_PROFILES`
2. Redeploy web service
3. Verify only allowed profiles emit traffic

Safety invariant:
- Single-domain inquiry remains active while pair profiles are disabled.

## 6) Verification command

```bash
BASE_URL=http://localhost:8000 \
PROM_URL=http://localhost:9090 \
INQUIRY_FEATURE_ENABLED=true \
EXPECT_MIGRATION_MATCH=true \
PHASE8_CROSS_DOMAIN_ENABLED=true \
PHASE8_PAIR_PROFILES=finance_habits_v1,projects_skills_v1,journal_habits_v1,health_habits_v1,projects_calendar_v1,relationships_journal_v1 \
PHASE8_EXPECT_PROFILE_VERSION=1.0.0 \
PHASE8_EXPECT_STRATEGY_VERSION=1.0.0 \
bash scripts/ops/phase6_inquiry_rollout_check.sh
```
