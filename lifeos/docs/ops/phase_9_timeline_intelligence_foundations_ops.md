# Phase 9 Timeline Intelligence Foundations - Ops Runbook

Owner: DevOps / Platform
Scope: rollout safety, observability, and rollback for Phase 9 timeline profiles
Last updated: 2026-03-13

## 1) Rollout controls

Primary inquiry gates:
- `ENABLE_PHASE6_FOCUSED_INQUIRY`
- `ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES` (for approved pair canaries)
- `ENABLE_PHASE9_TIMELINE_INTELLIGENCE`

Phase 9 rollout check controls:
- `PHASE9_TIMELINE_ENABLED`
- `PHASE9_FIRST_WAVE_DOMAINS` (default: `finance,habits,projects,skills,calendar`)
- `PHASE9_APPROVED_PAIR_DOMAINS` (default: `finance+habits,projects+skills,calendar+projects`)
- `PHASE9_EXPECTED_PROFILES`
- `PHASE9_EXPECT_PROFILE_VERSION` (default: `1.0.0`)
- `PHASE9_EXPECT_STRATEGY_VERSION` (default: `1.0.0`)
- `PHASE9_CANARY_DOMAIN` (optional)
- `PHASE9_CANARY_MAX_INSUFFICIENCY_RATE` (default: `0.80`)
- `PHASE9_CANARY_MAX_LATENCY_P95` (default: `1.20`)
- `PHASE9_CANARY_MAX_BLOCKED_CLAIMS_RATE` (default: `0.10`)
- `PHASE9_CANARY_MAX_REPLAY_MISMATCH_COUNT` (default: `0`)

Runtime profile allowlist:
- `PHASE9_ENABLED_TIMELINE_PROFILES` (comma-separated `timeline_profile_id` values)

## 2) Metrics and recording rules

Raw Phase 9 metrics:
- `lifeos_timeline_profile_usage_total`
- `lifeos_timeline_generation_latency_seconds_bucket`
- `lifeos_timeline_insufficiency_total`
- `lifeos_timeline_baseline_coverage_windows_bucket`
- `lifeos_timeline_blocked_claims_total`
- `lifeos_timeline_replay_mismatch_total`

Derived recordings:
- `lifeos:timeline_profile_usage_rate_by_profile:per_second`
- `lifeos:timeline_generation_latency_p95_by_profile:seconds`
- `lifeos:timeline_error_rate_by_profile:ratio`
- `lifeos:timeline_insufficiency_rate_by_profile:ratio`
- `lifeos:timeline_baseline_coverage_avg_windows_by_profile`
- `lifeos:timeline_baseline_coverage_distribution_by_profile:ratio`
- `lifeos:timeline_blocked_claims_rate_by_profile:ratio`
- `lifeos:timeline_replay_mismatch_count_by_profile`
- `lifeos:timeline_replay_mismatch_rate_by_profile:ratio`
- `lifeos:timeline_output_presence_rate:ratio`
- `lifeos:timeline_output_presence_rate_by_domain:ratio`

Build/profile identity triage:
- `/health` build id and `/api/bootstrap` build id must remain visible.
- Timeline profile/version labels (`profile`, `profile_version`, `strategy_version`) must match rollout expectations.

## 3) Dashboard and alerts

Dashboard:
- `deploy/monitoring/grafana/provisioning/dashboards/lifeos-inquiry-dashboard.json`

Phase 9 alert rules:
- `Phase9TimelineGenerationLatencyHigh`
- `Phase9TimelineErrorRateHigh`
- `Phase9TimelineInsufficiencyRateHigh`
- `Phase9TimelineBlockedClaimsSpike`
- `Phase9TimelineReplayMismatchDetected`
- `Phase9TimelineOutputPresenceLow`
- `Phase9TimelineProfileVersionUnexpected`

Prometheus rule file:
- `deploy/monitoring/phase6-inquiry-alerts.yml`

## 4) Staged rollout policy

1. Staging validation
- Enable `ENABLE_PHASE9_TIMELINE_INTELLIGENCE=true`.
- Keep strict migration checks enabled (`EXPECT_MIGRATION_MATCH=true`).
- Run `scripts/ops/phase9_timeline_rollout_check.sh`.
- Confirm no phase `9` alerts fire for one full observation window.

2. Single-domain canary
- Set `PHASE9_ENABLED_TIMELINE_PROFILES` to one first-wave domain timeline profile.
- Set `PHASE9_CANARY_DOMAIN` to the same domain.
- Run strict rollout check and evaluate canary thresholds.

3. Approved-pair temporal canary
- Keep domain canary stable, then add one first-wave approved pair profile.
- Validate `domain` labels stay inside approved pair scope only.
- Confirm `Phase9TimelineOutputPresenceLow` and replay mismatch alerts stay quiet.

4. Production staged enablement
- Expand allowlist incrementally in `PHASE9_ENABLED_TIMELINE_PROFILES`.
- Capture baseline/canary snapshots for each expansion.
- Promote only when profile/version labels are stable and no phase `9` alert remains firing.

## 5) Rollback

Primary rollback:
1. Set `ENABLE_PHASE9_TIMELINE_INTELLIGENCE=false`.
2. Redeploy web service.
3. Re-run `scripts/ops/phase9_timeline_rollout_check.sh` with `PHASE9_TIMELINE_ENABLED=false`.

Partial rollback:
1. Keep timeline enabled.
2. Remove offending profile IDs from `PHASE9_ENABLED_TIMELINE_PROFILES`.
3. Redeploy and verify profile usage labels converge.

Safety invariant:
- Base inquiry remains online (`ENABLE_PHASE6_FOCUSED_INQUIRY=true`) when Phase 9 timeline layer is disabled.
- No domain behavior rewrite is required for rollback.

## 6) Verification commands

Strict rollout check:

```bash
BASE_URL=http://localhost:8000 \
PROM_URL=http://localhost:9090 \
INQUIRY_FEATURE_ENABLED=true \
EXPECT_MIGRATION_MATCH=true \
PHASE8_CROSS_DOMAIN_ENABLED=true \
PHASE9_TIMELINE_ENABLED=true \
PHASE9_FIRST_WAVE_DOMAINS=finance,habits,projects,skills,calendar \
PHASE9_APPROVED_PAIR_DOMAINS=finance+habits,projects+skills,calendar+projects \
PHASE9_EXPECTED_PROFILES=finance_timeline_v1,habits_timeline_v1,projects_timeline_v1,skills_timeline_v1,calendar_timeline_v1,finance_habits_timeline_v1,projects_skills_timeline_v1,projects_calendar_timeline_v1 \
PHASE9_EXPECT_PROFILE_VERSION=1.0.0 \
PHASE9_EXPECT_STRATEGY_VERSION=1.0.0 \
bash scripts/ops/phase9_timeline_rollout_check.sh
```

Baseline/canary snapshots:

```bash
PROM_URL=http://localhost:9090 SNAPSHOT_LABEL=baseline bash scripts/ops/phase9_timeline_snapshot.sh
PROM_URL=http://localhost:9090 SNAPSHOT_LABEL=canary bash scripts/ops/phase9_timeline_snapshot.sh
```

## 7) Known rollout blockers

- `/metrics` missing one or more `lifeos_timeline_*` series.
- Prometheus not loading `phase6-inquiry-alerts.yml` recordings/alerts for phase `9`.
- Timeline profile/version drift against expected rollout values.
- Timeline output presence falls below threshold for active first-wave scopes.
- Any replay mismatch detected under active Phase 9 traffic.
