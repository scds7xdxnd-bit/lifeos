# LifeOS - Phase 3c-1: Read & Throughput Scaling Brief

**Audience:** Architecture, Backend, DB, DevOps, Frontend, QA
**Owner:** LifeOS Architecture
**Predecessor Phases:** Phase 3b -> Phase 3b.1 (Stabilization)
**Status:** Conditional Execution (trigger-driven)
**Nature:** Infrastructure hardening (no user-visible change)

---

## 1. Situation & Trigger (Why This Phase Exists)

Phase 3b and Phase 3b.1 establish that LifeOS is:

- Contract-stable
- Deterministic
- Observable
- Semantically frozen at the interface level

However, upcoming work (Phase 4 - Calendar visual & interaction rewrite) will materially increase read pressure due to:

- Time-canvas rendering (dense range queries)
- Month/week/day views with overlap computation
- Multi-day and all-day spanning
- Frequent re-queries during navigation and scroll

Before undertaking any major UI rewrite, we must answer one question conclusively:

**Can the current read paths sustain higher query density and interaction frequency without violating latency, correctness, or determinism guarantees?**

Phase 3c-1 exists to answer that question without changing meaning, semantics, or UX.

---

## 2. Purpose of Phase 3c-1

**Harden read throughput and latency ceilings so richer interfaces can be built safely.**

This phase focuses on:

- Read performance
- Query scalability
- Projection access patterns

It explicitly avoids:

- New features
- New semantics
- New UI
- New insight logic

---

## 3. Scope (Strictly In-Scope)

### 3.1 Read Surfaces Covered

Only high-frequency read paths are in scope, including:

- Calendar:
  - View / ledger APIs
  - Range queries (day/week/month)
- Finance:
  - Dashboard summaries
  - Trial balance
  - Forecast read surfaces
- Insights:
  - Feed
  - Review queue

Write paths are out of scope except where required to maintain read correctness.

---

## 4. Non-Goals (Explicitly Forbidden)

The following must not occur in Phase 3c-1:

- UI or interaction changes
- API shape changes
- Contract version bumps
- Semantic reinterpretation of data
- New projections
- ML feature work
- Event schema changes

If it changes what the user sees or what an API returns, it does not belong here.

---

## 5. Strategy
### Option C - Index & Query Optimization Only (Chosen)

- Composite indices
- Query plan tuning
- Pagination/windowing refinements

### Option A - Cached Projections (After Option C is completed)

- Cache read-only projections (memory / Redis)
- TTL-based invalidation
- Event-driven cache busting where safe

### Option B - Materialized Views (Not now)

- DB-level materialized views for:
  - Calendar range queries
  - Finance aggregates
- Refresh strategy must be deterministic



**CQRS is explicitly out of scope.**
This phase is conservative and incremental.

Each surface must document:

- Chosen option
- Rationale
- Fallback plan

---

## 6. Team-by-Team Responsibilities

### A. Architecture

**Scope**

- Own the read-scaling strategy selection
- Prevent scope creep into semantics or UX

**Deliverables**

- Phase 3c-1 design note:
  - Surfaces covered
  - Strategy chosen per surface
  - Expected latency targets

**Acceptance Criteria**

- Strategy documented and approved
- No contract or semantic drift

---

### B. Backend

**Scope**

- Optimize read APIs for throughput and latency
- Introduce caching/materialization if approved

**Deliverables**

- Updated service/query implementations
- Benchmarks (before/after)
- Safeguards ensuring read-only guarantees remain intact

**Acceptance Criteria**

- Read APIs remain contract-compatible
- Latency improves or remains stable under increased load
- Projection correctness metrics remain clean

---

### C. DB

**Scope**

- Query plan analysis
- Index design
- Materialized view support (if selected)

**Deliverables**

- Index additions or adjustments
- Migration scripts (reversible)
- Documentation of query performance characteristics

**Acceptance Criteria**

- No regression in write performance
- Range queries scale predictably
- Data integrity constraints preserved

---

### D. DevOps

**Scope**

- Observability of read performance
- Load characterization

**Deliverables**

- Dashboards for:
  - Read API latency
  - Cache hit/miss (if applicable)
- Optional synthetic read load harness

**Acceptance Criteria**

- Clear visibility into read bottlenecks
- Alerts remain quiet under expected load

---

### E. Frontend

**Scope**

- No feature work
- Assist with realistic read patterns for testing

**Deliverables**

- Representative query usage patterns
- Feedback on perceived latency (read-only)

#### Frontend Read Patterns (for load/DB testing)
Calendar (high-frequency):
- Day view: `GET /api/v1/calendar/day?date=YYYY-MM-DD` on view load + prev/next day
- Week view: `GET /api/v1/calendar/week?start=YYYY-MM-DD` on view load + prev/next week
- Month view: `GET /api/v1/calendar/month?year=YYYY&month=MM` on view load + prev/next month
- Ledger: `GET /api/v1/calendar/ledger?anchor=YYYY-MM-DD&direction=backward|forward&limit=50` on list view load + load older/newer

Finance (read-only summaries):
- Dashboard: `GET /api/finance/dashboard` on load (also used by forecast schedule list)
- Trial balance: `GET /api/finance/trial_balance`, `GET /api/finance/trial_balance/period`, `GET /api/finance/trial_balance/monthly` when filters/review run
- Forecast: `GET /api/finance/forecast?days=N` on refresh and after schedule recompute

Insights:
- Feed: `GET /api/v1/insights/feed?page=N&per_page=M` (pagination)
- Review queue: `GET /api/v1/insights/review?limit=N&offset=M`

#### Frontend Verification (read-only)
- Navigate day/week/month views quickly and confirm no contract errors or UI regressions.
- Load ledger and paginate older/newer events to exercise cached reads.
- Load finance dashboard, trial balance, and forecast to confirm response shapes unchanged.
- Check `/metrics` for `lifeos_read_cache_hits_total` and `lifeos_read_cache_misses_total` increments during navigation (no UI changes required).

**Acceptance Criteria**

- No UX changes introduced
- Frontend compatible with optimized reads

---

### F. QA

**Scope**

- Regression assurance

**Deliverables**

- Tests ensuring:
  - Contract compatibility
  - Deterministic replay still holds
  - Cached/materialized reads remain correct

**Acceptance Criteria**

- All Phase 3b tests remain green
- No flakiness introduced

---

## 7. Verification & Success Metrics

Phase 3c-1 is successful if:

- Read latency remains within defined SLOs under higher query frequency
- No increase in:
  - Projection correctness errors
  - Replay determinism failures
  - Contract violations
- Metrics and alerts remain trustworthy

No soak is required unless architecture deems risk elevated.

---

## 8. Exit Criteria

Phase 3c-1 is complete when:

- Architecture signs off on read scalability confidence
- All changes are deployed and observed
- Phase 3b guarantees remain intact

Only after this may Phase 4 (Calendar UI redesign) begin.

---

## 9. Architectural Note

Phase 3c-1 exists to make the system boring under load.

If Phase 4 succeeds, users will assume the calendar was always this smooth.
That illusion is only possible if Phase 3c-1 is executed with discipline.

Treat this phase as invisible structural reinforcement, not innovation.
