#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
EXPECT_MIGRATION_MATCH="${EXPECT_MIGRATION_MATCH:-true}"

PRIVATE_ALPHA_ENABLED="${PRIVATE_ALPHA_ENABLED:-true}"
ALPHA_EXPECT_INVITE_ONLY="${ALPHA_EXPECT_INVITE_ONLY:-true}"
ALPHA_EXPECT_MAX_USERS="${ALPHA_EXPECT_MAX_USERS:-30}"
ALPHA_EXPECT_VISIBLE_DOMAINS="${ALPHA_EXPECT_VISIBLE_DOMAINS:-calendar,habits,projects,skills}"
ALPHA_EXPECT_PAIR_PROFILES="${ALPHA_EXPECT_PAIR_PROFILES:-projects_calendar_v1,projects_skills_v1}"
ALPHA_EXPECT_TECHNICAL_BRIEF="${ALPHA_EXPECT_TECHNICAL_BRIEF:-true}"
ALPHA_EXPECT_HISTORY="${ALPHA_EXPECT_HISTORY:-true}"
ALPHA_EXPECT_INQUIRY_FEEDBACK="${ALPHA_EXPECT_INQUIRY_FEEDBACK:-true}"
ALPHA_EXPECT_HIDE_DOMAIN_CRUD="${ALPHA_EXPECT_HIDE_DOMAIN_CRUD:-true}"
ALPHA_EXPECT_REQUIRE_DATA_READINESS="${ALPHA_EXPECT_REQUIRE_DATA_READINESS:-true}"
ALPHA_EXPECT_CALENDAR_SYNC="${ALPHA_EXPECT_CALENDAR_SYNC:-true}"

INQUIRY_FEATURE_ENABLED="${INQUIRY_FEATURE_ENABLED:-true}"
PHASE8_CROSS_DOMAIN_ENABLED="${PHASE8_CROSS_DOMAIN_ENABLED:-true}"
PHASE8_PAIR_PROFILES="${PHASE8_PAIR_PROFILES:-projects_calendar_v1,projects_skills_v1}"
PHASE8_EXPECT_PROFILE_VERSION="${PHASE8_EXPECT_PROFILE_VERSION:-1.0.0}"
PHASE8_EXPECT_STRATEGY_VERSION="${PHASE8_EXPECT_STRATEGY_VERSION:-1.0.0}"
PHASE8_1_PRODUCTIZATION_ENABLED="${PHASE8_1_PRODUCTIZATION_ENABLED:-true}"
PHASE8_1_EXPECT_PRODUCTIZATION_VERSION="${PHASE8_1_EXPECT_PRODUCTIZATION_VERSION:-phase8_1_productization_v1}"
PHASE9_TIMELINE_ENABLED="${PHASE9_TIMELINE_ENABLED:-true}"
PHASE9_FIRST_WAVE_DOMAINS="${PHASE9_FIRST_WAVE_DOMAINS:-calendar,habits,projects,skills}"
PHASE9_APPROVED_PAIR_DOMAINS="${PHASE9_APPROVED_PAIR_DOMAINS:-calendar+projects,projects+skills}"
PHASE9_EXPECTED_PROFILES="${PHASE9_EXPECTED_PROFILES:-calendar_timeline_v1,habits_timeline_v1,projects_timeline_v1,skills_timeline_v1,projects_calendar_timeline_v1,projects_skills_timeline_v1}"
PHASE9_EXPECT_PROFILE_VERSION="${PHASE9_EXPECT_PROFILE_VERSION:-1.0.0}"
PHASE9_EXPECT_STRATEGY_VERSION="${PHASE9_EXPECT_STRATEGY_VERSION:-1.0.0}"
PHASE10_HUMANIZATION_ENABLED="${PHASE10_HUMANIZATION_ENABLED:-true}"
PHASE10_EXPECT_HUMANIZATION_VERSION="${PHASE10_EXPECT_HUMANIZATION_VERSION:-phase10_humanization_v1}"

BASE_URL="${BASE_URL}" \
PROM_URL="${PROM_URL}" \
INQUIRY_FEATURE_ENABLED="${INQUIRY_FEATURE_ENABLED}" \
EXPECT_MIGRATION_MATCH="${EXPECT_MIGRATION_MATCH}" \
PHASE8_CROSS_DOMAIN_ENABLED="${PHASE8_CROSS_DOMAIN_ENABLED}" \
PHASE8_PAIR_PROFILES="${PHASE8_PAIR_PROFILES}" \
PHASE8_EXPECT_PROFILE_VERSION="${PHASE8_EXPECT_PROFILE_VERSION}" \
PHASE8_EXPECT_STRATEGY_VERSION="${PHASE8_EXPECT_STRATEGY_VERSION}" \
PHASE8_1_PRODUCTIZATION_ENABLED="${PHASE8_1_PRODUCTIZATION_ENABLED}" \
PHASE8_1_EXPECT_PRODUCTIZATION_VERSION="${PHASE8_1_EXPECT_PRODUCTIZATION_VERSION}" \
PHASE9_TIMELINE_ENABLED="${PHASE9_TIMELINE_ENABLED}" \
PHASE9_FIRST_WAVE_DOMAINS="${PHASE9_FIRST_WAVE_DOMAINS}" \
PHASE9_APPROVED_PAIR_DOMAINS="${PHASE9_APPROVED_PAIR_DOMAINS}" \
PHASE9_EXPECTED_PROFILES="${PHASE9_EXPECTED_PROFILES}" \
PHASE9_EXPECT_PROFILE_VERSION="${PHASE9_EXPECT_PROFILE_VERSION}" \
PHASE9_EXPECT_STRATEGY_VERSION="${PHASE9_EXPECT_STRATEGY_VERSION}" \
PHASE10_HUMANIZATION_ENABLED="${PHASE10_HUMANIZATION_ENABLED}" \
PHASE10_EXPECT_HUMANIZATION_VERSION="${PHASE10_EXPECT_HUMANIZATION_VERSION}" \
bash scripts/ops/phase10_humanization_rollout_check.sh

bootstrap_json="$(curl -fsS "${BASE_URL}/api/bootstrap")"
BOOTSTRAP_JSON="${bootstrap_json}" \
PRIVATE_ALPHA_ENABLED="${PRIVATE_ALPHA_ENABLED}" \
ALPHA_EXPECT_INVITE_ONLY="${ALPHA_EXPECT_INVITE_ONLY}" \
ALPHA_EXPECT_MAX_USERS="${ALPHA_EXPECT_MAX_USERS}" \
ALPHA_EXPECT_VISIBLE_DOMAINS="${ALPHA_EXPECT_VISIBLE_DOMAINS}" \
ALPHA_EXPECT_PAIR_PROFILES="${ALPHA_EXPECT_PAIR_PROFILES}" \
ALPHA_EXPECT_TECHNICAL_BRIEF="${ALPHA_EXPECT_TECHNICAL_BRIEF}" \
ALPHA_EXPECT_HISTORY="${ALPHA_EXPECT_HISTORY}" \
ALPHA_EXPECT_INQUIRY_FEEDBACK="${ALPHA_EXPECT_INQUIRY_FEEDBACK}" \
ALPHA_EXPECT_HIDE_DOMAIN_CRUD="${ALPHA_EXPECT_HIDE_DOMAIN_CRUD}" \
ALPHA_EXPECT_REQUIRE_DATA_READINESS="${ALPHA_EXPECT_REQUIRE_DATA_READINESS}" \
ALPHA_EXPECT_CALENDAR_SYNC="${ALPHA_EXPECT_CALENDAR_SYNC}" \
"${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["BOOTSTRAP_JSON"])
alpha = payload.get("private_alpha") or {}


def _truthy(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _as_set(raw: str) -> set[str]:
    return {item.strip() for item in str(raw or "").split(",") if item.strip()}

if bool(alpha.get("enabled")) != _truthy(os.environ["PRIVATE_ALPHA_ENABLED"]):
    print("ERROR: bootstrap private_alpha.enabled does not match expected rollout state", file=sys.stderr)
    sys.exit(1)
if bool(alpha.get("invite_only")) != _truthy(os.environ["ALPHA_EXPECT_INVITE_ONLY"]):
    print("ERROR: bootstrap private_alpha.invite_only mismatch", file=sys.stderr)
    sys.exit(1)
if int(alpha.get("max_users") or 0) != int(os.environ["ALPHA_EXPECT_MAX_USERS"]):
    print("ERROR: bootstrap private_alpha.max_users mismatch", file=sys.stderr)
    sys.exit(1)

visible_expected = _as_set(os.environ["ALPHA_EXPECT_VISIBLE_DOMAINS"])
visible_observed = {str(item) for item in (alpha.get("visible_domains") or [])}
if visible_expected != visible_observed:
    print(
        "ERROR: bootstrap private_alpha.visible_domains mismatch: "
        f"observed={sorted(visible_observed)} expected={sorted(visible_expected)}",
        file=sys.stderr,
    )
    sys.exit(1)

pairs_expected = _as_set(os.environ["ALPHA_EXPECT_PAIR_PROFILES"])
pairs_observed = {str(item) for item in (alpha.get("enabled_pair_profiles") or [])}
if pairs_expected != pairs_observed:
    print(
        "ERROR: bootstrap private_alpha.enabled_pair_profiles mismatch: "
        f"observed={sorted(pairs_observed)} expected={sorted(pairs_expected)}",
        file=sys.stderr,
    )
    sys.exit(1)

truth_checks = {
    "technical_brief_enabled": "ALPHA_EXPECT_TECHNICAL_BRIEF",
    "history_enabled": "ALPHA_EXPECT_HISTORY",
    "inquiry_feedback_enabled": "ALPHA_EXPECT_INQUIRY_FEEDBACK",
    "hide_domain_crud": "ALPHA_EXPECT_HIDE_DOMAIN_CRUD",
    "require_data_readiness": "ALPHA_EXPECT_REQUIRE_DATA_READINESS",
    "calendar_sync_enabled": "ALPHA_EXPECT_CALENDAR_SYNC",
}
for key, env_name in truth_checks.items():
    if bool(alpha.get(key)) != _truthy(os.environ[env_name]):
        print(f"ERROR: bootstrap private_alpha.{key} mismatch", file=sys.stderr)
        sys.exit(1)

print("OK: /api/bootstrap private-alpha flag state matches rollout expectations")
PY

metrics_payload="$(curl -fsS "${BASE_URL}/metrics")"
required_metrics=(
  "lifeos_private_alpha_active_users"
  "lifeos_private_alpha_user_cap"
  "lifeos_private_alpha_user_cap_utilization_ratio"
  "lifeos_private_alpha_enabled"
  "lifeos_private_alpha_invites_issued_total"
  "lifeos_private_alpha_invites_accepted_total"
  "lifeos_private_alpha_invites_rejected_total"
  "lifeos_private_alpha_readiness_evaluated_total"
  "lifeos_private_alpha_readiness_blocked_total"
  "lifeos_inquiry_feedback_submitted_total"
  "lifeos_inquiry_feedback_submitted_by_domain_total"
)
for metric in "${required_metrics[@]}"; do
  if ! grep -q "^${metric}" <<< "${metrics_payload}"; then
    echo "ERROR: missing private-alpha metric ${metric}" >&2
    exit 1
  fi
done
echo "OK: private-alpha metrics are exposed"

if ! grep -q 'lifeos_inquiry_humanization_fallback_total{reason="feature_disabled"' <<< "${metrics_payload}"; then
  echo "ERROR: expected feature-disabled humanization fallback series missing (rollback signal unavailable)" >&2
  exit 1
fi
echo "OK: rollback fallback metric series is exposed"

if curl -fsS "${PROM_URL}/api/v1/alerts" >/dev/null 2>&1; then
  required_recordings=(
    "lifeos:private_alpha_active_user_cap_utilization:ratio"
    "lifeos:private_alpha_invite_acceptance_rate:ratio"
    "lifeos:private_alpha_invite_rejection_rate:ratio"
    "lifeos:private_alpha_readiness_completion_rate:ratio"
    "lifeos:private_alpha_readiness_blocked_rate:ratio"
    "lifeos:private_alpha_feedback_submission_rate:per_second"
    "lifeos:private_alpha_inquiry_failure_rate:ratio"
    "lifeos:private_alpha_inquiry_latency_p95:seconds"
    "lifeos:private_alpha_humanization_fallback_rate:ratio"
    "lifeos:private_alpha_technical_brief_expansion_rate:ratio"
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
    print("ERROR: invalid Prometheus query payload", file=sys.stderr)
    sys.exit(1)
PY
  done
  echo "OK: private-alpha recording rules are queryable"

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
    if str(labels.get("phase") or "") == "alpha" and alert.get("state") == "firing":
        firing.append(labels.get("alertname") or "unknown")
if firing:
    print("ERROR: private-alpha alerts are firing: " + ", ".join(sorted(set(firing))), file=sys.stderr)
    sys.exit(1)
print("OK: no private-alpha alerts are firing")
PY
else
  echo "WARN: Prometheus not reachable at ${PROM_URL}; recording/alert checks skipped" >&2
fi

echo "PASS: private-alpha strict rollout gate checks completed"
