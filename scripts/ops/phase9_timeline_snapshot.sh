#!/usr/bin/env bash
set -euo pipefail

PROM_URL="${PROM_URL:-http://localhost:9090}"
SNAPSHOT_LABEL="${SNAPSHOT_LABEL:-baseline}"
OUTPUT_PATH="${OUTPUT_PATH:-/tmp/lifeos_phase9_${SNAPSHOT_LABEL}_snapshot.json}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PHASE9_DOMAIN_REGEX="${PHASE9_DOMAIN_REGEX:-finance|habits|projects|skills|calendar|finance\\+habits|projects\\+skills|calendar\\+projects}"

queries=(
  "lifeos:timeline_output_presence_rate:ratio"
  "lifeos:timeline_output_presence_rate_by_domain:ratio{domain=~\"${PHASE9_DOMAIN_REGEX}\"}"
  "lifeos:timeline_generation_latency_p95_by_profile:seconds{domain=~\"${PHASE9_DOMAIN_REGEX}\"}"
  "lifeos:timeline_error_rate_by_profile:ratio{domain=~\"${PHASE9_DOMAIN_REGEX}\"}"
  "lifeos:timeline_insufficiency_rate_by_profile:ratio{domain=~\"${PHASE9_DOMAIN_REGEX}\"}"
  "lifeos:timeline_baseline_coverage_avg_windows_by_profile{domain=~\"${PHASE9_DOMAIN_REGEX}\"}"
  "lifeos:timeline_blocked_claims_rate_by_profile:ratio{domain=~\"${PHASE9_DOMAIN_REGEX}\"}"
  "lifeos:timeline_replay_mismatch_count_by_profile{domain=~\"${PHASE9_DOMAIN_REGEX}\"}"
  "sum(rate(lifeos_timeline_profile_usage_total{domain=~\"${PHASE9_DOMAIN_REGEX}\"}[15m])) by (domain, profile, profile_version, strategy, strategy_version)"
  "sum(rate(lifeos_timeline_insufficiency_total{domain=~\"${PHASE9_DOMAIN_REGEX}\"}[15m])) by (domain, profile, profile_version)"
)

snapshots_json="[]"
for query in "${queries[@]}"; do
  query_json="$(curl -fsS --get --data-urlencode "query=${query}" "${PROM_URL}/api/v1/query")"
  snapshots_json="$(
    SNAPSHOTS_JSON="${snapshots_json}" QUERY="${query}" QUERY_JSON="${query_json}" "${PYTHON_BIN}" - <<'PY'
import json
import os

snapshots = json.loads(os.environ["SNAPSHOTS_JSON"])
query = os.environ["QUERY"]
payload = json.loads(os.environ["QUERY_JSON"])
snapshots.append({"query": query, "result": payload.get("data", {}).get("result", [])})
print(json.dumps(snapshots, separators=(",", ":")))
PY
  )"
done

SNAPSHOT_LABEL="${SNAPSHOT_LABEL}" SNAPSHOTS_JSON="${snapshots_json}" "${PYTHON_BIN}" - <<'PY' > "${OUTPUT_PATH}"
import json
import os
from datetime import datetime, timezone

payload = {
    "phase": "9",
    "label": os.environ["SNAPSHOT_LABEL"],
    "captured_at": datetime.now(timezone.utc).isoformat(),
    "queries": json.loads(os.environ["SNAPSHOTS_JSON"]),
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY

echo "OK: wrote Phase 9 snapshot to ${OUTPUT_PATH}"
