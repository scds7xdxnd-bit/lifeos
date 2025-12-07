# syntax=docker/dockerfile:1
# Multi-stage build for LifeOS Flask application
# Stage 1: Builder - compiles dependencies
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=on \
    FLASK_APP=lifeos.wsgi \
    APP_ENV=production

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies to wheel format
COPY lifeos/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r /tmp/requirements.txt

# Stage 2: Runtime - minimal production image
FROM python:3.11-slim AS runtime

# Security: Run as non-root user
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* && \
    addgroup --system lifeos && \
    adduser --system --ingroup lifeos --home /app lifeos

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=lifeos.wsgi \
    APP_ENV=production \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy wheels from builder and install
COPY --from=builder /app/wheels /tmp/wheels
RUN pip install --upgrade pip && \
    pip install --no-cache /tmp/wheels/* && \
    rm -rf /tmp/wheels

# Copy application code
COPY --chown=lifeos:lifeos lifeos /app/lifeos
COPY --chown=lifeos:lifeos flask_app /app/flask_app
COPY --chown=lifeos:lifeos migrations /app/migrations
COPY --chown=lifeos:lifeos alembic.ini /app/alembic.ini
COPY --chown=lifeos:lifeos deploy /app/deploy

# Prepare application directories
RUN chmod +x /app/deploy/scripts/*.sh && \
    mkdir -p /app/instance/uploads /app/instance/backups /app/logs && \
    chown -R lifeos:lifeos /app && \
    chmod 750 /app/logs /app/instance

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=5 --start-period=20s \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Switch to non-root user
USER lifeos

# Metadata
LABEL maintainer="LifeOS DevOps" \
      description="LifeOS Flask application with event-driven architecture" \
      version="1.0.0"

EXPOSE 8000

ENTRYPOINT ["/app/deploy/scripts/entrypoint.sh"]
CMD ["gunicorn", "-c", "/app/deploy/gunicorn.conf.py", "lifeos.wsgi:app"]
