#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INQUIRY_FEATURE_ENABLED="${INQUIRY_FEATURE_ENABLED:-true}"
INQUIRY_JWT="${INQUIRY_JWT:-}"
EXPECT_MIGRATION_MATCH="${EXPECT_MIGRATION_MATCH:-true}"

required_metrics=(
  "lifeos_inquiry_created_total"
  "lifeos_inquiry_generated_total"
  "lifeos_inquiry_viewed_total"
  "lifeos_inquiry_refined_total"
  "lifeos_inquiry_generation_latency_seconds_bucket"
  "lifeos_inquiry_errors_total"
  "lifeos_inquiry_empty_brief_total"
  "lifeos_inquiry_evidence_coverage_ratio"
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
echo "OK: required Phase 6 inquiry metrics are exposed"

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
    if labels.get("phase") == "6" and alert.get("state") == "firing":
        firing.append(labels.get("alertname") or "unknown")

if firing:
    print("ERROR: Phase 6 inquiry alerts firing: " + ", ".join(sorted(set(firing))), file=sys.stderr)
    sys.exit(1)

print("OK: no Phase 6 inquiry alerts firing")
PY
else
  echo "WARN: Prometheus is unreachable at ${PROM_URL}; alert-state check skipped" >&2
fi

echo "Phase 6 focused inquiry rollout checks passed"
