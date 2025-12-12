import multiprocessing
import os

bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
workers = int(
    os.environ.get("GUNICORN_WORKERS", str(multiprocessing.cpu_count() * 2 + 1))
)
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "30"))
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "gthread")
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")
