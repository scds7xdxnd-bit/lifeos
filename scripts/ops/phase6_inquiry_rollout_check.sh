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
PHASE9_TIMELINE_ENABLED="${PHASE9_TIMELINE_ENABLED:-false}"
PHASE9_FIRST_WAVE_DOMAINS="${PHASE9_FIRST_WAVE_DOMAINS:-finance,habits,projects,skills,calendar}"
PHASE9_APPROVED_PAIR_DOMAINS="${PHASE9_APPROVED_PAIR_DOMAINS:-finance+habits,projects+skills,calendar+projects}"
PHASE9_EXPECTED_PROFILES="${PHASE9_EXPECTED_PROFILES:-finance_timeline_v1,habits_timeline_v1,projects_timeline_v1,skills_timeline_v1,calendar_timeline_v1,finance_habits_timeline_v1,projects_skills_timeline_v1,projects_calendar_timeline_v1}"
PHASE9_EXPECT_PROFILE_VERSION="${PHASE9_EXPECT_PROFILE_VERSION:-1.0.0}"
PHASE9_EXPECT_STRATEGY_VERSION="${PHASE9_EXPECT_STRATEGY_VERSION:-1.0.0}"
PHASE9_CANARY_DOMAIN="${PHASE9_CANARY_DOMAIN:-}"
PHASE9_CANARY_MAX_INSUFFICIENCY_RATE="${PHASE9_CANARY_MAX_INSUFFICIENCY_RATE:-0.80}"
PHASE9_CANARY_MAX_LATENCY_P95="${PHASE9_CANARY_MAX_LATENCY_P95:-1.20}"
PHASE9_CANARY_MAX_BLOCKED_CLAIMS_RATE="${PHASE9_CANARY_MAX_BLOCKED_CLAIMS_RATE:-0.10}"
PHASE9_CANARY_MAX_REPLAY_MISMATCH_COUNT="${PHASE9_CANARY_MAX_REPLAY_MISMATCH_COUNT:-0}"
PHASE10_HUMANIZATION_ENABLED="${PHASE10_HUMANIZATION_ENABLED:-false}"
PHASE10_EXPECT_HUMANIZATION_VERSION="${PHASE10_EXPECT_HUMANIZATION_VERSION:-phase10_humanization_v1}"
PHASE10_CANARY_PROFILE="${PHASE10_CANARY_PROFILE:-}"
PHASE10_CANARY_MAX_FALLBACK_RATE="${PHASE10_CANARY_MAX_FALLBACK_RATE:-0.20}"
PHASE10_CANARY_MAX_FAILURE_RATE="${PHASE10_CANARY_MAX_FAILURE_RATE:-0.08}"
PHASE10_CANARY_MAX_LATENCY_P95="${PHASE10_CANARY_MAX_LATENCY_P95:-0.25}"
PHASE10_CANARY_MAX_EQUIVALENCE_VIOLATION_COUNT="${PHASE10_CANARY_MAX_EQUIVALENCE_VIOLATION_COUNT:-0}"
PHASE10_CANARY_MAX_REFINE_AFTER_VIEW_RATE="${PHASE10_CANARY_MAX_REFINE_AFTER_VIEW_RATE:-0.70}"

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
  "lifeos_inquiry_humanization_render_total"
  "lifeos_inquiry_humanization_render_by_domain_total"
  "lifeos_inquiry_humanization_render_latency_seconds_bucket"
  "lifeos_inquiry_humanization_render_latency_seconds_by_domain_bucket"
  "lifeos_inquiry_humanization_failure_total"
  "lifeos_inquiry_humanization_failure_by_domain_total"
  "lifeos_inquiry_humanization_fallback_total"
  "lifeos_inquiry_humanization_fallback_by_domain_total"
  "lifeos_inquiry_humanization_equivalence_violation_total"
  "lifeos_inquiry_humanization_equivalence_violation_by_domain_total"
  "lifeos_inquiry_humanized_output_total"
  "lifeos_inquiry_humanized_output_by_domain_total"
  "lifeos_inquiry_humanized_view_total"
  "lifeos_inquiry_humanized_view_by_domain_total"
  "lifeos_inquiry_technical_brief_expanded_total"
  "lifeos_inquiry_technical_brief_expanded_by_domain_total"
  "lifeos_inquiry_refine_after_humanized_view_total"
  "lifeos_inquiry_refine_after_humanized_view_by_domain_total"
  "lifeos_inquiry_humanization_version_total"
  "lifeos_phase6_inquiry_migration_mismatch"
)

if [[ "${PHASE9_TIMELINE_ENABLED}" == "true" ]]; then
  required_metrics+=(
    "lifeos_timeline_profile_usage_total"
    "lifeos_timeline_generation_latency_seconds_bucket"
    "lifeos_timeline_insufficiency_total"
    "lifeos_timeline_baseline_coverage_windows_bucket"
    "lifeos_timeline_blocked_claims_total"
    "lifeos_timeline_replay_mismatch_total"
  )
fi

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
echo "OK: required Phase 6/6.1/7/7.1/8/8.1/9/10 inquiry metrics are exposed"

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
    "lifeos:inquiry_humanization_render_latency_p95:seconds"
    "lifeos:inquiry_humanization_render_latency_p95_by_domain_profile:seconds"
    "lifeos:inquiry_humanization_failure_rate:ratio"
    "lifeos:inquiry_humanization_failure_rate_by_domain_profile:ratio"
    "lifeos:inquiry_humanization_fallback_rate:ratio"
    "lifeos:inquiry_humanization_fallback_rate_by_domain_profile:ratio"
    "lifeos:inquiry_humanization_equivalence_violation_count"
    "lifeos:inquiry_humanization_equivalence_violation_count_by_domain_profile"
    "lifeos:inquiry_humanized_output_presence_rate:ratio"
    "lifeos:inquiry_humanized_output_presence_rate_by_domain_profile:ratio"
    "lifeos:inquiry_technical_brief_expansion_rate:ratio"
    "lifeos:inquiry_technical_brief_expansion_rate_by_domain_profile:ratio"
    "lifeos:inquiry_refine_after_humanized_view_rate:ratio"
    "lifeos:inquiry_refine_after_humanized_view_rate_by_domain_profile:ratio"
    "lifeos:timeline_profile_usage_rate_by_profile:per_second"
    "lifeos:timeline_generation_latency_p95_by_profile:seconds"
    "lifeos:timeline_error_rate_by_profile:ratio"
    "lifeos:timeline_insufficiency_rate_by_profile:ratio"
    "lifeos:timeline_baseline_coverage_avg_windows_by_profile"
    "lifeos:timeline_baseline_coverage_distribution_by_profile:ratio"
    "lifeos:timeline_blocked_claims_rate_by_profile:ratio"
    "lifeos:timeline_replay_mismatch_count_by_profile"
    "lifeos:timeline_replay_mismatch_rate_by_profile:ratio"
    "lifeos:timeline_output_presence_rate:ratio"
    "lifeos:timeline_output_presence_rate_by_domain:ratio"
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
  echo "OK: required Phase 6/6.1/7/7.1/8/8.1/9/10 recording rules are queryable"

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
    if phase in {"6", "6.1", "7", "7.1", "8", "8.1", "9", "10"} and alert.get("state") == "firing":
        firing.append(labels.get("alertname") or "unknown")

if firing:
    print("ERROR: Phase 6/6.1/7/7.1/8/8.1/9/10 inquiry alerts firing: " + ", ".join(sorted(set(firing))), file=sys.stderr)
    sys.exit(1)

print("OK: no Phase 6/6.1/7/7.1/8/8.1/9/10 inquiry alerts firing")
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

  if [[ "${PHASE9_TIMELINE_ENABLED}" == "true" ]]; then
    phase9_domains_regex="${PHASE9_FIRST_WAVE_DOMAINS//,/|}"
    if [[ -n "${PHASE9_APPROVED_PAIR_DOMAINS}" ]]; then
      phase9_domains_regex="${phase9_domains_regex}|${PHASE9_APPROVED_PAIR_DOMAINS//,/|}"
    fi
    # PromQL string escaping rejects "\+"; use character class form for literal plus in pair domains.
    phase9_domains_regex="${phase9_domains_regex//+/[+]}"

    phase9_usage_query="sum(rate(lifeos_timeline_profile_usage_total{domain=~\"${phase9_domains_regex}\"}[30m])) by (domain, profile, profile_version, strategy, strategy_version, expert_mode)"
    phase9_usage_json="$(curl -fsS --get --data-urlencode "query=${phase9_usage_query}" "${PROM_URL}/api/v1/query")"
    PHASE9_USAGE_JSON="${phase9_usage_json}" \
    PHASE9_FIRST_WAVE_DOMAINS="${PHASE9_FIRST_WAVE_DOMAINS}" \
    PHASE9_APPROVED_PAIR_DOMAINS="${PHASE9_APPROVED_PAIR_DOMAINS}" \
    PHASE9_EXPECTED_PROFILES="${PHASE9_EXPECTED_PROFILES}" \
    PHASE9_EXPECT_PROFILE_VERSION="${PHASE9_EXPECT_PROFILE_VERSION}" \
    PHASE9_EXPECT_STRATEGY_VERSION="${PHASE9_EXPECT_STRATEGY_VERSION}" \
    "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["PHASE9_USAGE_JSON"])
rows = payload.get("data", {}).get("result", [])
expected_domains = {
    item.strip()
    for item in (os.environ["PHASE9_FIRST_WAVE_DOMAINS"] + "," + os.environ["PHASE9_APPROVED_PAIR_DOMAINS"]).split(",")
    if item.strip()
}
expected_profiles = {item.strip() for item in os.environ["PHASE9_EXPECTED_PROFILES"].split(",") if item.strip()}
expected_profile_version = os.environ["PHASE9_EXPECT_PROFILE_VERSION"]
expected_strategy_version = os.environ["PHASE9_EXPECT_STRATEGY_VERSION"]

if not rows:
    print("WARN: no Phase 9 timeline traffic observed yet; profile validation skipped", file=sys.stderr)
    sys.exit(0)

seen_profiles: set[str] = set()
for row in rows:
    metric = row.get("metric", {})
    domain = str(metric.get("domain") or "")
    profile = str(metric.get("profile") or "")
    profile_version = str(metric.get("profile_version") or "")
    strategy_version = str(metric.get("strategy_version") or "")

    if domain and domain not in expected_domains:
        print(f"ERROR: unexpected Phase 9 timeline domain label observed: {domain}", file=sys.stderr)
        sys.exit(1)
    if profile and profile not in expected_profiles:
        print(f"ERROR: unexpected Phase 9 timeline profile observed: {profile}", file=sys.stderr)
        sys.exit(1)
    if profile_version != expected_profile_version:
        print(
            f"ERROR: Phase 9 profile_version drift for profile={profile} domain={domain}: {profile_version} != {expected_profile_version}",
            file=sys.stderr,
        )
        sys.exit(1)
    if strategy_version != expected_strategy_version:
        print(
            f"ERROR: Phase 9 strategy_version drift for profile={profile} domain={domain}: {strategy_version} != {expected_strategy_version}",
            file=sys.stderr,
        )
        sys.exit(1)
    if profile:
        seen_profiles.add(profile)

missing = sorted(expected_profiles - seen_profiles)
if missing:
    print("WARN: no recent Phase 9 traffic for profiles: " + ", ".join(missing), file=sys.stderr)

print("OK: Phase 9 timeline profiles and versions are within expected rollout values")
PY

    if [[ -n "${PHASE9_CANARY_DOMAIN}" ]]; then
      phase9_latency_query="max(lifeos:timeline_generation_latency_p95_by_profile:seconds{domain=\"${PHASE9_CANARY_DOMAIN}\"})"
      phase9_insuff_query="max(lifeos:timeline_insufficiency_rate_by_profile:ratio{domain=\"${PHASE9_CANARY_DOMAIN}\"})"
      phase9_blocked_query="max(lifeos:timeline_blocked_claims_rate_by_profile:ratio{domain=\"${PHASE9_CANARY_DOMAIN}\"})"
      phase9_replay_query="max(lifeos:timeline_replay_mismatch_count_by_profile{domain=\"${PHASE9_CANARY_DOMAIN}\"})"
      phase9_latency_json="$(curl -fsS --get --data-urlencode "query=${phase9_latency_query}" "${PROM_URL}/api/v1/query")"
      phase9_insuff_json="$(curl -fsS --get --data-urlencode "query=${phase9_insuff_query}" "${PROM_URL}/api/v1/query")"
      phase9_blocked_json="$(curl -fsS --get --data-urlencode "query=${phase9_blocked_query}" "${PROM_URL}/api/v1/query")"
      phase9_replay_json="$(curl -fsS --get --data-urlencode "query=${phase9_replay_query}" "${PROM_URL}/api/v1/query")"
      PHASE9_LATENCY_JSON="${phase9_latency_json}" \
      PHASE9_INSUFF_JSON="${phase9_insuff_json}" \
      PHASE9_BLOCKED_JSON="${phase9_blocked_json}" \
      PHASE9_REPLAY_JSON="${phase9_replay_json}" \
      PHASE9_CANARY_DOMAIN="${PHASE9_CANARY_DOMAIN}" \
      PHASE9_CANARY_MAX_INSUFFICIENCY_RATE="${PHASE9_CANARY_MAX_INSUFFICIENCY_RATE}" \
      PHASE9_CANARY_MAX_LATENCY_P95="${PHASE9_CANARY_MAX_LATENCY_P95}" \
      PHASE9_CANARY_MAX_BLOCKED_CLAIMS_RATE="${PHASE9_CANARY_MAX_BLOCKED_CLAIMS_RATE}" \
      PHASE9_CANARY_MAX_REPLAY_MISMATCH_COUNT="${PHASE9_CANARY_MAX_REPLAY_MISMATCH_COUNT}" \
      "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys


def _first_value(raw: str) -> float | None:
    payload = json.loads(raw)
    result = payload.get("data", {}).get("result", [])
    if not result:
        return None
    value = result[0].get("value", [None, None])[1]
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


domain = os.environ["PHASE9_CANARY_DOMAIN"]
max_insuff = float(os.environ["PHASE9_CANARY_MAX_INSUFFICIENCY_RATE"])
max_latency = float(os.environ["PHASE9_CANARY_MAX_LATENCY_P95"])
max_blocked = float(os.environ["PHASE9_CANARY_MAX_BLOCKED_CLAIMS_RATE"])
max_replay = float(os.environ["PHASE9_CANARY_MAX_REPLAY_MISMATCH_COUNT"])

latency = _first_value(os.environ["PHASE9_LATENCY_JSON"])
insuff = _first_value(os.environ["PHASE9_INSUFF_JSON"])
blocked = _first_value(os.environ["PHASE9_BLOCKED_JSON"])
replay = _first_value(os.environ["PHASE9_REPLAY_JSON"])

if latency is None and insuff is None and blocked is None and replay is None:
    print(f"WARN: no Phase 9 canary series for domain={domain}; threshold checks skipped", file=sys.stderr)
    sys.exit(0)

if latency is not None and latency > max_latency:
    print(
        f"ERROR: Phase 9 canary domain={domain} latency_p95={latency:.3f} above threshold {max_latency:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)
if insuff is not None and insuff > max_insuff:
    print(
        f"ERROR: Phase 9 canary domain={domain} insufficiency_rate={insuff:.3f} above threshold {max_insuff:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)
if blocked is not None and blocked > max_blocked:
    print(
        f"ERROR: Phase 9 canary domain={domain} blocked_claims_rate={blocked:.3f} above threshold {max_blocked:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)
if replay is not None and replay > max_replay:
    print(
        f"ERROR: Phase 9 canary domain={domain} replay_mismatch_count={replay:.3f} above threshold {max_replay:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"OK: Phase 9 canary thresholds satisfied for domain={domain}")
PY
    fi
  fi

  if [[ "${PHASE10_HUMANIZATION_ENABLED}" == "true" ]]; then
    phase10_query="sum(rate(lifeos_inquiry_humanization_render_by_domain_total[30m])) by (domain, profile, profile_version, strategy, strategy_version, expert_mode)"
    phase10_json="$(curl -fsS --get --data-urlencode "query=${phase10_query}" "${PROM_URL}/api/v1/query")"
    PHASE10_JSON="${phase10_json}" "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["PHASE10_JSON"])
result = payload.get("data", {}).get("result", [])
if not result:
    print("WARN: no Phase 10 humanization render traffic observed yet; profile checks skipped", file=sys.stderr)
    sys.exit(0)
print("OK: Phase 10 humanization render traffic is observable")
PY

    version_query="sum(rate(lifeos_inquiry_humanization_version_total[30m])) by (humanization_version, canonical_version)"
    version_json="$(curl -fsS --get --data-urlencode "query=${version_query}" "${PROM_URL}/api/v1/query")"
    VERSION_JSON="${version_json}" EXPECTED_HUMANIZATION_VERSION="${PHASE10_EXPECT_HUMANIZATION_VERSION}" "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["VERSION_JSON"])
rows = payload.get("data", {}).get("result", [])
expected = os.environ["EXPECTED_HUMANIZATION_VERSION"]

if not rows:
    print("WARN: no Phase 10 version labels observed yet; version drift check skipped", file=sys.stderr)
    sys.exit(0)

observed = sorted({
    str((row.get("metric") or {}).get("humanization_version") or "").strip()
    for row in rows
    if str((row.get("metric") or {}).get("humanization_version") or "").strip()
})
concrete = [value for value in observed if value.lower() not in {"unknown", "unlabeled"}]

if not concrete:
    print("WARN: only placeholder Phase 10 version labels observed; version drift check skipped", file=sys.stderr)
    sys.exit(0)

unexpected = sorted({value for value in concrete if value != expected})
if unexpected:
    print(
        "ERROR: observed unexpected humanization_version label(s): "
        + ", ".join(unexpected)
        + f"; expected={expected}",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"OK: observed Phase 10 humanization_version labels match expected ({expected})")
PY

    if [[ -n "${INQUIRY_JWT}" ]]; then
      humanization_json="$(curl -fsS -H "Authorization: Bearer ${INQUIRY_JWT}" "${BASE_URL}/api/v1/inquiries?limit=20&offset=0")"
      HUMANIZATION_JSON="${humanization_json}" \
      EXPECTED_HUMANIZATION_VERSION="${PHASE10_EXPECT_HUMANIZATION_VERSION}" \
      "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["HUMANIZATION_JSON"])
items = payload.get("items", [])
expected = os.environ["EXPECTED_HUMANIZATION_VERSION"]
observed = []
for item in items:
    latest = item.get("latest_brief") or {}
    brief = latest.get("brief") if isinstance(latest, dict) else None
    if not isinstance(brief, dict):
        continue
    humanized = brief.get("humanized_brief")
    if not isinstance(humanized, dict):
        continue
    metadata = humanized.get("metadata")
    if not isinstance(metadata, dict):
        continue
    version = str(metadata.get("humanization_version") or "").strip()
    if version:
        observed.append(version)

if not observed:
    print("WARN: no humanized_brief metadata found in inquiry list; API shape check skipped", file=sys.stderr)
    sys.exit(0)

unexpected = sorted({value for value in observed if value != expected})
if unexpected:
    print(
        "ERROR: observed unexpected humanized_brief metadata version(s): "
        + ", ".join(unexpected)
        + f"; expected={expected}",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"OK: inquiry list exposes humanized_brief metadata version={expected}")
PY
    fi

    if [[ -n "${PHASE10_CANARY_PROFILE}" ]]; then
      phase10_fallback_query="max(lifeos:inquiry_humanization_fallback_rate_by_domain_profile:ratio{profile=\"${PHASE10_CANARY_PROFILE}\"})"
      phase10_failure_query="max(lifeos:inquiry_humanization_failure_rate_by_domain_profile:ratio{profile=\"${PHASE10_CANARY_PROFILE}\"})"
      phase10_latency_query="max(lifeos:inquiry_humanization_render_latency_p95_by_domain_profile:seconds{profile=\"${PHASE10_CANARY_PROFILE}\"})"
      phase10_equiv_query="max(lifeos:inquiry_humanization_equivalence_violation_count_by_domain_profile{profile=\"${PHASE10_CANARY_PROFILE}\"})"
      phase10_refine_query="max(lifeos:inquiry_refine_after_humanized_view_rate_by_domain_profile:ratio{profile=\"${PHASE10_CANARY_PROFILE}\"})"
      phase10_fallback_json="$(curl -fsS --get --data-urlencode "query=${phase10_fallback_query}" "${PROM_URL}/api/v1/query")"
      phase10_failure_json="$(curl -fsS --get --data-urlencode "query=${phase10_failure_query}" "${PROM_URL}/api/v1/query")"
      phase10_latency_json="$(curl -fsS --get --data-urlencode "query=${phase10_latency_query}" "${PROM_URL}/api/v1/query")"
      phase10_equiv_json="$(curl -fsS --get --data-urlencode "query=${phase10_equiv_query}" "${PROM_URL}/api/v1/query")"
      phase10_refine_json="$(curl -fsS --get --data-urlencode "query=${phase10_refine_query}" "${PROM_URL}/api/v1/query")"
      PHASE10_FALLBACK_JSON="${phase10_fallback_json}" \
      PHASE10_FAILURE_JSON="${phase10_failure_json}" \
      PHASE10_LATENCY_JSON="${phase10_latency_json}" \
      PHASE10_EQUIV_JSON="${phase10_equiv_json}" \
      PHASE10_REFINE_JSON="${phase10_refine_json}" \
      PHASE10_CANARY_PROFILE="${PHASE10_CANARY_PROFILE}" \
      PHASE10_CANARY_MAX_FALLBACK_RATE="${PHASE10_CANARY_MAX_FALLBACK_RATE}" \
      PHASE10_CANARY_MAX_FAILURE_RATE="${PHASE10_CANARY_MAX_FAILURE_RATE}" \
      PHASE10_CANARY_MAX_LATENCY_P95="${PHASE10_CANARY_MAX_LATENCY_P95}" \
      PHASE10_CANARY_MAX_EQUIVALENCE_VIOLATION_COUNT="${PHASE10_CANARY_MAX_EQUIVALENCE_VIOLATION_COUNT}" \
      PHASE10_CANARY_MAX_REFINE_AFTER_VIEW_RATE="${PHASE10_CANARY_MAX_REFINE_AFTER_VIEW_RATE}" \
      "${PYTHON_BIN}" - <<'PY'
import json
import os
import sys


def _first_value(raw: str) -> float | None:
    payload = json.loads(raw)
    result = payload.get("data", {}).get("result", [])
    if not result:
        return None
    value = result[0].get("value", [None, None])[1]
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


profile = os.environ["PHASE10_CANARY_PROFILE"]
max_fallback = float(os.environ["PHASE10_CANARY_MAX_FALLBACK_RATE"])
max_failure = float(os.environ["PHASE10_CANARY_MAX_FAILURE_RATE"])
max_latency = float(os.environ["PHASE10_CANARY_MAX_LATENCY_P95"])
max_equiv = float(os.environ["PHASE10_CANARY_MAX_EQUIVALENCE_VIOLATION_COUNT"])
max_refine = float(os.environ["PHASE10_CANARY_MAX_REFINE_AFTER_VIEW_RATE"])

fallback = _first_value(os.environ["PHASE10_FALLBACK_JSON"])
failure = _first_value(os.environ["PHASE10_FAILURE_JSON"])
latency = _first_value(os.environ["PHASE10_LATENCY_JSON"])
equiv = _first_value(os.environ["PHASE10_EQUIV_JSON"])
refine = _first_value(os.environ["PHASE10_REFINE_JSON"])

if fallback is None and failure is None and latency is None and equiv is None and refine is None:
    print(f"WARN: no Phase 10 canary series for profile={profile}; threshold checks skipped", file=sys.stderr)
    sys.exit(0)

if fallback is not None and fallback > max_fallback:
    print(
        f"ERROR: Phase 10 canary profile={profile} fallback_rate={fallback:.3f} above threshold {max_fallback:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)
if failure is not None and failure > max_failure:
    print(
        f"ERROR: Phase 10 canary profile={profile} failure_rate={failure:.3f} above threshold {max_failure:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)
if latency is not None and latency > max_latency:
    print(
        f"ERROR: Phase 10 canary profile={profile} render_latency_p95={latency:.3f} above threshold {max_latency:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)
if equiv is not None and equiv > max_equiv:
    print(
        f"ERROR: Phase 10 canary profile={profile} equivalence_violation_count={equiv:.3f} above threshold {max_equiv:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)
if refine is not None and refine > max_refine:
    print(
        f"ERROR: Phase 10 canary profile={profile} refine_after_humanized_view_rate={refine:.3f} above threshold {max_refine:.3f}",
        file=sys.stderr,
    )
    sys.exit(1)

print(f"OK: Phase 10 canary thresholds satisfied for profile={profile}")
PY
    fi
  fi
else
  echo "WARN: Prometheus is unreachable at ${PROM_URL}; alert-state check skipped" >&2
fi

echo "Phase 6/6.1/7/7.1/8/8.1/9/10 focused inquiry rollout checks passed"
