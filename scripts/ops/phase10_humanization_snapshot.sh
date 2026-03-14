#!/usr/bin/env bash
set -euo pipefail

PROM_URL="${PROM_URL:-http://localhost:9090}"
SNAPSHOT_LABEL="${SNAPSHOT_LABEL:-baseline}"
OUTPUT_PATH="${OUTPUT_PATH:-/tmp/lifeos_phase10_${SNAPSHOT_LABEL}_snapshot.json}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

queries=(
  "lifeos:inquiry_humanization_render_latency_p95:seconds"
  "lifeos:inquiry_humanization_failure_rate:ratio"
  "lifeos:inquiry_humanization_fallback_rate:ratio"
  "lifeos:inquiry_humanization_equivalence_violation_count"
  "lifeos:inquiry_humanized_output_presence_rate:ratio"
  "lifeos:inquiry_technical_brief_expansion_rate:ratio"
  "lifeos:inquiry_refine_after_humanized_view_rate:ratio"
  "lifeos:inquiry_humanization_render_latency_p95_by_domain_profile:seconds"
  "lifeos:inquiry_humanization_failure_rate_by_domain_profile:ratio"
  "lifeos:inquiry_humanization_fallback_rate_by_domain_profile:ratio"
  "lifeos:inquiry_humanization_equivalence_violation_count_by_domain_profile"
  "lifeos:inquiry_humanized_output_presence_rate_by_domain_profile:ratio"
  "lifeos:inquiry_technical_brief_expansion_rate_by_domain_profile:ratio"
  "lifeos:inquiry_refine_after_humanized_view_rate_by_domain_profile:ratio"
  "sum(rate(lifeos_inquiry_humanization_version_total[15m])) by (domain, profile, profile_version, strategy, strategy_version, humanization_version, canonical_version)"
)

snapshots_json="[]"
for query in "${queries[@]}"; do
  query_json="$(curl -fsS --get --data-urlencode "query=${query}" "${PROM_URL}/api/v1/query")"
  snapshots_json="$({ SNAPSHOTS_JSON="${snapshots_json}" QUERY="${query}" QUERY_JSON="${query_json}" "${PYTHON_BIN}" - <<'PY'
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
    "phase": "10",
    "label": os.environ["SNAPSHOT_LABEL"],
    "captured_at": datetime.now(timezone.utc).isoformat(),
    "queries": json.loads(os.environ["SNAPSHOTS_JSON"]),
}
print(json.dumps(payload, indent=2, sort_keys=True))
PY

echo "OK: wrote Phase 10 snapshot to ${OUTPUT_PATH}"
