#!/usr/bin/env bash
set -euo pipefail

PROM_URL="${PROM_URL:-http://localhost:9090}"
SNAPSHOT_LABEL="${SNAPSHOT_LABEL:-alpha-snapshot}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

queries=(
  "lifeos_private_alpha_active_users"
  "lifeos_private_alpha_user_cap"
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

echo "snapshot=${SNAPSHOT_LABEL}"
for query in "${queries[@]}"; do
  query_json="$(curl -fsS --get --data-urlencode "query=${query}" "${PROM_URL}/api/v1/query")"
  QUERY_JSON="${query_json}" QUERY_NAME="${query}" "${PYTHON_BIN}" - <<'PY'
import json
import os

payload = json.loads(os.environ["QUERY_JSON"])
query = os.environ["QUERY_NAME"]
rows = payload.get("data", {}).get("result", [])
if not rows:
    print(f"{query}=<no-data>")
else:
    for row in rows:
        metric = row.get("metric", {})
        value = row.get("value", [None, ""])[1]
        labels = ",".join(f"{k}={v}" for k, v in sorted(metric.items()) if k != "__name__")
        label_text = f"{{{labels}}}" if labels else ""
        print(f"{query}{label_text}={value}")
PY
done
