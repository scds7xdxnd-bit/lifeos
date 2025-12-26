# Phase 3a Intelligence Hardening - DevOps Runbook

## Purpose
Operationalize determinism, governance, and telemetry checks for Phase 3a without CI/CD changes.

## Smoke tests (determinism + governance)
- Script: `scripts/ops/phase3a_replay_smoketest.sh`
- Runs unit tests that validate replay determinism, governance, ML replay contracts, and projection registry.
- Optional integration check (requires DB): `RUN_INTEGRATION=true`

```bash
scripts/ops/phase3a_replay_smoketest.sh
RUN_INTEGRATION=true scripts/ops/phase3a_replay_smoketest.sh
```

## Telemetry snapshot check (non-production)
- Script: `scripts/ops/phase3a_insight_telemetry_check.sh`
- Requires an admin Bearer token and non-production environment (endpoint disabled in prod).
- Validates telemetry fields and flags high average latency (default threshold 1000ms).

```bash
AUTH_TOKEN="$TOKEN" BASE_URL="https://staging.lifeos.example.com" \
  scripts/ops/phase3a_insight_telemetry_check.sh

# Optional threshold override
MAX_AVG_LATENCY_MS=500 scripts/ops/phase3a_insight_telemetry_check.sh
```

## Monitoring focus
- Determinism regression: run the replay/governance smoke tests after deployments that touch insights or contracts.
- Latency regressions: watch `avg_latency_ms` and `per_rule_avg_latency_ms` in telemetry snapshots during staging.
- Routing drift: review `per_rule_counts` + review queue volume after deploys; unexpected spikes should trigger investigation.

## Rollout guidance
- No pipeline changes required.
- Use these checks during staging validation and before Phase 3b sign-off.
