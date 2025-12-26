# LifeOS - Phase 5b: Deterministic Cross-Domain Insights (Rules Only)

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps, ML (rules-only)
**Owner:** LifeOS Architecture
**Preconditions:** Phase 5a (Insight Substrate & Proposal Infrastructure) complete and signed off
**Status:** Approved to Open
**Nature:** Meaning expansion (deterministic, explainable, non-autonomous)

---

## 1. Purpose (Why This Phase Exists)

Phase 5b exists to prove real cross-domain value to users using strictly deterministic, explainable logic, while preserving the trust guarantees established in Phase 5a.

This phase answers the question:

"Can LifeOS surface genuinely useful insights that connect domains, without surprising or overriding the user?"

Phase 5b deliberately avoids probabilistic learning or automation. All insights must be:

- Rule-based
- Explainable
- Conservative in tone and delivery

---

## 2. Strategic Objective

Make the Insight Feed meaningfully useful, without changing system authority or user control.

Specifically, Phase 5b must:

- Demonstrate cross-domain reasoning (Calendar <-> Finance, Journal <-> Habits, etc.)
- Establish a stable Insight Type Registry
- Introduce simple, auditable feature computation
- Build user confidence that insights are grounded and fair

---

## 3. Scope (Strictly In-Scope)

### 3.1 Systems Extended

Phase 5b extends (but does not redefine):

- Canonical Timeline
- Interpretation Framework
- Insight Records
- Review & Feedback flows

### 3.2 New Capabilities Introduced

**Feature Computation**

- Simple aggregates (counts, sums, streaks, deltas)
- Windowed by time (last 7 / 30 / 90 days)
- Deterministic and reproducible

**Insight Type Registry (v1)**

- 5-10 predefined Insight Types
- Each type explicitly declares:
  - Required features
  - Query window
  - Trigger conditions
  - Confidence computation
  - Explanation template

**Cross-Domain Correlations**

- Insights may draw from multiple domains
- Each Insight Type defines its own dependencies

**Feed-Only Ranking**

- Conservative, deterministic ordering
- No personalization or learning

---

## 4. Explicit Non-Goals (Hard Guardrails)

Phase 5b must not include:

- ML models or statistical learning
- Embeddings, semantic similarity, or NLP
- Personalized ranking or LTR
- Proactive notifications or nudges
- Autonomous actions or system writes
- Cross-user comparisons or benchmarks

If a feature requires learning from the user, it belongs in Phase 5c or later.

---

## 5. Feature Computation (Normative)

### 5.1 Feature Characteristics

All features must be:

- Windowed (time-bounded)
- Versioned (definition changes tracked)
- Explainable (traceable back to events)
- Deterministic (same inputs -> same outputs)

### 5.2 Example Feature Classes (Non-Exhaustive)

- Counts: number of events per category
- Aggregates: total spend by merchant/category; total duration of calendar blocks
- Deltas: week-over-week change
- Streaks: consecutive habit check-ins

### 5.3 Storage

Features may be stored in:

- features_daily tables, or
- domain-scoped feature namespaces

Raw timeline events must remain the source of truth.

---

## 6. Insight Type Registry (v1)

### 6.1 Insight Type Contract

Each Insight Type must define:

- insight_type (enum)
- required_features[]
- query_window
- trigger_logic (rule-based)
- confidence_logic
- priority_logic
- summary_template
- detail_template
- delivery_policy (feed only)

### 6.2 v1 Required Insight Categories

At least 5-10 Insight Types must ship, including cross-domain examples such as:

- Finance <-> Calendar: upcoming obligation vs projected balance risk
- Finance <-> Journal: spending spike correlated with stress mentions
- Journal <-> Habits: habit adherence improves after reflective entries
- Calendar <-> Relationships: long gap since last interaction with a person
- Calendar <-> Projects: project slippage correlated with late-night events
- Habits <-> Health (non-medical): sleep consistency improving alongside habit streaks

All wording must remain observational, not prescriptive.

---

## 7. Ranking & Delivery

### 7.1 Ranking Rules

- Deterministic ordering only
- Priority based on:
  - Relevance window
  - Confidence band
  - Novelty (not recently shown)
- No personalization

### 7.2 Delivery Policy

- Insight Feed only
- No notifications
- No banners
- No interrupts

Users must pull, not be pushed.

---

## 8. User Experience Requirements

### 8.1 Insight Presentation

Each insight must show:

- Clear summary (1-2 lines)
- "Based on" references (events/features)
- Plain-language explanation
- Confidence label (mapped from numeric)

### 8.2 User Actions

Users may:

- Dismiss
- Snooze
- Act (if CTA exists)

User actions must emit feedback events for future phases.

---

## 9. Data & Storage (DB)

**Minimum required tables (in addition to Phase 5a):**

- features_daily (or equivalent)

**Extended insights records with:**

- priority
- delivery_policy

No destructive updates to timeline or interpretations.

---

## 10. Team Responsibilities

### Architecture

- Approve Insight Types and rules
- Ensure cross-domain reasoning remains conservative
- Gate Phase 5c entry

### Backend

- Implement feature computation jobs
- Implement Insight Type registry execution
- Ensure idempotent insight generation

### Frontend

- Insight Feed UI enhancements
- Evidence + explanation rendering
- Clear system-derived labeling

### DB

- Feature storage schemas
- Indexing for time-window queries

### QA

- Golden fixtures for insight outputs
- Rule correctness tests
- Regression tests for trust guarantees

### DevOps

- Scheduled jobs for feature and insight runs
- Observability:
  - insight counts per type
  - dismiss / act rates
- Feature flags per Insight Type

### ML

- No active role
- Ensure future ML hooks do not leak into Phase 5b

---

## 11. Acceptance Criteria (Phase 5b Done)

Phase 5b is complete when:

- Feature computation runs deterministically
- At least 5 Insight Types ship, including cross-domain ones
- Insight Feed is consistently non-empty and useful
- Users interact with insights (dismiss / act)
- Rejection/dismiss rates are explainable
- No trust regressions or surprise behaviors are reported
- Architecture signs off readiness for Phase 5c

---

## 12. Exit Gate

Phase 5c (Personalization Scaffolding) may only begin if:

- Insight logic feels fair and predictable
- Users understand why insights appear
- The system demonstrates restraint

---

## Architectural Note

Phase 5b is where LifeOS proves it can connect the dots without overreaching.

If Phase 5a taught the system how to be wrong safely,
Phase 5b teaches it how to be useful without being clever.

This is the last phase where intelligence must earn trust purely through clarity.

---

## QA Verification (2025-01-11)

**Phase 5b Test Suite (required)**

Command:
```bash
python3 -m pytest lifeos/tests/test_phase5b_feature_service.py \
  lifeos/tests/test_phase5b_registry.py \
  lifeos/tests/test_phase5b_rules.py \
  lifeos/tests/test_insight_services.py \
  lifeos/tests/test_phase5b_ml_contracts.py
```
Result: ✅ 18 passed

**Seeded-data runner verification**

Seeded events for user `phase5b.qa@example.com` (user_id=11) and ran:
```bash
python3 /app/scripts/ops/phase5b_insight_runner.py --since-minutes 120 --limit 100 --user-id 11
```
Result: ❌ Runner crashed during insight persistence.
```
TypeError: 'EventRecord' object is not iterable
  at persist_insights(event, insights)
```
Notes: Features stored successfully; insight run failed. Feed population and duplicate suppression via runner are **blocked** pending fix in the runner call order.

**Duplicate suppression**

Validated via test coverage: `lifeos/tests/test_phase5b_rules.py::test_phase5b_rules_skip_duplicates` ✅

**Regression safety (Phase 3b/3c)**

Command:
```bash
python3 -m pytest lifeos/tests/test_phase_3b_api_contracts.py \
  lifeos/tests/test_phase_3b_dsd_alignment.py \
  lifeos/tests/test_phase_3b_read_only_guard.py \
  lifeos/tests/test_phase_3b_frontend_contract_errors.py \
  lifeos/tests/test_phase_3c1_read_cache_observability.py
```
Result: ✅ 16 passed (1 warning: SAWarning transaction rollback)

**Contract violations**

No contract violations detected in Phase 3b frontend contract error checks ✅

### QA Sign-off

Status: **BLOCKED**
Reason: Phase 5b runner crashes during insight persistence; feed non-empty verification cannot be confirmed until runner is fixed.

---

## DevOps Runtime Verification (Local)

**Timestamp:** 2025-12-26T18:35:34Z
**Environment:** local dev (`PYTHONPATH=.` with `.venv`)

**Runner (one-shot)**
```bash
PYTHONPATH=. ./.venv/bin/python scripts/ops/phase5b_insight_runner.py --mode both --since-minutes 60 --limit 500
```
Output:
- `phase5b: features stored for users=10 window_days=30`
- `phase5b: insights processed=0 emitted=0 since_minutes=60 limit=500`

**Observability snapshot**
```bash
PYTHONPATH=. ./.venv/bin/python scripts/ops/phase5b_insight_observability.py --since-hours 24
```
Output:
- Insight counts by type: `(no insights found)`
- Insight action counts: `(no insight actions found)`

**Phase 3b/3c metrics**
- Prometheus not reachable (`curl` to `http://127.0.0.1:9090/api/v1/query` failed, exit 7), so green checks not verified in this run.

**Status**
- Runner executes without error, feature computation runs.
- No insights persisted for the 60-minute window; likely requires seed data or broader window to trigger Phase 5b rules.
