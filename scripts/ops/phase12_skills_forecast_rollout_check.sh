#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:5001}"
PYTHON_BIN="${PYTHON_BIN:-/Users/ammarhakimi/Dev/finance_app_clean/.venv/bin/python}"

EXPECT_SKILLS_GOALS="${EXPECT_SKILLS_GOALS:-true}"
EXPECT_SKILLS_PATH="${EXPECT_SKILLS_PATH:-true}"
EXPECT_SKILLS_FORECAST="${EXPECT_SKILLS_FORECAST:-false}"
EXPECT_SKILLS_GOALS_STRICT="${EXPECT_SKILLS_GOALS_STRICT:-false}"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "ERROR: Python binary not found or not executable: ${PYTHON_BIN}" >&2
  exit 1
fi

function assert_bool() {
  local name="$1"
  local actual="$2"
  local expected="$3"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "ERROR: ${name} expected=${expected} actual=${actual}" >&2
    exit 1
  fi
  echo "OK: ${name}=${actual}"
}

echo "== Phase 12 Skills Forecast Rollout Check =="
echo "BASE_URL=${BASE_URL}"

echo "-- Health check"
status_code="$(curl -sS -o /dev/null -w "%{http_code}" "${BASE_URL}/health" || true)"
if [[ "${status_code}" != "200" ]]; then
  echo "ERROR: health check failed at ${BASE_URL}/health (status=${status_code})" >&2
  exit 1
fi
echo "OK: health endpoint returned 200"

echo "-- Effective config check"
config_json="$(${PYTHON_BIN} - <<'PY'
import json
from lifeos.config import BaseConfig
print(json.dumps({
    "goals": bool(BaseConfig.ENABLE_PHASE12_SKILLS_GOALS),
    "path": bool(BaseConfig.ENABLE_PHASE12_SKILLS_PATH),
    "forecast": bool(BaseConfig.ENABLE_PHASE12_SKILLS_FORECAST),
    "strict": bool(BaseConfig.ENABLE_PHASE12_SKILLS_GOALS_STRICT),
}))
PY
)"

goals_actual="$(${PYTHON_BIN} - <<PY
import json
print(str(json.loads('''${config_json}''')["goals"]).lower())
PY
)"
path_actual="$(${PYTHON_BIN} - <<PY
import json
print(str(json.loads('''${config_json}''')["path"]).lower())
PY
)"
forecast_actual="$(${PYTHON_BIN} - <<PY
import json
print(str(json.loads('''${config_json}''')["forecast"]).lower())
PY
)"
strict_actual="$(${PYTHON_BIN} - <<PY
import json
print(str(json.loads('''${config_json}''')["strict"]).lower())
PY
)"

assert_bool "ENABLE_PHASE12_SKILLS_GOALS" "${goals_actual}" "${EXPECT_SKILLS_GOALS}"
assert_bool "ENABLE_PHASE12_SKILLS_PATH" "${path_actual}" "${EXPECT_SKILLS_PATH}"
assert_bool "ENABLE_PHASE12_SKILLS_FORECAST" "${forecast_actual}" "${EXPECT_SKILLS_FORECAST}"
assert_bool "ENABLE_PHASE12_SKILLS_GOALS_STRICT" "${strict_actual}" "${EXPECT_SKILLS_GOALS_STRICT}"

echo "-- Guidance"
if [[ "${forecast_actual}" == "true" ]]; then
  echo "Forecast is ENABLED: verify Skills cards render forecast panel and monitor 5xx/latency."
else
  echo "Forecast is DISABLED: system is in safe fallback mode."
fi

echo "PASS: Phase 12 skills forecast rollout checks completed"
