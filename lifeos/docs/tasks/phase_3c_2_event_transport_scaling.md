# LifeOS - Phase 3c-2: Event Transport Scaling (Broker Hardening)

**Audience:** Architecture, Backend, DevOps, QA, DB
**Owner:** LifeOS Architecture
**Predecessor Phases:** Phase 3b -> Phase 3b.1 -> Phase 3c-1
**Status:** Conditional Execution (trigger-driven)
**Nature:** Infrastructure hardening (no semantic or UX changes)

---

## 1. Purpose

**Introduce durable, scalable event transport without changing meaning, contracts, or UX.**

Phase 3c-2 exists to move from in-process event dispatch to a broker-backed transport only when scale demands it.

---

## 2. Non-Goals (Forbidden)

- No new insights or event types
- No semantic changes to existing events
- No API changes or version bumps
- No UI changes
- No personalization or ML changes
- No write-path redesign beyond transport

If it changes meaning or user-visible behavior, it is out of scope.

---

## 3. Scope (In-Scope)

- Outbox -> broker bridge
- Broker-backed fan-out and retry semantics
- Durable delivery guarantees
- Dead-letter queue (DLQ) policy
- Observability for event transport health

---

## 4. Architecture Strategy

**Default path:** retain the existing outbox as system-of-record and add a broker bridge.

- Outbox remains authoritative
- Broker is delivery transport only
- Idempotency enforced at consumer side

**Broker candidates:** RabbitMQ or Kafka (selection by Architecture)

---

## 5. Team Responsibilities

### A. Architecture

- Select broker technology and delivery guarantees
- Approve idempotency strategy and retry policy
- Define Phase 3c-2 exit criteria

### B. Backend

- Implement outbox -> broker bridge
- Ensure idempotent consumers
- Maintain event contracts unchanged

### C. DB

- Additive schema only (if required for broker offsets or delivery tracking)
- No destructive migrations

### D. DevOps

- Provision broker in staging and production
- Add monitoring for queue depth, lag, retries, DLQ
- Provide rollback plan

### E. QA

- Verify delivery guarantees
- Validate no contract drift
- Confirm retry and DLQ behavior

---

## 6. Required Deliverables

- Broker selection and rationale (Architecture)
- Outbox bridge implementation (Backend)
- Delivery semantics documented (at-least-once with idempotency)
- Retry and DLQ policy documented and tested
- Observability dashboards and alerts
- Rollback plan

---

## 7. Verification & Exit Criteria

Phase 3c-2 is complete when:

- Broker-backed transport operates under load with no data loss
- Outbox remains authoritative and replay-safe
- Retry and DLQ behavior proven in staging
- Contract and determinism tests remain green

---

## 8. Architectural Note

Phase 3c-2 is transport scaling, not system evolution.

It exists to keep the event pipeline boring under higher concurrency and fan-out.
The system must behave exactly the same to users and to downstream consumers.
