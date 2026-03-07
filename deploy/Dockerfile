# Multi-stage build for LifeOS Flask application
# Stage 1: Builder - compiles dependencies
FROM python:3.11-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=on \
    FLASK_APP=lifeos.wsgi \
    APP_ENV=production

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_BINARY=:none:

RUN python - <<'EOF'
import socket
socket.setdefaulttimeout(120)
EOF

WORKDIR /app

# Install build dependencies
RUN printf 'Acquire::ForceIPv4 "true";\n' > /etc/apt/apt.conf.d/99force-ipv4 \
 && sed -i 's|http://deb.debian.org/debian|https://mirror.sg.gs/debian|g' /etc/apt/sources.list.d/debian.sources \
 && sed -i 's|http://security.debian.org/debian-security|https://mirror.sg.gs/debian-security|g' /etc/apt/sources.list.d/debian.sources \
 && apt-get update -o Acquire::Retries=10 \
 && apt-get install -y --no-install-recommends build-essential libpq-dev git \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies to wheel format
COPY lifeos/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools \
    && pip wheel \
    --no-cache-dir \
    --no-build-isolation \
    --wheel-dir /app/wheels \
    -r /tmp/requirements.txt

# Stage 2: Runtime - minimal production image
FROM python:3.11-slim-bookworm AS runtime

# Security: Run as non-root user
RUN printf 'Acquire::ForceIPv4 "true";\n' > /etc/apt/apt.conf.d/99force-ipv4 \
 && sed -i 's|http://deb.debian.org/debian|https://mirror.sg.gs/debian|g' /etc/apt/sources.list.d/debian.sources \
 && sed -i 's|http://security.debian.org/debian-security|https://mirror.sg.gs/debian-security|g' /etc/apt/sources.list.d/debian.sources \
 && apt-get update -o Acquire::Retries=10 \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    libpq5 \
 && rm -rf /var/lib/apt/lists/* \
 && addgroup --system lifeos \
 && adduser --system --ingroup lifeos --home /app lifeos

ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_BINARY=:none:

RUN python - <<'EOF'
import socket
socket.setdefaulttimeout(120)
EOF

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=lifeos.wsgi \
    APP_ENV=production \
    MLSUGGESTER_MODEL_DIR=/app/lifeos/ml_assets \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy wheels from builder and install
COPY --from=builder /app/wheels /tmp/wheels
COPY lifeos/requirements.txt /tmp/requirements.txt
RUN pip install --no-index --find-links=/tmp/wheels -r /tmp/requirements.txt && \
    rm -rf /tmp/wheels

# Copy application code
COPY --chown=lifeos:lifeos lifeos /app/lifeos
COPY --chown=lifeos:lifeos migrations /app/migrations
COPY --chown=lifeos:lifeos alembic.ini /app/alembic.ini
COPY --chown=lifeos:lifeos deploy /app/deploy
COPY --chown=lifeos:lifeos scripts /app/scripts

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
