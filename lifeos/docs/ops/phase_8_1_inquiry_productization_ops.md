# Phase 8.1 Inquiry Productization - Ops Runbook

Owner: DevOps / Platform
Scope: operational rollout safety and usefulness-SLO observability for inquiry productization
Last updated: 2026-03-13

## 1) Rollout controls

Primary gates:
- `ENABLE_PHASE6_FOCUSED_INQUIRY`
- `ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES` (for pair-profile canary coverage)

Phase 8.1 rollout check controls:
- `PHASE8_1_PRODUCTIZATION_ENABLED`
- `PHASE8_1_EXPECT_PRODUCTIZATION_VERSION` (default: `phase8_1_productization_v1`)
- `PHASE8_1_CANARY_PROFILE` (optional profile for strict canary thresholds)
- `PHASE8_1_CANARY_MIN_DIRECT_ANSWER_RATE` (default: `0.55`)
- `PHASE8_1_CANARY_MAX_WEAK_RATE` (default: `0.70`)

Pair-profile canary controls (from Phase 8):
- `PHASE8_CROSS_DOMAIN_ENABLED`
- `PHASE8_PAIR_PROFILES`
- `PHASE8_EXPECT_PROFILE_VERSION`
- `PHASE8_EXPECT_STRATEGY_VERSION`

## 2) Metrics

Runtime metrics used for Phase 8.1:
- `lifeos_inquiry_productization_total`
- `lifeos_inquiry_productization_by_domain_total`
- `lifeos_inquiry_productization_latency_seconds_bucket`
- `lifeos_inquiry_productization_latency_seconds_by_domain_bucket`
- `lifeos_inquiry_productization_errors_total`
- `lifeos_inquiry_productization_errors_by_domain_total`
- `lifeos_inquiry_direct_answer_present_total`
- `lifeos_inquiry_direct_answer_present_by_domain_total`
- `lifeos_inquiry_answerability_total{classification}`
- `lifeos_inquiry_answerability_by_domain_total{classification,...}`
- `lifeos_inquiry_limitation_redundancy_removed_total`
- `lifeos_inquiry_limitation_redundancy_removed_by_domain_total`
- `lifeos_inquiry_replay_mismatch_total`
- `lifeos_inquiry_replay_mismatch_by_domain_total`

Derived recording rules:
- `lifeos:inquiry_direct_answer_presence_rate:ratio`
- `lifeos:inquiry_direct_answer_presence_rate_by_domain_profile:ratio`
- `lifeos:inquiry_answerability_distribution:ratio`
- `lifeos:inquiry_answerability_distribution_by_domain_profile:ratio`
- `lifeos:inquiry_weak_answer_rate:ratio`
- `lifeos:inquiry_weak_answer_rate_by_domain_profile:ratio`
- `lifeos:inquiry_limitation_redundancy_rate:ratio`
- `lifeos:inquiry_limitation_redundancy_rate_by_domain_profile:ratio`
- `lifeos:inquiry_refine_after_weak_answer_lift:ratio`
- `lifeos:inquiry_refine_after_weak_answer_lift_by_domain_profile:ratio`
- `lifeos:inquiry_productization_latency_p95:seconds`
- `lifeos:inquiry_productization_latency_p95_by_domain_profile:seconds`
- `lifeos:inquiry_productization_error_rate:ratio`
- `lifeos:inquiry_productization_error_rate_by_domain_profile:ratio`
- `lifeos:inquiry_productization_replay_mismatch_count`
- `lifeos:inquiry_productization_replay_mismatch_count_by_domain_profile`

## 3) Dashboard and alerts

Dashboard:
- `deploy/monitoring/grafana/provisioning/dashboards/lifeos-inquiry-dashboard.json`

Phase 8.1 panels:
- Productization runs/errors
- Productization latency p95
- Productization error rate
- Direct-answer presence rate
- Answerability distribution
- Weak-answer rate
- Limitation redundancy removed per brief
- Refine-after-weak-answer lift
- Replay mismatch count
- Pair-profile canary comparison (direct-answer vs weak-answer)

Prometheus rule file:
- `deploy/monitoring/phase6-inquiry-alerts.yml`

Phase 8.1 alerts:
- `Phase81ProductizationErrorRateHigh`
- `Phase81ProductizationLatencyHigh`
- `Phase81WeakAnswerRateHigh`
- `Phase81DirectAnswerPresenceLow`
- `Phase81ProductizationReplayMismatchDetected`

## 4) Staged rollout plan

1. Staging validation
- Keep `EXPECT_MIGRATION_MATCH=true`.
- Run `scripts/ops/phase8_1_inquiry_productization_rollout_check.sh`.
- Confirm no phase `8.1` alerts fire for one observation window.

2. Single canary
- Set `PHASE8_1_CANARY_PROFILE` to one active profile.
- Enforce canary thresholds:
  - direct answer presence >= `PHASE8_1_CANARY_MIN_DIRECT_ANSWER_RATE`
  - weak answer rate <= `PHASE8_1_CANARY_MAX_WEAK_RATE`
- Verify `productization_metadata.version == PHASE8_1_EXPECT_PRODUCTIZATION_VERSION` from authenticated inquiry list.

3. Gradual production enablement
- Expand traffic/profile exposure in stages.
- Keep Phase 8 and 8.1 dashboards visible side-by-side for baseline comparison.
- Advance only when phase `8.1` alerts remain quiet and canary thresholds hold.

## 5) Rollback

Rollback triggers:
- sustained `Phase81ProductizationErrorRateHigh`
- sustained `Phase81WeakAnswerRateHigh`
- sustained `Phase81DirectAnswerPresenceLow`
- any `Phase81ProductizationReplayMismatchDetected`

Rollback steps:
1. Deploy previous runtime image (Phase 8 baseline behavior).
2. Keep DB/migrations unchanged (8.1 has no schema expansion).
3. Keep `ENABLE_PHASE6_FOCUSED_INQUIRY=true` so inquiry remains available.
4. Re-run rollout checks and verify phase `8.1` alerts clear.

Safety invariant:
- Single-domain and pair inquiry flows remain online under rollback to Phase 8 baseline.

## 6) Verification command

```bash
BASE_URL=http://localhost:8000 \
PROM_URL=http://localhost:9090 \
INQUIRY_FEATURE_ENABLED=true \
EXPECT_MIGRATION_MATCH=true \
PHASE8_CROSS_DOMAIN_ENABLED=true \
PHASE8_PAIR_PROFILES=finance_habits_v1,projects_skills_v1,journal_habits_v1,health_habits_v1,projects_calendar_v1,relationships_journal_v1 \
PHASE8_1_PRODUCTIZATION_ENABLED=true \
PHASE8_1_EXPECT_PRODUCTIZATION_VERSION=phase8_1_productization_v1 \
PHASE8_1_CANARY_PROFILE=finance_habits_v1 \
PHASE8_1_CANARY_MIN_DIRECT_ANSWER_RATE=0.55 \
PHASE8_1_CANARY_MAX_WEAK_RATE=0.70 \
bash scripts/ops/phase8_1_inquiry_productization_rollout_check.sh
```

Baseline/canary snapshots (Prometheus query capture):

```bash
PROM_URL=http://localhost:9090 SNAPSHOT_LABEL=baseline bash scripts/ops/phase8_1_inquiry_productization_snapshot.sh
PROM_URL=http://localhost:9090 SNAPSHOT_LABEL=canary bash scripts/ops/phase8_1_inquiry_productization_snapshot.sh
```

## 7) Known failure modes

- Productization metrics present but recording rules not loaded in Prometheus.
- Canary profile has no traffic; threshold checks are skipped with warning.
- Authenticated list endpoint unavailable (no JWT), so metadata-version check is skipped.
- Replay mismatch counter increments under mixed runtime versions.
