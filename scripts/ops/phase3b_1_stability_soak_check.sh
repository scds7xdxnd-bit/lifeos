#!/usr/bin/env bash
set -euo pipefail

# Phase 3b.1 stability soak checks for observability and alert health.
# Validates Phase 3b metrics exist on /metrics and Phase 3b alerts are not firing.

BASE_URL="${BASE_URL:-http://localhost:5001}"
PROM_URL="${PROM_URL:-http://localhost:9090}"

METRICS_ENDPOINT="${BASE_URL}/metrics"

required_metrics=(
  "lifeos_insight_latency_seconds_bucket"
  "lifeos_projection_correctness_total"
  "lifeos_projection_correctness_errors_total"
  "lifeos_replay_determinism_failures_total"
  "lifeos_contract_violations_total"
)

metrics_payload="$(curl -fsS "${METRICS_ENDPOINT}")"

for metric in "${required_metrics[@]}"; do
  if ! grep -q "^${metric}" <<< "${metrics_payload}"; then
    echo "ERROR: missing metric ${metric} from ${METRICS_ENDPOINT}" >&2
    exit 1
  fi
done

echo "OK: Phase 3b metrics present at ${METRICS_ENDPOINT}"

if curl -fsS "${PROM_URL}/api/v1/alerts" >/dev/null; then
  ALERTS_JSON="$(curl -fsS "${PROM_URL}/api/v1/alerts")"
  ALERTS_JSON="${ALERTS_JSON}" python - <<'PY'
import json
import os
import sys

payload = os.environ.get("ALERTS_JSON", "")
data = json.loads(payload)
alerts = data.get("data", {}).get("alerts", [])
firing = []
for alert in alerts:
    labels = alert.get("labels", {})
    if labels.get("phase") == "3b" and alert.get("state") == "firing":
        firing.append(labels.get("alertname") or "unknown")

if firing:
    print("ERROR: Phase 3b alerts firing: " + ", ".join(sorted(set(firing))), file=sys.stderr)
    sys.exit(2)

print("OK: No Phase 3b alerts firing")
PY
else
  echo "WARN: Unable to reach Prometheus at ${PROM_URL}; skipping alert check" >&2
fi
