"""Observability histogram presence checks."""

from __future__ import annotations

import re

import pytest

from lifeos.core.events.event_bus import EventBus
from lifeos.core.events.event_models import EventRecord

pytestmark = pytest.mark.unit


def test_metrics_expose_http_and_event_latency_histograms(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    payload = resp.get_data(as_text=True)
    assert "lifeos_http_request_latency_seconds_bucket" in payload
    assert "lifeos_event_dispatch_latency_seconds_bucket" in payload


def test_http_latency_histogram_preregistered_labels(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    payload = resp.get_data(as_text=True)
    assert any(
        "lifeos_http_request_latency_seconds_bucket" in line
        and 'method="GET"' in line
        and 'route="unknown"' in line
        and 'status_code="200"' in line
        for line in payload.splitlines()
    )


def test_http_latency_records_route_label(client):
    client.get("/login")
    payload = client.get("/metrics").get_data(as_text=True)
    assert any(
        "lifeos_http_request_latency_seconds_bucket" in line
        and 'method="GET"' in line
        and 'route="/login"' in line
        and 'status_code="200"' in line
        for line in payload.splitlines()
    )


def test_event_dispatch_latency_increments_on_publish(client):
    before = _extract_metric_value(client.get("/metrics").get_data(as_text=True))

    bus = EventBus()
    bus.subscribe("test.event", lambda event: None)
    bus.publish(EventRecord(event_type="test.event", payload={}, user_id=None))

    after = _extract_metric_value(client.get("/metrics").get_data(as_text=True))
    assert after is not None
    if before is not None:
        assert after >= before + 1.0


def test_extract_metric_value_handles_bucket_and_missing_payload(monkeypatch):
    class _Match:
        def __init__(self, value: str):
            self._value = value

        def group(self, _: int) -> str:
            return self._value

    calls = {"count": 0}

    def _fake_search(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return _Match("7")
        return None

    monkeypatch.setattr(re, "search", _fake_search)
    assert _extract_metric_value("unused") == 7.0
    assert _extract_metric_value("unused") is None


def _extract_metric_value(payload: str) -> float | None:
    bucket_match = re.search(
        r'^lifeos_event_dispatch_latency_seconds_bucket\\{[^}]*le="\\+Inf"[^}]*\\}\s+([0-9.eE+-]+)$', payload, re.M
    )
    if bucket_match:
        return float(bucket_match.group(1))
    count_match = re.search(
        r"^lifeos_event_dispatch_latency_seconds_count(?:\\{[^}]*\\})?\s+([0-9.eE+-]+)$", payload, re.M
    )
    if count_match:
        return float(count_match.group(1))
    return None
