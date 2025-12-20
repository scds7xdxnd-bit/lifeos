"""Prometheus metrics endpoint."""

from __future__ import annotations

from flask import Blueprint, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from lifeos.core.observability import metrics  # noqa: F401

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.get("/metrics")
def metrics_endpoint() -> Response:
    payload = generate_latest()
    return Response(payload, mimetype=CONTENT_TYPE_LATEST)
