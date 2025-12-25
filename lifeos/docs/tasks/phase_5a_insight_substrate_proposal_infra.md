# LifeOS - Phase 5a: Insight Substrate & Proposal Infrastructure

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps, ML (stub only)
**Owner:** LifeOS Architecture
**Status:** Approved to Open
**Preconditions:** Phase 4 (Calendar UI) closed and signed off
**Nature:** Meaning infrastructure (no intelligence yet)

---

## 1. Purpose (Why This Phase Exists)

Phase 5a establishes the substrate of intelligence in LifeOS - the minimum system required for the platform to understand user activity in a reversible, explainable, and trustworthy way.

This phase does not attempt to be smart. It creates the structures that allow intelligence to exist later without rewriting the system.

Phase 5a answers one question only:
"Can LifeOS safely propose meaning and let the user correct it?"

---

## 2. Strategic Objective

Introduce system-generated meaning in a way that preserves trust, reversibility, and user authority.

This phase ensures:

- All intelligence is proposed, not imposed
- Every derived object has provenance
- Every system action is undoable
- The user can correct the system's understanding

Phase 5a must make mistakes safe.

---

## 3. Scope (Strictly In-Scope)

### 3.1 Systems Introduced

Phase 5a introduces four foundational systems:

- Canonical Timeline
- Interpretation Framework (Proposal Layer)
- Review & Correction UX
- Insight Record Skeleton (No real logic yet)

### 3.2 Domains Ingested (Initial)

Timeline ingestion must cover at least:

- Calendar
- Journal
- Finance

Other domains may be stubbed but not required.

---

## 4. Explicit Non-Goals (Hard Guardrails)

Phase 5a must not include:

- ML-driven inference
- Embeddings or semantic analysis
- Personalized ranking
- Notifications or nudges
- Autonomous actions
- Cross-user comparisons
- Optimization of insight quality

If something feels "smart", it is likely out of scope.

---

## 5. Core Concepts (Normative)

### 5.1 Canonical Timeline

A unified, append-only event log representing everything the user did or the system observed.

**Timeline Event (minimum fields):**

- event_id
- user_id
- timestamp_start
- timestamp_end (nullable)
- source_domain
- event_type
- source_object_ref
- raw_payload (immutable)
- ingested_at

**Rules**

- Append-only
- Idempotent ingestion
- No rewriting of history
- Raw payloads are immutable

### 5.2 Interpretation (Proposal Layer)

An Interpretation is a system-generated proposal that links or derives meaning from one or more timeline events.

Interpretations are not actions. They are questions the system asks the user implicitly.

**Interpretation record (minimum):**

- interpretation_id
- user_id
- input_event_ids[]
- interpretation_type
- proposed_writes[]
- confidence
- evidence (human-readable)
- status (proposed | accepted | rejected)
- reversible_plan
- created_at, decided_at

**Rules**

- No silent commits
- Every proposal has a reversible plan
- Confidence must be present, even if heuristic

### 5.3 Insight (Skeleton Only)

An Insight in Phase 5a is a container, not a recommendation engine.

**Insight record (minimum):**

- insight_id
- user_id
- insight_type
- summary
- supporting_refs
- confidence
- status
- created_at

No ranking, no notification logic required yet.

---

## 6. Interpretation Types (Phase 5a Minimum)

Phase 5a ships with 1-2 low-risk interpretation types only.

### Required Type (Mandatory)

**Calendar -> Relationship Interaction**

Example:

- Calendar event "Meeting with Taeyang"
- System proposal
- Link event to a Person entity
- Propose an interaction edge (met_with)

**Commit policy**

- Always proposed
- Never auto-committed
- User must confirm, reject, or correct

### Optional Second Type (If Time Permits)

**Calendar -> Obligation Recognition (No Finance Write)**

Example:

- "Pay Rent"
- System proposal
- Propose an "obligation" concept only
- No transaction creation
- No amount inference

---

## 7. User Experience Requirements (Non-Negotiable)

### 7.1 Review Queue

Users must be able to:

- See all pending proposals
- Understand why the proposal exists
- Accept / Reject / Correct

### 7.2 Correction Flow

If a proposal is wrong:

- User can correct the entity mapping
- System must:
  - Apply correction
  - Undo proposed writes
  - Prevent the same mistake in future runs (deterministic fingerprinting)

### 7.3 Provenance & Language

All system copy must:

- Avoid authority tone
- Use "It looks like..." / "We noticed..."
- Clearly show evidence sources

---

## 8. Data & Storage (DB)

**Minimum tables:**

- timeline_events
- interpretations
- insights
- user_feedback_events

**Immutability rules**

- Timeline events immutable
- Interpretations append-only with status transitions
- Insights dismissible but not silently mutated

---

## 9. Team Responsibilities

### Architecture

- Own conceptual integrity
- Approve interpretation types
- Gate Phase 5b entry

### Backend

- Implement timeline ingestion hooks
- Implement interpretation framework
- Enforce idempotency + reversibility
- Build admin/debug endpoints

### Frontend

- Review Queue UI
- Proposal cards (evidence + confidence)
- Correction UX
- Clear system-derived labeling

### DB

- Schema design and indexing
- Migration safety

### QA

- Idempotency tests
- Undo correctness
n- Regression tests for proposal lifecycle
- Golden fixtures for interpretation output

### DevOps

- Background jobs for interpretation runs
- Feature flags per interpretation type
- Observability:
  - proposal counts
  - accept / reject / correct rates

### ML

- Explicitly stubbed
- No models shipped
- Only define future interfaces if needed

---

## 10. Acceptance Criteria (Phase 5a Done)

Phase 5a is complete when:

- Timeline ingestion works for Calendar, Journal, Finance
- At least one interpretation type ships end-to-end
- Users can review, accept, reject, and correct proposals
- Undo works without residue
- No autonomous system actions occur
- Architecture signs off that trust baseline is met

---

## 11. Exit Gate

Phase 5b must not begin until:

- Correction flows feel safe
- Rejection rates are explainable
- No user confusion about system vs user data

---

## Architectural Note

Phase 5a is where LifeOS learns how to be wrong safely.

If this phase is done well:

- All future intelligence becomes easier
- Trust compounds
- Users forgive mistakes

If done poorly:

- No amount of ML will save the system

Treat this phase as foundational, not experimental.
