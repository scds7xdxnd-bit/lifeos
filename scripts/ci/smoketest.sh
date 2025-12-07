#!/usr/bin/env bash
# Purpose: Post-deploy smoke test
# Called by: make smoketest

set -euo pipefail

TARGET_URL="${TARGET_URL:-http://localhost:5000}"
MAX_RETRIES="${MAX_RETRIES:-30}"
RETRY_DELAY="${RETRY_DELAY:-2}"

echo "=== Running Smoke Tests against $TARGET_URL ==="

# Wait for service to be ready
echo "Waiting for service to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf "${TARGET_URL}/health" > /dev/null 2>&1; then
        echo "Service is ready!"
        break
    fi
    if [ "$i" -eq "$MAX_RETRIES" ]; then
        echo "❌ ERROR: Service did not become ready in time"
        exit 1
    fi
    echo "Attempt $i/$MAX_RETRIES - waiting ${RETRY_DELAY}s..."
    sleep "$RETRY_DELAY"
done

# Health endpoint
echo ""
echo "Testing /health endpoint..."
HEALTH=$(curl -sf "${TARGET_URL}/health" || echo "")
if echo "$HEALTH" | grep -qE "ok|healthy|status"; then
    echo "✓ Health check passed"
    echo "Response: $HEALTH"
else
    echo "❌ Health check failed"
    echo "Response: $HEALTH"
    exit 1
fi

# Readiness endpoint (if available)
echo ""
echo "Testing /ready endpoint (if available)..."
READY=$(curl -sf "${TARGET_URL}/ready" 2>/dev/null || echo "")
if [ -n "$READY" ]; then
    echo "✓ Readiness check passed"
    echo "Response: $READY"
else
    echo "(Readiness endpoint not available, skipping)"
fi

# Basic API endpoint (if auth not required)
echo ""
echo "Testing /api/v1/ping (if available)..."
PING=$(curl -sf "${TARGET_URL}/api/v1/ping" 2>/dev/null || echo "")
if [ -n "$PING" ]; then
    echo "✓ Ping check passed"
else
    echo "(Ping endpoint not available or requires auth, skipping)"
fi

echo ""
echo "✓ Smoke tests passed"
