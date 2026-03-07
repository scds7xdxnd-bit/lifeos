# Observability Completion - HTTP & Event Latency (DevOps)

**Audience:** DevOps, QA
**Scope:** Dashboard wiring and verification only. No code changes.

## Goals
- Confirm `/metrics` exposes:
  - `lifeos_http_request_latency_seconds_bucket`
  - `lifeos_event_dispatch_latency_seconds_bucket`
- Ensure Prometheus returns non-NaN histogram quantiles after traffic.

## Grafana
Dashboard: `deploy/monitoring/grafana/provisioning/dashboards/lifeos-dashboard.json`

Panels added:
- HTTP Request Latency (LifeOS p50/p95/p99)
- Event Dispatch Latency (p50/p95/p99)

## Verification
1) Generate traffic (any normal UI/API usage).
2) Run in Prometheus:
```
histogram_quantile(0.95, sum(rate(lifeos_http_request_latency_seconds_bucket[5m])) by (le))
histogram_quantile(0.95, sum(rate(lifeos_event_dispatch_latency_seconds_bucket[5m])) by (le))
```
Expected: non-empty vectors (not `{}` / NaN).

3) Confirm `/metrics` includes the new histogram buckets:
```
curl -fsS http://127.0.0.1:8000/metrics | rg "lifeos_http_request_latency_seconds_bucket|lifeos_event_dispatch_latency_seconds_bucket"
```

## Acceptance
- Histograms are visible and populated after traffic.
- No Phase 3 alerts regress.
