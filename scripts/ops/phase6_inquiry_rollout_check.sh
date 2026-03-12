#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INQUIRY_FEATURE_ENABLED="${INQUIRY_FEATURE_ENABLED:-true}"
INQUIRY_JWT="${INQUIRY_JWT:-}"
EXPECT_MIGRATION_MATCH="${EXPECT_MIGRATION_MATCH:-true}"
PHASE7_DOMAIN_EXPERT_ENABLED="${PHASE7_DOMAIN_EXPERT_ENABLED:-false}"
PHASE7_FIRST_WAVE_DOMAINS="${PHASE7_FIRST_WAVE_DOMAINS:-finance,habits,projects,skills}"
PHASE7_EXPECT_PROFILE_VERSION="${PHASE7_EXPECT_PROFILE_VERSION:-1.0.0}"
PHASE7_EXPECT_STRATEGY_VERSION="${PHASE7_EXPECT_STRATEGY_VERSION:-1.0.0}"
PHASE7_1_LATER_WAVE_ENABLED="${PHASE7_1_LATER_WAVE_ENABLED:-false}"
PHASE7_1_LATER_WAVE_DOMAINS="${PHASE7_1_LATER_WAVE_DOMAINS:-journal,relationships,health}"
PHASE7_1_EXPECT_PROFILE_VERSION="${PHASE7_1_EXPECT_PROFILE_VERSION:-1.0.0}"
PHASE7_1_EXPECT_STRATEGY_VERSION="${PHASE7_1_EXPECT_STRATEGY_VERSION:-1.0.0}"
PHASE8_CROSS_DOMAIN_ENABLED="${PHASE8_CROSS_DOMAIN_ENABLED:-false}"
PHASE8_EXPECT_PROFILE_VERSION="${PHASE8_EXPECT_PROFILE_VERSION:-1.0.0}"
PHASE8_EXPECT_STRATEGY_VERSION="${PHASE8_EXPECT_STRATEGY_VERSION:-1.0.0}"
PHASE8_PAIR_PROFILES="${PHASE8_PAIR_PROFILES:-finance_habits_v1,projects_skills_v1,journal_habits_v1,health_habits_v1,projects_calendar_v1,relationships_journal_v1}"
PHASE8_1_PRODUCTIZATION_ENABLED="${PHASE8_1_PRODUCTIZATION_ENABLED:-false}"
PHASE8_1_EXPECT_PRODUCTIZATION_VERSION="${PHASE8_1_EXPECT_PRODUCTIZATION_VERSION:-phase8_1_productization_v1}"
PHASE8_1_CANARY_PROFILE="${PHASE8_1_CANARY_PROFILE:-}"
PHASE8_1_CANARY_MIN_DIRECT_ANSWER_RATE="${PHASE8_1_CANARY_MIN_DIRECT_ANSWER_RATE:-0.55}"
PHASE8_1_CANARY_MAX_WEAK_RATE="${PHASE8_1_CANARY_MAX_WEAK_RATE:-0.70}"

required_metrics=(
  "lifeos_inquiry_created_total"
  "lifeos_inquiry_generated_total"
  "lifeos_inquiry_generated_by_domain_total"
  "lifeos_inquiry_viewed_total"
  "lifeos_inquiry_refined_total"
  "lifeos_inquiry_refined_by_domain_total"
  "lifeos_inquiry_generation_latency_seconds_bucket"
  "lifeos_inquiry_generation_latency_seconds_by_domain_bucket"
  "lifeos_inquiry_errors_total"
  "lifeos_inquiry_errors_by_domain_total"
  "lifeos_inquiry_empty_brief_total"
  "lifeos_inquiry_empty_brief_by_domain_total"
  "lifeos_inquiry_findings_by_domain_total"
  "lifeos_inquiry_findings_with_evidence_by_domain_total"
  "lifeos_inquiry_low_coverage_total"
  "lifeos_inquiry_low_coverage_by_domain_total"
  "lifeos_inquiry_refine_after_low_quality_total"
  "lifeos_inquiry_refine_after_low_quality_by_domain_total"
  "lifeos_inquiry_refine_after_low_coverage_total"
  "lifeos_inquiry_refine_after_low_coverage_by_domain_total"
  "lifeos_inquiry_quality_state_total"
  "lifeos_inquiry_quality_state_by_domain_total"
  "lifeos_inquiry_evidence_coverage_ratio"
  "lifeos_inquiry_blocked_claims_total"
  "lifeos_inquiry_blocked_claims_by_domain_total"
  "lifeos_inquiry_replay_mismatch_total"
  "lifeos_inquiry_replay_mismatch_by_domain_total"
  "lifeos_inquiry_productization_total"
  "lifeos_inquiry_productization_by_domain_total"
  "lifeos_inquiry_productization_latency_seconds_bucket"
  "lifeos_inquiry_productization_latency_seconds_by_domain_bucket"
  "lifeos_inquiry_productization_errors_total"
  "lifeos_inquiry_productization_errors_by_domain_total"
  "lifeos_inquiry_direct_answer_present_total"
  "lifeos_inquiry_direct_answer_present_by_domain_total"
  "lifeos_inquiry_answerability_total"
  "lifeos_inquiry_answerability_by_domain_total"
  "lifeos_inquiry_limitation_redundancy_removed_total"
  "lifeos_inquiry_limitation_redundancy_removed_by_domain_total"
  "lifeos_phase6_inquiry_migration_mismatch"
)

health_json="$(curl -fsS "${BASE_URL}/health")"
HEALTH_JSON="${health_json}" "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["HEALTH_JSON"])
if not payload.get("ok"):
    print("ERROR: /health did not return ok=true", file=sys.stderr)
    sys.exit(1)
if not payload.get("build_id"):
    print("ERROR: /health missing build_id", file=sys.stderr)
    sys.exit(1)
print(f"OK: build_id={payload.get('build_id')}")
PY

bootstrap_json="$(curl -fsS "${BASE_URL}/api/bootstrap")"
BOOTSTRAP_JSON="${bootstrap_json}" "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["BOOTSTRAP_JSON"])
if not payload.get("ok"):
    print("ERROR: /api/bootstrap did not return ok=true", file=sys.stderr)
    sys.exit(1)
if not payload.get("build_id"):
    print("ERROR: /api/bootstrap missing build_id", file=sys.stderr)
    sys.exit(1)
print("OK: /api/bootstrap exposes build_id")
PY

metrics_payload="$(curl -fsS "${BASE_URL}/metrics")"
for metric in "${required_metrics[@]}"; do
  if ! grep -q "^${metric}" <<< "${metrics_payload}"; then
    echo "ERROR: missing metric ${metric} from ${BASE_URL}/metrics" >&2
    exit 1
  fi
done
echo "OK: required Phase 6/6.1/7/7.1/8/8.1 inquiry metrics are exposed"

inquiry_status="$(curl -s -o /dev/null -w '%{http_code}' "${BASE_URL}/api/v1/inquiries")"
if [[ "${INQUIRY_FEATURE_ENABLED}" == "true" ]]; then
  if [[ "${inquiry_status}" != "401" ]]; then
    echo "ERROR: expected 401 for unauthenticated inquiry list when feature enabled, got ${inquiry_status}" >&2
    exit 1
  fi
  echo "OK: inquiry endpoint requires auth when enabled"

  if [[ -n "${INQUIRY_JWT}" ]]; then
    auth_status="$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${INQUIRY_JWT}" "${BASE_URL}/api/v1/inquiries")"
    if [[ "${auth_status}" != "200" ]]; then
      echo "ERROR: authenticated inquiry list expected 200, got ${auth_status}" >&2
      exit 1
    fi
    echo "OK: authenticated inquiry list is available"
  fi
else
  if [[ "${inquiry_status}" != "404" ]]; then
    echo "ERROR: expected 404 for inquiry endpoint when feature disabled, got ${inquiry_status}" >&2
    exit 1
  fi
  echo "OK: inquiry endpoint gated off when feature disabled"
fi

if [[ "${EXPECT_MIGRATION_MATCH}" == "true" ]]; then
  mismatch_value="$(grep '^lifeos_phase6_inquiry_migration_mismatch' <<< "${metrics_payload}" | awk '{print $2}' | tail -n 1)"
  if [[ -z "${mismatch_value}" ]]; then
    echo "ERROR: unable to read lifeos_phase6_inquiry_migration_mismatch" >&2
    exit 1
  fi
  if [[ "${mismatch_value}" != "0" && "${mismatch_value}" != "0.0" ]]; then
    echo "ERROR: migration mismatch metric indicates mismatch (${mismatch_value})" >&2
    exit 1
  fi
  echo "OK: migration mismatch metric indicates applied head"
fi

if curl -fsS "${PROM_URL}/api/v1/alerts" >/dev/null 2>&1; then
  required_recordings=(
    "lifeos:inquiry_error_rate:ratio"
    "lifeos:inquiry_empty_brief_rate:ratio"
    "lifeos:inquiry_evidence_coverage_ratio"
    "lifeos:inquiry_low_coverage_rate:ratio"
    "lifeos:inquiry_refine_after_low_quality_rate:ratio"
    "lifeos:inquiry_refine_after_low_coverage_rate:ratio"
    "lifeos:inquiry_quality_state_distribution:ratio"
    "lifeos:inquiry_error_rate_by_domain_profile:ratio"
    "lifeos:inquiry_empty_brief_rate_by_domain_profile:ratio"
    "lifeos:inquiry_evidence_coverage_ratio_by_domain_profile"
    "lifeos:inquiry_low_coverage_rate_by_domain_profile:ratio"
    "lifeos:inquiry_refine_after_low_quality_rate_by_domain_profile:ratio"
    "lifeos:inquiry_refine_after_low_coverage_rate_by_domain_profile:ratio"
    "lifeos:inquiry_generation_latency_p95_by_domain_profile:seconds"
    "lifeos:inquiry_quality_state_distribution_by_domain_profile:ratio"
    "lifeos:inquiry_blocked_claims_rate_by_domain_profile:ratio"
    "lifeos:inquiry_replay_mismatch_rate_by_domain_profile:ratio"
    "lifeos:inquiry_direct_answer_presence_rate:ratio"
    "lifeos:inquiry_direct_answer_presence_rate_by_domain_profile:ratio"
    "lifeos:inquiry_answerability_distribution:ratio"
    "lifeos:inquiry_answerability_distribution_by_domain_profile:ratio"
    "lifeos:inquiry_weak_answer_rate:ratio"
    "lifeos:inquiry_weak_answer_rate_by_domain_profile:ratio"
    "lifeos:inquiry_limitation_redundancy_rate:ratio"
    "lifeos:inquiry_limitation_redundancy_rate_by_domain_profile:ratio"
    "lifeos:inquiry_refine_after_weak_answer_lift:ratio"
    "lifeos:inquiry_refine_after_weak_answer_lift_by_domain_profile:ratio"
    "lifeos:inquiry_productization_latency_p95:seconds"
    "lifeos:inquiry_productization_latency_p95_by_domain_profile:seconds"
    "lifeos:inquiry_productization_error_rate:ratio"
    "lifeos:inquiry_productization_error_rate_by_domain_profile:ratio"
    "lifeos:inquiry_productization_replay_mismatch_count"
    "lifeos:inquiry_productization_replay_mismatch_count_by_domain_profile"
  )
  for recording in "${required_recordings[@]}"; do
    query_json="$(curl -fsS --get --data-urlencode "query=${recording}" "${PROM_URL}/api/v1/query")"
    QUERY_JSON="${query_json}" "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["QUERY_JSON"])
result = payload.get("data", {}).get("result", [])
if not isinstance(result, list):
    print("ERROR: recording query returned invalid result payload", file=sys.stderr)
    sys.exit(1)
PY
  done
  echo "OK: required Phase 6/6.1/7/7.1/8/8.1 recording rules are queryable"

  alerts_json="$(curl -fsS "${PROM_URL}/api/v1/alerts")"
  ALERTS_JSON="${alerts_json}" "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["ALERTS_JSON"])
alerts = payload.get("data", {}).get("alerts", [])
firing = []
for alert in alerts:
    labels = alert.get("labels", {})
    phase = str(labels.get("phase") or "")
    if phase in {"6", "6.1", "7", "7.1", "8", "8.1"} and alert.get("state") == "firing":
        firing.append(labels.get("alertname") or "unknown")

if firing:
    print("ERROR: Phase 6/6.1/7/7.1/8/8.1 inquiry alerts firing: " + ", ".join(sorted(set(firing))), file=sys.stderr)
    sys.exit(1)

print("OK: no Phase 6/6.1/7/7.1/8/8.1 inquiry alerts firing")
PY

  check_rollout_versions() {
    local wave_name="${1}"
    local domains="${2}"
    local expected_profile="${3}"
    local expected_strategy="${4}"
    local rollout_query
    rollout_query="sum(rate(lifeos_inquiry_generated_by_domain_total{expert_mode=\"true\",domain=~\"${domains//,/|}\"}[30m])) by (domain, profile_version, strategy_version)"
    rollout_json="$(curl -fsS --get --data-urlencode "query=${rollout_query}" "${PROM_URL}/api/v1/query")"
    ROLLOUT_JSON="${rollout_json}" \
    WAVE_NAME="${wave_name}" \
    EXPECTED_DOMAINS="${domains}" \
    EXPECTED_PROFILE="${expected_profile}" \
    EXPECTED_STRATEGY="${expected_strategy}" \
    "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["ROLLOUT_JSON"])
result = payload.get("data", {}).get("result", [])
wave_name = os.environ["WAVE_NAME"]
expected_domains = {d.strip() for d in os.environ["EXPECTED_DOMAINS"].split(",") if d.strip()}
expected_profile = os.environ["EXPECTED_PROFILE"]
expected_strategy = os.environ["EXPECTED_STRATEGY"]

if not result:
    print(f"WARN: no {wave_name} expert-mode traffic observed yet; version-drift check skipped", file=sys.stderr)
    sys.exit(0)

domains_seen = set()
for row in result:
    metric = row.get("metric", {})
    domain = str(metric.get("domain") or "")
    profile_version = str(metric.get("profile_version") or "")
    strategy_version = str(metric.get("strategy_version") or "")
    if domain:
        domains_seen.add(domain)
    if profile_version != expected_profile:
        print(
            f"ERROR: wave={wave_name} domain={domain} has profile_version={profile_version}, expected={expected_profile}",
            file=sys.stderr,
        )
        sys.exit(1)
    if strategy_version != expected_strategy:
        print(
            f"ERROR: wave={wave_name} domain={domain} has strategy_version={strategy_version}, expected={expected_strategy}",
            file=sys.stderr,
        )
        sys.exit(1)

missing = sorted(expected_domains - domains_seen)
if missing:
    print(f"WARN: no recent {wave_name} expert-mode traffic for domains: " + ", ".join(missing), file=sys.stderr)

print(f"OK: {wave_name} profile/strategy labels are within expected rollout versions")
PY
  }

  if [[ "${PHASE7_DOMAIN_EXPERT_ENABLED}" == "true" ]]; then
    check_rollout_versions "phase7-first-wave" "${PHASE7_FIRST_WAVE_DOMAINS}" "${PHASE7_EXPECT_PROFILE_VERSION}" "${PHASE7_EXPECT_STRATEGY_VERSION}"
  fi

  if [[ "${PHASE7_1_LATER_WAVE_ENABLED}" == "true" ]]; then
    check_rollout_versions "phase7.1-later-wave" "${PHASE7_1_LATER_WAVE_DOMAINS}" "${PHASE7_1_EXPECT_PROFILE_VERSION}" "${PHASE7_1_EXPECT_STRATEGY_VERSION}"
  fi

  if [[ "${PHASE8_CROSS_DOMAIN_ENABLED}" == "true" ]]; then
    phase8_query="sum(rate(lifeos_inquiry_generated_by_domain_total{expert_mode=\"true\",profile=~\"${PHASE8_PAIR_PROFILES//,/|}\"}[30m])) by (profile, domain, profile_version, strategy_version)"
    phase8_json="$(curl -fsS --get --data-urlencode "query=${phase8_query}" "${PROM_URL}/api/v1/query")"
    PHASE8_JSON="${phase8_json}" \
    PHASE8_PAIR_PROFILES="${PHASE8_PAIR_PROFILES}" \
    PHASE8_EXPECT_PROFILE_VERSION="${PHASE8_EXPECT_PROFILE_VERSION}" \
    PHASE8_EXPECT_STRATEGY_VERSION="${PHASE8_EXPECT_STRATEGY_VERSION}" \
    "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["PHASE8_JSON"])
result = payload.get("data", {}).get("result", [])
expected_profiles = {item.strip() for item in os.environ["PHASE8_PAIR_PROFILES"].split(",") if item.strip()}
expected_profile_version = os.environ["PHASE8_EXPECT_PROFILE_VERSION"]
expected_strategy_version = os.environ["PHASE8_EXPECT_STRATEGY_VERSION"]

if not result:
    print("WARN: no Phase 8 pair-profile traffic observed yet; version-drift check skipped", file=sys.stderr)
    sys.exit(0)

seen_profiles: set[str] = set()
for row in result:
    metric = row.get("metric", {})
    profile = str(metric.get("profile") or "")
    domain = str(metric.get("domain") or "")
    profile_version = str(metric.get("profile_version") or "")
    strategy_version = str(metric.get("strategy_version") or "")
    if expected_profiles and profile not in expected_profiles:
        print(f"ERROR: unexpected Phase 8 profile label detected: profile={profile} domain={domain}", file=sys.stderr)
        sys.exit(1)
    seen_profiles.add(profile)
    if profile_version != expected_profile_version:
        print(
            f"ERROR: Phase 8 profile_version drift for profile={profile} domain={domain}: {profile_version} != {expected_profile_version}",
            file=sys.stderr,
        )
        sys.exit(1)
    if strategy_version != expected_strategy_version:
        print(
            f"ERROR: Phase 8 strategy_version drift for profile={profile} domain={domain}: {strategy_version} != {expected_strategy_version}",
            file=sys.stderr,
        )
        sys.exit(1)

missing = sorted(expected_profiles - seen_profiles)
if missing:
    print("WARN: no recent Phase 8 traffic for profiles: " + ", ".join(missing), file=sys.stderr)
print("OK: Phase 8 pair-profile versions are within expected rollout values")
PY
  fi

  if [[ "${PHASE8_1_PRODUCTIZATION_ENABLED}" == "true" ]]; then
    phase81_query="sum(rate(lifeos_inquiry_productization_by_domain_total[30m])) by (domain, profile, profile_version, strategy, strategy_version, expert_mode)"
    phase81_json="$(curl -fsS --get --data-urlencode "query=${phase81_query}" "${PROM_URL}/api/v1/query")"
    PHASE81_JSON="${phase81_json}" "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["PHASE81_JSON"])
result = payload.get("data", {}).get("result", [])
if not result:
    print("WARN: no Phase 8.1 productization traffic observed yet; profile-level checks skipped", file=sys.stderr)
    sys.exit(0)
print("OK: Phase 8.1 productization traffic is observable")
PY

    if [[ -n "${PHASE8_1_CANARY_PROFILE}" ]]; then
      canary_direct_query="lifeos:inquiry_direct_answer_presence_rate_by_domain_profile:ratio{profile=\"${PHASE8_1_CANARY_PROFILE}\"}"
      canary_weak_query="lifeos:inquiry_weak_answer_rate_by_domain_profile:ratio{profile=\"${PHASE8_1_CANARY_PROFILE}\"}"
      canary_direct_json="$(curl -fsS --get --data-urlencode "query=${canary_direct_query}" "${PROM_URL}/api/v1/query")"
      canary_weak_json="$(curl -fsS --get --data-urlencode "query=${canary_weak_query}" "${PROM_URL}/api/v1/query")"
      CANARY_DIRECT_JSON="${canary_direct_json}" \
      CANARY_WEAK_JSON="${canary_weak_json}" \
      CANARY_PROFILE="${PHASE8_1_CANARY_PROFILE}" \
      MIN_DIRECT="${PHASE8_1_CANARY_MIN_DIRECT_ANSWER_RATE}" \
      MAX_WEAK="${PHASE8_1_CANARY_MAX_WEAK_RATE}" \
      "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

def _values(raw: str) -> list[float]:
    payload = json.loads(raw)
    result = payload.get("data", {}).get("result", [])
    values: list[float] = []
    for row in result:
        metric = row.get("metric", {})
        value = row.get("value", [None, None])[1]
        if value is None:
            continue
        try:
            values.append(float(value))
        except Exception:
            continue
    return values

canary = os.environ["CANARY_PROFILE"]
min_direct = float(os.environ["MIN_DIRECT"])
max_weak = float(os.environ["MAX_WEAK"])
direct_values = _values(os.environ["CANARY_DIRECT_JSON"])
weak_values = _values(os.environ["CANARY_WEAK_JSON"])

if not direct_values:
    print(f"WARN: no direct-answer rate series for canary profile={canary}; threshold check skipped", file=sys.stderr)
    sys.exit(0)

direct_min_observed = min(direct_values)
if direct_min_observed < min_direct:
    print(
        f"ERROR: canary profile={canary} direct-answer presence {direct_min_observed:.3f} below threshold {min_direct:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)

if weak_values:
    weak_max_observed = max(weak_values)
    if weak_max_observed > max_weak:
        print(
            f"ERROR: canary profile={canary} weak-answer rate {weak_max_observed:.3f} above threshold {max_weak:.3f}",
            file=sys.stderr,
        )
        sys.exit(1)

print(f"OK: Phase 8.1 canary thresholds satisfied for profile={canary}")
PY
    fi

    if [[ -n "${INQUIRY_JWT}" ]]; then
      productization_version_json="$(curl -fsS -H "Authorization: Bearer ${INQUIRY_JWT}" "${BASE_URL}/api/v1/inquiries?limit=20&offset=0")"
      PRODUCTIZATION_VERSION_JSON="${productization_version_json}" \
      EXPECTED_PRODUCTIZATION_VERSION="${PHASE8_1_EXPECT_PRODUCTIZATION_VERSION}" \
      "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["PRODUCTIZATION_VERSION_JSON"])
items = payload.get("items", [])
expected = os.environ["EXPECTED_PRODUCTIZATION_VERSION"]
observed = []
for item in items:
    latest = item.get("latest_brief") or {}
    brief = latest.get("brief") if isinstance(latest, dict) else None
    if not isinstance(brief, dict):
        continue
    metadata = brief.get("productization_metadata")
    if not isinstance(metadata, dict):
        continue
    version = str(metadata.get("version") or "").strip()
    if version:
        observed.append(version)

if not observed:
    print("WARN: no productization metadata version observed from inquiry list; version check skipped", file=sys.stderr)
    sys.exit(0)

unexpected = sorted({value for value in observed if value != expected})
if unexpected:
    print(
        "ERROR: observed unexpected productization metadata version(s): "
        + ", ".join(unexpected)
        + f"; expected={expected}",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"OK: observed productization metadata version matches expected ({expected})")
PY
    fi
  fi
else
  echo "WARN: Prometheus is unreachable at ${PROM_URL}; alert-state check skipped" >&2
fi

echo "Phase 6/6.1/7/7.1/8/8.1 focused inquiry rollout checks passed"
