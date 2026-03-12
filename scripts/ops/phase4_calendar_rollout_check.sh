#!/usr/bin/env bash
set -euo pipefail

# Phase 4 calendar rollout check: verify metrics exposure and no Phase 3b alerts firing.

BASE_URL="${BASE_URL:-http://localhost:8000}"
PROM_URL="${PROM_URL:-http://localhost:9090}"
PYTHON_BIN="${PYTHON_BIN:-}"

required_metrics=(
  "lifeos_insight_latency_seconds_bucket"
  "lifeos_read_cache_hits_total"
  "lifeos_read_cache_misses_total"
)

if [[ -z "${PYTHON_BIN}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "ERROR: python not found. Set PYTHON_BIN to your venv python." >&2
    exit 1
  fi
elif ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "ERROR: PYTHON_BIN '${PYTHON_BIN}' not found in PATH." >&2
  exit 1
fi

metrics_payload="$(curl -fsS "${BASE_URL}/metrics")"
for metric in "${required_metrics[@]}"; do
  if ! grep -q "^${metric}" <<< "${metrics_payload}"; then
    echo "ERROR: missing metric ${metric} from ${BASE_URL}/metrics" >&2
    exit 1
  fi
done

echo "OK: metrics exposed at ${BASE_URL}/metrics"

alerts_json="$(curl -fsS "${PROM_URL}/api/v1/alerts")"
ALERTS_JSON="${alerts_json}" "${PYTHON_BIN}" - <<'PY'
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

print("OK: no Phase 3b alerts firing")
PY
