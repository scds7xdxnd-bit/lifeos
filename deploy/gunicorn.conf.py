"""
Gunicorn Configuration for LifeOS
Production-grade WSGI server settings with monitoring, logging, and performance tuning.
All configuration driven from environment variables for container deployment.
"""

from __future__ import annotations

import logging
import multiprocessing
import os
from pathlib import Path

# ===== Server Binding & Backlog =====
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
backlog = int(os.environ.get("GUNICORN_BACKLOG", "2048"))

# ===== Worker Settings =====
# gthread worker class: threading-based, ideal for Flask (I/O-bound)
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "gthread")
workers = int(os.environ.get("GUNICORN_WORKERS", str(multiprocessing.cpu_count() * 2 + 1)))
threads = int(os.environ.get("GUNICORN_THREADS", "4"))
worker_connections = int(os.environ.get("GUNICORN_WORKER_CONNECTIONS", "1000"))
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "10000"))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "1000"))
worker_tmp_dir = os.environ.get("GUNICORN_WORKER_TMP_DIR", "/dev/shm")

# ===== Timeout Settings =====
# Request timeout after which worker is killed and restarted
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "60"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# ===== Logging Configuration =====
accesslog = os.environ.get("GUNICORN_ACCESSLOG", "-")  # stdout
errorlog = os.environ.get("GUNICORN_ERRORLOG", "-")    # stderr
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")
capture_output = True

# JSON-structured access log for better parsing in log aggregation
access_log_format = os.environ.get(
    "GUNICORN_ACCESS_LOG_FORMAT",
    '{"timestamp": "%(t)s", "remote": "%(h)s", "request": "%(r)s", '
    '"status": %(s)s, "bytes": %(b)s, "response_time": %(D)s, "pid": %(p)s}',
)

# Load config file if present
logconfig_path = Path(os.environ.get("GUNICORN_LOGCONFIG", "/app/deploy/logging.conf"))
if logconfig_path.exists():
    logconfig = str(logconfig_path)

# ===== Server Mechanics =====
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None
preload_app = os.environ.get("GUNICORN_PRELOAD", "false").lower() in ("1", "true", "yes")

# ===== Security Settings =====
# Limit request size to prevent abuse
limit_request_line = int(os.environ.get("GUNICORN_LIMIT_REQUEST_LINE", "8190"))
limit_request_fields = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELDS", "100"))
limit_request_field_size = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", "8190"))

# ===== Socket Settings =====
reuse_port = True
forwarded_allow_ips = os.environ.get("GUNICORN_FORWARDED_ALLOW_IPS", "*")

# ===== Monitoring & Metrics =====
statsd_host = os.environ.get("STATSD_HOST")
if statsd_host:
    statsd_port = int(os.environ.get("STATSD_PORT", "8125"))
    statsd_prefix = os.environ.get("STATSD_PREFIX", "lifeos")
    statsd_on_error = os.environ.get("STATSD_ON_ERROR", "true").lower() == "true"

# Process naming for monitoring
proc_name = os.environ.get("GUNICORN_PROC_NAME", "lifeos")

# ===== Custom Environment =====
raw_env = [env for env in os.environ.get("GUNICORN_RAW_ENV", "").split(",") if env]

# ===== Lifecycle Hooks =====
def on_starting(server):
    """Called just before the master process is initialized."""
    logger = logging.getLogger(__name__)
    logger.info(
        f"Gunicorn starting: workers={workers}, threads={threads}, "
        f"worker_class={worker_class}, timeout={timeout}s"
    )

def when_ready(server):
    """Called just after the server is started."""
    logger = logging.getLogger(__name__)
    logger.info(f"Gunicorn ready. Listening on {bind}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    logger = logging.getLogger(__name__)
    logger.info("Gunicorn exiting gracefully")

def worker_int(worker):
    """Handle SIGINT on worker."""
    logger = logging.getLogger(__name__)
    logger.info(f"Worker {worker.pid} received interrupt signal")

def worker_abort(worker):
    """Called when a worker is timed out and is being replaced."""
    logger = logging.getLogger(__name__)
    logger.warning(f"Worker {worker.pid} timed out (>{timeout}s), aborting")
