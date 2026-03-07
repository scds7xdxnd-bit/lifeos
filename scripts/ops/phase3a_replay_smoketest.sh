#!/usr/bin/env bash
set -euo pipefail

# Phase 3a deterministic replay + governance smoke tests.
# Optional: set RUN_INTEGRATION=true to include review queue integration test (requires DB).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

PYTHON_BIN="${PYTHON_BIN:-python}"
PYTEST_BIN="${PYTEST_BIN:-${PYTHON_BIN} -m pytest}"

tests=(
  "lifeos/tests/test_phase_3a_governance.py"
  "lifeos/tests/test_phase_3a_replay_determinism.py"
  "lifeos/tests/test_phase_3a_ml_replay_contracts.py"
  "lifeos/tests/test_phase_3a_projections.py"
)

if [[ "${RUN_INTEGRATION:-false}" == "true" ]]; then
  tests+=("lifeos/tests/test_phase_3a_routing_review_queue.py")
fi

echo "Running Phase 3a replay/governance tests..."
echo "Tests: ${tests[*]}"

${PYTEST_BIN} -q "${tests[@]}"
