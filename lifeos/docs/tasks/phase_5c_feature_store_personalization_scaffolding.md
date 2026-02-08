# LifeOS - Phase 5c: Feature Store & Personalization Scaffolding (Readiness Only)

**Audience:** Architecture, Backend, DB, Frontend, QA, DevOps, ML
**Owner:** LifeOS Architecture
**Preconditions:** Phase 5b closed (rules-only insights shipping, deterministic, feed stable)
**Status:** Ready to Open
**Nature:** Internal readiness (no product behavior change)

---

## 1) Intent

Phase 5c builds the learning substrate (data + instrumentation + contracts) while guaranteeing:

- No user-visible behavior change
- No ranking/personalization effects
- No ML-driven decisions
- No hidden optimization

Phase 5c produces data and validates invariants. Phase 6 is the first phase allowed to consume these outputs for decisions.

---

## 2) Scope

### In-scope (exactly)

1. Versioned Feature Store (v1)
2. User feedback events wired cleanly (explicit only)
3. Insight engagement metrics + dashboards
4. Personalization hooks (inactive / no-op)
5. Replay / leakage / backfill gates

### Out-of-scope (explicitly forbidden)

- Any ranking changes to the Insight Feed
- Any model scoring, training, embeddings, or smart selection
- Any implicit feedback inference (dwell-time, scroll depth) unless explicitly labeled as engagement metric and kept non-decisioning
- Any new insight logic beyond instrumentation needs
- Any new user-visible UI features beyond minimal feedback controls

---

## 3) Non-Negotiable Guarantees

### 3.1 No-Op Personalization Guarantee

- Default config: `PERSONALIZATION_ENABLED=false`
- `rank_insights(...)` must be no-op:
  - output order == input order, or
  - deterministic stable sort using an invariant key that does not change candidate order semantics (e.g., stable by existing `created_at` only if already used)

### 3.2 Feature Invariants

All features must be:

- Deterministic: same inputs -> same outputs
- Time-causal: computed as-of timestamp; no future leakage
- Auditable: can trace which events produced it (provenance)
- Versioned: semantic versioning major.minor.patch

---

## 4) System Contracts to Implement

### 4.1 Feature Store Data Model (Normative)

**Table / Collection:** `features` (or `features_v1`)

**Minimum fields:**

| Field | Type | Notes |
| --- | --- | --- |
| feature_id | UUID / int | PK |
| user_id | FK | Required for user-scoped features |
| entity_type | enum | user, insight, event |
| entity_id | string | e.g., insight_id if entity_type=insight |
| feature_name | string | canonical name |
| value | numeric / string / bool / json | enforce dtype |
| dtype | enum | float, int, bool, str, json |
| window | string | e.g., 7d, 30d, as_of_day |
| computed_at | datetime | computation timestamp |
| as_of_ts | datetime | causal boundary |
| feature_version | semver string | major.minor.patch |
| source_event_types | array/string | provenance |
| provenance_ref | json/string | pointers to event_ids or hashes |
| backfill_policy | enum | allowed, disallowed, limited |
| lifecycle_state | enum | proposed, shadow, active_ready, deprecated, removed |
| created_at, updated_at | datetime |  |

**Indexes (minimum)**

- (user_id, feature_name, as_of_ts desc)
- (entity_type, entity_id, feature_name, as_of_ts desc)
- (feature_name, feature_version)

**Rules**

- Writes are append-only per (user_id/entity, feature_name, as_of_ts, version) unless explicitly defined as upsert-safe.
- As-of is the truth boundary. Anything computed must only depend on events with timestamp <= as_of_ts.

---

### 4.2 Feature Lifecycle Rules (Normative)

- proposed: defined but not computed in prod
- shadow: computed and stored, not consumed
- active_ready: computed + validated, still not consumed for decisions
- deprecated: no new writes, still readable
- removed: not written and not queried

Only Phase 6 may switch features into decision consumption. Phase 5c stops at active_ready.

---

### 4.3 Feedback Event Taxonomy (Normative)

**Events to emit (explicit user action only):**

- insight_viewed
- insight_dismissed
- insight_saved
- insight_shared
- insight_feedback_positive
- insight_feedback_negative
- insight_reported_issue

**Optional field:**

- feedback_reason enum: not_me, already_know, too_personal, irrelevant, wrong, sensitive, other

**Event requirements**

- idempotent (client retries safe)
- session-aware (include session_id/request_id)
- no inferred labels from dwell time (unless explicitly defined as engagement, not feedback)

---

### 4.4 Metric Contract (Define Before Dashboards)

**Metrics families:**

**Exposure**
- impressions per user per day

**Engagement**
- save-rate, dismiss-rate, feedback-rate

**Negative quality**
- report-rate, wrong reason counts

**Latency**
- insight generation -> delivered -> interacted

Each metric must define:

- exact definition
- source events
- windowing rule
- expected range + anomaly threshold

---

### 4.5 Personalization Hook Interface (Inactive)

Add policy interface:

`rank_insights(user_id, candidates, context) -> ordered_candidates`

Phase 5c implementation must be:

- deterministic
- no-op (order preserved)
- kill-switch protected

---

## 5) Team-by-Team Responsibilities

### A) Architecture (Owner / Gate)

**Scope**
- Own contracts, invariants, and no behavior change guarantee.

**Deliverables**
- Phase 5c contract doc:
  - Feature schema + lifecycle
  - Feedback taxonomy
  - Metric definitions
  - Personalization policy interface rules
  - Acceptance gate checklist (replay/leakage/coverage/no-op proof)

**Acceptance**
- All Phase 5c gates defined and signed

---

### B) Backend

**Scope**
- Implement feature storage, feature compute runners, feedback ingestion endpoints, and metric-friendly logs.

**Deliverables**
- Feature store service (write/read)
- Provenance capture (event_ids or hashed references)
- Feedback endpoints:
  - POST /insights/{id}/feedback
  - POST /insights/{id}/dismiss (if server-side)
  - POST /insights/{id}/save
  - POST /insights/{id}/report
- Idempotency keys + session context
- Personalization policy hook wired into feed pipeline as no-op
- Replay rebuild command:
  - rebuild features from raw events for a window (e.g., 30d)

**Acceptance**
- No feed ordering change under default config
- Replay rebuild matches stored outputs

---

### C) DB

**Scope**
- Add feature store tables/indexes and maintain migration discipline.

**Deliverables**
- Migration for features table + indexes
- Optional provenance tables if you avoid JSON refs
- Rollback-safe migration plan

**Acceptance**
- Window queries performant
- No schema drift between ORM and DB

---

### D) Frontend

**Scope**
- Minimal UI additions to collect explicit feedback and ensure event emission coverage.

**Deliverables**
- Insight card actions wired to backend:
  - dismiss/save/feedback/report
- Guarantee >99% interaction emission:
  - view event on render
  - click events for all controls
- Reason picker only for report/negative feedback (optional)

**Acceptance**
- No UI/UX changes that alter feed ranking or content
- Event emission verified by QA

---

### E) QA (Non-Negotiable Gate)

**Scope**
- Prove invariants and no-op behavior.

**Deliverables**
- Tests:
  - replay correctness (feature rebuild equality)
  - leakage checks (no event timestamp > as_of_ts used)
  - idempotency tests for feedback events
  - coverage test: interactions emit events (>99% in fixture flows)
  - no-op personalization A/B diff: zero ranking deltas
- Golden fixtures for:
  - feature outputs
  - engagement metrics windows

**Acceptance**
- All gates green; no flakiness

---

### F) DevOps

**Scope**
- Operate runners, dashboards, and safe backfill execution.

**Deliverables**
- Scheduled jobs:
  - feature compute (daily + optional incremental)
  - metric rollups (if computed outside Prometheus)
- Dashboards:
  - exposure/engagement/negative-quality
  - pipeline health + latency
- Alerts:
  - metrics-missing
  - pipeline failure
  - coverage drop
- Backfill runbook:
  - backfill 30 days safely

**Acceptance**
- Backfill works without breaking invariants
- Dashboards populated and trusted

---

### G) ML

**Scope**
- Contracts only. No training, no scoring.

**Deliverables**
- phase5c_contracts.py documenting:
  - feature naming rules
  - lifecycle states
  - future consumption boundaries
- Alignment helper verifying backend feature registry <-> ML contract registry

**Acceptance**
- ML is non-blocking; no runtime dependency on ML for Phase 5c

---

## 6) Verification Gates (Exit Criteria)

Phase 5c closes only if all are true:

1. Replay correctness
   - Rebuilding features from raw events yields same results (within defined tolerance).
2. Leakage checks pass
   - No future timestamps used vs as_of_ts.
3. Event coverage >99%
   - Insight interactions reliably emit events.
4. Dashboards exist and work
   - Exposure + engagement + negative-quality + pipeline health.
5. Safe backfill proven
   - Backfill 30-day window without violating invariants or breaking dashboards.
6. No-op personalization proven
   - A/B diff shows zero ranking deltas under default config.

---

## 7) Rollout & Kill Switch

- Default: PERSONALIZATION_ENABLED=false
- Default: features in shadow or active_ready only
- If anomalies detected:
  - disable runners
  - stop backfills
  - keep feature store read-only

---

## 8) Explicit Non-Goals

- No Phase 6 behavior (ranking, learning, personalization)
- No notifications
- No smart suggestions
- No expansion of insight types beyond instrumentation needs

---

## 9) Completion Artifacts

To close Phase 5c, produce:

- phase_5c_feature_store_personalization_scaffolding.md (signed)
- Test reports proving gates
- Ops runbook for backfill
- Dashboard links/screenshots
- Architecture doc update + task archived

---

## Incident Resolution Note (Migration Authority)

Architectural closure statement: Migration Authority Note has been fully executed. Images were rebuilt from the canonical commit, missing migrations are baked into the runtime images, `alembic upgrade head` ran cleanly, and QA verified determinism, feed visibility, and `features_v1` presence. The migration incident is CLOSED. Phase 5c infrastructure is unblocked.

- **Date:** 2026-02-06
- **Issue:** Runtime containers failed to locate revisions `20251227_phase5b_features_daily` and `20260205_phase5c_feature_store_v1` due to images missing migration files.
- **Resolution:** Images rebuilt from canonical commit, migrations baked into image, `alembic upgrade head` executed cleanly, containers redeployed.
- **QA:** Verified runner determinism, feed API, and `features_v1` presence; sign-off recorded.
- **Status:** Incident CLOSED; Phase 5c infra unblocked.
