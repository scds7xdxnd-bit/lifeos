# LifeOS - Observability Completion Task
HTTP & Event Dispatch Latency Histograms

**Audience:** DevOps, Backend
**Owner:** Architecture
**Status:** Approved follow-up (non-phase, non-scaling)
**Context:** Phase 3b complete, Phase 3c-2 deferred

---

## 1. Situation (Why This Task Exists)

During the Phase 3c-2 trigger assessment:

- Determinism, contract violations, and projection correctness were all 0
- Retry pressure and fan-out pressure were not observed
- Phase 3c-2 was correctly deferred

However, one observability gap was identified and recorded:

`histogram_quantile(0.95, sum(rate(lifeos_insight_latency_seconds_bucket[5m])) by (le))` -> NaN

This indicates missing or unpopulated latency histograms, not a transport issue.

This task exists solely to close that observability gap, so future trigger assessments and UI-heavy phases (Phase 4+) have reliable latency data.

---

## 2. Goal (Strict)

Emit stable, non-NaN latency histograms for core request and dispatch paths, visible in Prometheus and Grafana.

This task does not:

- Change behavior
- Change contracts
- Add infra
- Introduce queues or brokers
- Optimize performance

---

## 3. Scope (Exactly What to Instrument)

### A. HTTP Request Latency (Required)

Instrument end-to-end HTTP request latency for the web app.

**Metric**

`lifeos_http_request_latency_seconds_bucket`

**Labels (minimum)**

- `method`
- `route` (templated, not raw path)
- `status_code`

**Notes**

- Use Prometheus histogram buckets suitable for UI/API traffic (e.g., 50ms -> 5s).
- Ensure the metric is registered at startup, even if no traffic occurs.
- Avoid high-cardinality labels.

### B. Event Dispatch Latency (Optional but Recommended)

If a clear dispatch boundary exists (event emitted -> handler executed):

**Metric**

`lifeos_event_dispatch_latency_seconds_bucket`

**This should measure**

- Time from event emission to handler completion (or enqueue -> handled, depending on current architecture)

If this boundary is ambiguous, document why and skip rather than guessing.

---

## 4. Explicit Non-Goals (Forbidden)

This task must not:

- Introduce new queues, brokers, or workers
- Change outbox semantics
- Add retries or DLQs
- Modify event schemas
- Touch UI code
- Tune performance

If the work starts to resemble scaling, stop and escalate.

---

## 5. Deliverables

### Backend

- Instrument latency histograms in request middleware and (if applicable) dispatch path
- Ensure metrics are registered and exported via `/metrics`
- Add minimal unit coverage to assert metric presence (not values)

### DevOps

- Confirm `/metrics` exposes the new histogram buckets
- Update Grafana dashboards to include:
  - p50 / p95 / p99 HTTP request latency
- Verify no "metrics-missing" alerts fire

---

## 6. Verification Checklist (Blocking)

This task is complete only when:

- `/metrics` includes:
  - `lifeos_http_request_latency_seconds_bucket`
- Prometheus query returns real values (not `{}` / NaN):

```
histogram_quantile(
  0.95,
  sum(rate(lifeos_http_request_latency_seconds_bucket[5m])) by (le)
)
```

- Metrics persist across app restart
- No existing Phase 3 alerts regress
- Architecture confirms observability gap is closed

---

## 7. Acceptance Criteria

- Latency histograms visible and populated under normal usage
- No change in system behavior
- No additional infra introduced
- Task documented as observability completion, not scaling

---

## 8. Architectural Position (Important)

This task exists to enable correct future decisions, not to justify new architecture.

Once complete:

- Phase 3c-2 assessments become data-backed
- Phase 4 UI work has latency confidence
- Phase 3c-3 decisions won't be speculative

Keep this boring, minimal, and correct.
