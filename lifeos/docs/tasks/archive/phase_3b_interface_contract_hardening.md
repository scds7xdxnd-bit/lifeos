# LifeOS - Phase 3b: Interface and Contract Hardening

Audience: Architecture, Backend, Frontend, QA, DevOps
Owner: Systems Architecture
Phase Context: Phase 3b (Post-UX Stabilization, Pre-Learning)
Status: Completed (Archived)

---

## 1. Purpose
Phase 3b freezes external system behavior without changing meaning.

At this point:
- Domain semantics are frozen (Phase 2.5)
- Cross-domain intelligence is deterministic and governed (Phase 3a)
- Human-facing domain surfaces are aligned and stable (Phase 3a.5)

Phase 3b converts this stability into explicit, enforceable contracts.
No new meaning, no new features, and no UX changes are allowed in this phase.

---

## 2. Strategic Objective
Make LifeOS externally reliable, backward-compatible, and regression-proof.

Phase 3b ensures that:
- APIs can be depended on by clients
- Projections cannot mutate state
- Determinism violations are detectable
- Governance rules are enforced automatically

This phase marks the transition from evolving system to stable platform.

---

## 3. Scope (Strictly In-Scope)

### A. External and Semi-External Interfaces
- Insight feed
- Review queue
- Calendar view / ledger
- Finance read-only surfaces
- UX surface-backed projection endpoints

### B. Supporting Infrastructure
- Auth (admin reset only)
- Observability and SLOs
- Governance documentation

---

## 4. Core Principles (Non-Negotiable)
1) Freeze behavior, not implementation
2) Backward compatibility is mandatory
3) Read-only means read-only
4) Contracts must reflect DSD authority
5) Violations must fail fast

---

## 5. Required Deliverables (Blocking)

### 5.1 API Contract Freeze
Version and document response schemas for:
- Insight feed
- Review queue
- Calendar view / ledger
- Finance read surfaces (journal, trial balance, receivables, forecast)

Each schema must include:
- Field names and types
- Field meaning (human-legible)
- Field source (user / system / imported)
- Stability classification (stable / conditional)

Schemas become canonical references.

### 5.2 Contract Tests (Backward Compatibility)
Add automated contract tests that ensure:
- No breaking field removals
- No type changes
- No semantic redefinition
- No authority violations (claims exceeding DSD)

Breaking changes require:
- Major version bump
- DSD amendment
- Architectural approval

### 5.3 Read-Only Guarantee Enforcement
Ensure that:
- Projection endpoints cannot mutate state
- No write paths are reachable from read surfaces
- Accidental side effects are impossible

Add:
- Guardrails in routing and services
- Negative tests asserting immutability
- CI failures on mutation attempts

### 5.4 Auth Hygiene (Minimal Scope)
Permitted changes only:
- Admin reset session flow
- Database reset script

Explicitly forbidden:
- Token format changes
- Device identity
- Session semantics expansion

Auth is considered stable for this phase.

### 5.5 Observability and SLOs
Define and instrument SLOs for:
- Insight generation latency
- Projection correctness
- Replay determinism health
- Contract violation frequency

Add alerts for:
- Determinism regressions
- Schema contract breaks
- Unauthorized write attempts

Metrics must describe system correctness, not engagement.

### 5.6 Governance Updates
- Update architecture documentation to lock Phase 3b scope
- Publish Phase 3b rules as enforceable policy
- Define escalation path for contract exceptions

---

## 6. Explicit Non-Goals
Strictly forbidden in Phase 3b:
- UX changes
- New API fields (without version bump)
- New insights
- ML behavior changes
- Performance optimization
- Personalization or ranking

If it alters meaning or user experience, it is out of scope.

---

## 7. Team Responsibilities

### A. Architecture
- Approve schema versions
- Enforce DSD alignment
- Gate Phase 4 entry

### B. Backend
- Implement versioned schemas
- Add contract and immutability tests
- Enforce read-only guarantees

### C. Frontend
- Consume versioned schemas
- Avoid reliance on unstable fields
- Surface errors on contract mismatch

### D. QA
- Validate backward compatibility
- Assert read-only behavior
- Test determinism and SLO adherence

### E. DevOps
- Monitor SLOs
- Alert on violations
- Support replay validation tooling

---

## 8. Exit Criteria (Phase Gate)
Phase 3b is complete only when:
- All target APIs are versioned and documented
- Contract tests block breaking changes
- Read-only guarantees are enforced and tested
- SLOs are defined, live, and alerting
- Architecture formally signs off

No learning or personalization phase may begin before this gate.

---

## 9. Architectural Note
Phase 3b is where LifeOS stops being flexible by default.

From this point on:
- Change requires intent
- Stability is assumed
- Trust compounds over time

---

# API Schema Versioning Rules (Aligned with DSDs)

## 1. Versioning Model
- Semantic versioning per surface: MAJOR.MINOR.PATCH
- Version applies to response shape and meaning, not implementation

---

## 2. Version Change Rules

### PATCH (x.y.Z)
Allowed:
- Documentation clarification
- Non-functional metadata
- Bugfixes with identical semantics

Forbidden:
- Field addition/removal
- Type changes

### MINOR (x.Y.0)
Allowed:
- Adding optional fields marked as:
  - source = system-derived
  - stability = conditional
- Must not change existing field meaning

Requires:
- DSD review
- Contract test updates

### MAJOR (X.0.0)
Required when:
- Removing fields
- Changing field meaning
- Promoting conditional to stable semantics
- Expanding domain authority

Requires:
- DSD amendment
- Architecture sign-off
- Explicit migration notes

---

## 3. DSD Alignment Rules (Hard Law)
- Every API field must map to a DSD data field
- Field meaning must match DSD language
- Fields marked "Stable" in DSD:
  - cannot change type or meaning
  - cannot be removed without MAJOR bump
- Fields marked "Likely to change":
  - may evolve only via MINOR bump

---

## 4. Authority Enforcement
Schemas must not:
- Exceed claims allowed by the surface's DSD
- Introduce confidence semantics not defined in Phase 2.5
- Imply automation where review-only is mandated

Violations must fail CI.

---

## 5. Deprecation Policy
- Deprecated fields:
  - Must be documented
  - Must remain for at least one MINOR version
- Silent removal is forbidden

---

## 6. Governance Enforcement
- All schema changes require:
  - Updated schema doc
  - Passing contract tests
  - Architecture approval if MAJOR

This policy is binding.

---

## Final Architectural Note
DSDs define what LifeOS is allowed to say.
Phase 3b schemas define how that truth is communicated safely over time.

Once Phase 3b completes, LifeOS becomes a platform that can evolve without breaking trust.
