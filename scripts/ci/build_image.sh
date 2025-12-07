#!/usr/bin/env bash
# Purpose: Build Docker image for LifeOS
# Called by: make build-image

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Defaults
IMAGE_NAME="${IMAGE_NAME:-lifeos}"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')}"
DOCKERFILE="${DOCKERFILE:-deploy/Dockerfile}"
BUILD_CONTEXT="${BUILD_CONTEXT:-.}"

echo "=== Building Docker Image ==="
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Dockerfile: ${DOCKERFILE}"
echo "Context: ${BUILD_CONTEXT}"

# Get git info
GIT_SHA=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

docker build \
    --file "$DOCKERFILE" \
    --tag "${IMAGE_NAME}:${IMAGE_TAG}" \
    --tag "${IMAGE_NAME}:latest" \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg GIT_SHA="$GIT_SHA" \
    --build-arg GIT_BRANCH="$GIT_BRANCH" \
    "$BUILD_CONTEXT"

echo ""
echo "✓ Image built successfully"
echo "  - ${IMAGE_NAME}:${IMAGE_TAG}"
echo "  - ${IMAGE_NAME}:latest"
