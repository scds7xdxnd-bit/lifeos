# LifeOS - Phase 3c-2: Event Transport Scaling
Trigger Assessment & Decision Brief (Architecture-Owned)

**Audience:** Architecture (primary), Backend, DevOps, QA
**Owner:** LifeOS Architecture
**Status:** Trigger Assessment (no implementation authorized)
**Purpose:** Determine - based on evidence, not anticipation - whether Phase 3c-2 (event transport scaling via broker/queue) should formally open.

---

## 1. Why This Exists (Context)

LifeOS has completed:

- Phase 3b: Interface & contract hardening
- Phase 3b.1: Stabilization
- Phase 3c-1: Read & throughput scaling (verified, documented, closed)

The system is currently:

- Deterministic
- Contract-stable
- Projection-correct
- Read-scaled
- Operating primarily in a single-process / low fan-out regime

Before introducing brokers, queues, or distributed event transport, we must prove necessity.
This phase exists to prevent premature infrastructure complexity.

Phase 3c-2 is opened only if real fan-out or dispatch pressure is observed.

---

## 2. Decision Principle (Non-Negotiable)

Phase 3c-2 must not open based on:

- Theoretical future scale
- Anticipated UI richness
- Architectural elegance
- "Best practice" arguments

It opens only if trigger signals are present, sustained, and documented.

---

## 3. Trigger Signals (Decision Inputs)

Phase 3c-2 is eligible to open only if at least one of the following conditions is observed under normal operation:

### A. Outbox / Dispatch Pressure

- Outbox pending count is persistently high and growing
- Dispatch latency exceeds defined SLOs
- Retry volume is non-trivial and sustained
- Failed event count accumulates over time

### B. Fan-Out Saturation

- In-process workers cannot keep up with event volume
- Handler execution time variability causes backlog
- Multiple workers are required just to maintain steady state

### C. Failure Isolation Need

- Events require dead-letter handling to avoid blocking progress
- Retry/backoff behavior impacts unrelated event streams
- Failure domains cannot be safely isolated in-process

If none of these are present, Phase 3c-2 remains deferred.

---

## 4. Metrics to Collect (Current System Only)

No new infrastructure is introduced for this assessment.

**Outbox & Dispatch**
- Outbox pending count (p50 / p95)
- Dispatch latency (event -> handled)
- Retry rate (per minute)
- Retry age (time to recovery)
- Failed events per day

**Worker Throughput**
- Events processed per minute per worker
- Queue depth vs throughput ratio
- Worker utilization (if observable)

**Failure Characteristics**
- Count of events stuck in failed / retry state
- Backoff duration vs eventual success
- Any cross-handler interference observed

---

## 5. Evidence Log (Architecture-Owned)

Architecture maintains a rolling evidence log:

```
Date:
Environment:
Observed event volume (avg / peak):
Outbox pending p95:
Dispatch latency p95:
Retry rate:
Failure rate:
Fan-out / isolation observations:
Decision recommendation (Open / Defer):
Rationale:
```

At least two observation windows are required before escalation.

---

## 6. Decision Gate

**Open Phase 3c-2 if:**

- Two or more trigger signals are confirmed, or
- One trigger signal is confirmed and rising across consecutive windows

**Defer Phase 3c-2 if:**

- Signals are absent
- Signals are transient
- System stabilizes after minor tuning

The default decision is DEFER unless evidence proves otherwise.

---

## 7. Explicit Non-Actions (Forbidden During Assessment)

During this phase, teams must not:

- Introduce brokers (Kafka, RabbitMQ, etc.)
- Add queues or DLQs
- Refactor event schemas
- Change handler semantics
- Introduce CQRS or async fan-out frameworks

This phase is observational and evaluative only.

---

## 8. If Triggered (Next Step Only)

If Architecture formally decides to open Phase 3c-2:

- Create `phase_3c_2_event_transport_scaling.md`
- Define:
  - Transport strategy (broker choice, delivery guarantees)
  - Outbox -> broker bridge
  - Retry / DLQ semantics
  - Worker topology
  - Sequence rollout with strict rollback plan

No preparatory work is authorized before that decision.

---

## 9. Architectural Position

Phase 3c-2 is a one-way door:

- It increases operational surface area
- It increases failure modes
- It increases long-term maintenance cost

Therefore, proof precedes construction.

This trigger assessment protects LifeOS from premature scale complexity and preserves the discipline established in earlier phases.

---

## 10. Evidence Log (Current Window - 2025-12-25)

```
Date: 2025-12-25
Environment: local dev (macOS)
Observed event volume (avg / peak): not recorded
Outbox pending p95: not recorded
Dispatch latency p95: not observed (no retries; no backlog growth)
Retry rate: increase(lifeos_event_retry_total[15m]) -> not observed
Failure rate: lifeos_replay_determinism_failures_total=0.0; lifeos_contract_violations_total=0.0; lifeos_projection_correctness_errors_total=0.0
Fan-out / isolation observations: none
Decision recommendation (Open / Defer): Defer
Rationale: Trigger signals absent; outbox count (status != processed) returned 380 but no evidence of growth or backlog pressure.
```

**Notes:**
- Insight latency p95 query returned empty vector (no data). This is an instrumentation gap, not a Phase 3c-2 trigger.
- SELECT count(*) FROM platform_outbox WHERE status != 'processed' returned 380; without growth trend, it does not indicate sustained backlog.

**Decision Table (2025-12-25):**

| Question                    | Yes | No |
| --------------------------- | --- | -- |
| Events backing up?          | ☐   | ☑  |
| Retries sustained?          | ☐   | ☑  |
| Dispatch latency growing?   | ☐   | ☑  |
| Workers overloaded?         | ☐   | ☑  |
| Failures needing isolation? | ☐   | ☑  |
