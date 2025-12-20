#!/usr/bin/env bash
set -euo pipefail

# Fetch the debug-only insight telemetry snapshot and validate key fields.
# Requires an admin Bearer token and non-production environment (endpoint disabled in prod).

BASE_URL="${BASE_URL:-http://localhost:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"
MAX_AVG_LATENCY_MS="${MAX_AVG_LATENCY_MS:-1000}"

if [[ -z "${AUTH_TOKEN}" ]]; then
  echo "ERROR: AUTH_TOKEN is required (admin Bearer token)." >&2
  exit 1
fi

resp="$(curl -sS -H "Authorization: Bearer ${AUTH_TOKEN}" -w '\n%{http_code}' \
  "${BASE_URL}/admin/debug/insight-telemetry")"

code="${resp##*$'\n'}"
body="${resp%$'\n'*}"

if [[ "${code}" != "200" ]]; then
  echo "ERROR: telemetry endpoint returned status ${code}" >&2
  echo "${body}" >&2
  exit 1
fi

TELEMETRY_JSON="${body}" python -c '
import json
import os
import sys

payload = os.environ.get("TELEMETRY_JSON", "")
try:
    data = json.loads(payload)
except json.JSONDecodeError as exc:
    print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
    sys.exit(1)

telemetry = data.get("telemetry") or {}
required = [
    "events_processed",
    "events_with_insights",
    "total_insights",
    "per_rule_counts",
    "avg_latency_ms",
    "per_rule_avg_latency_ms",
    "false_positives",
    "false_negatives",
    "coverage",
    "per_event_counts",
    "recent_events",
]
missing = [key for key in required if key not in telemetry]
if missing:
    print(f"ERROR: missing telemetry fields: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

avg_latency = float(telemetry.get("avg_latency_ms") or 0.0)
threshold = float(os.environ.get("MAX_AVG_LATENCY_MS", "1000"))
if avg_latency > threshold:
    print(f"ERROR: avg_latency_ms {avg_latency} exceeds threshold {threshold}", file=sys.stderr)
    sys.exit(2)

print("OK: telemetry snapshot")
print(f"  events_processed: {telemetry['events_processed']}")
print(f"  events_with_insights: {telemetry['events_with_insights']}")
print(f"  total_insights: {telemetry['total_insights']}")
print(f"  avg_latency_ms: {avg_latency}")
print(f"  recent_events: {len(telemetry['recent_events'])}")
'
