#!/usr/bin/env bash
set -euo pipefail

PROM_URL="${PROM_URL:-http://localhost:9090}"
SNAPSHOT_LABEL="${SNAPSHOT_LABEL:-baseline}"
OUTPUT_PATH="${OUTPUT_PATH:-/tmp/lifeos_phase8_1_${SNAPSHOT_LABEL}_snapshot.json}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

queries=(
  "lifeos:inquiry_direct_answer_presence_rate:ratio"
  "lifeos:inquiry_weak_answer_rate:ratio"
  "lifeos:inquiry_limitation_redundancy_rate:ratio"
  "lifeos:inquiry_refine_after_weak_answer_lift:ratio"
  "lifeos:inquiry_productization_latency_p95:seconds"
  "lifeos:inquiry_productization_error_rate:ratio"
  "lifeos:inquiry_productization_replay_mismatch_count"
  "sum(rate(lifeos_inquiry_productization_by_domain_total[15m])) by (domain, profile, profile_version, strategy_version)"
  "lifeos:inquiry_direct_answer_presence_rate_by_domain_profile:ratio"
  "lifeos:inquiry_weak_answer_rate_by_domain_profile:ratio"
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
    "phase": "8.1",
    "label": os.environ["SNAPSHOT_LABEL"],
    "captured_at": datetime.now(timezone.utc).isoformat(),
    "queries": json.loads(os.environ["SNAPSHOTS_JSON"]),
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY

echo "OK: wrote Phase 8.1 snapshot to ${OUTPUT_PATH}"
