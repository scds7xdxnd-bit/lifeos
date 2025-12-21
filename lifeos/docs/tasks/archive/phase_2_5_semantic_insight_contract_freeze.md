# LifeOS - Phase 2.5 Semantic & Insight Contract Freeze

Audience: Architecture, Backend, ML, QA, Product
Owner: Systems Architecture
Phase Context: Phase 2.5 (Pre-Hardening)
Status: Completed (Archived) / Phase 2.5 sign-off

---

## 1. Purpose
Phase 2.5 exists to freeze meaning before mechanism is hardened.

LifeOS is transitioning from:
- Feature correctness -> system truthfulness
- Isolated domains -> cross-domain intelligence

This phase defines and locks:
- What LifeOS claims to know
- What each domain represents
- How insights are formed and qualified
- What "confidence" means in human and system terms

No performance, scaling, ML optimization, or projection hardening is allowed in this phase.

---

## 2. Strategic Objective
Establish a stable semantic contract so future replay, determinism, telemetry, and ML attach to fixed meaning.

Phase 2.5 ensures that when LifeOS later becomes:
- deterministic
- replay-safe
- ML-assisted

...it is doing so against correct, agreed, and legible truth.

---

## 3. Scope (Strictly In-Scope)

### A. Domains Covered
All domains that emit events contributing to insights, including:
- Calendar
- Journal
- Finance
- Habits / Health (if present)
- System / Meta events

### B. Surfaces Affected
- Dashboards (read-only)
- Insight panels
- Review queues
- Internal insight pipelines

---

## 4. Core Principles (Non-Negotiable)
1) Meaning before math
   - Define semantics before confidence scores
   - Define claims before probabilities

2) Human-legible truth
   - Every insight must be explainable in plain language
   - No "black-box" conclusions

3) Conservatism
   - Prefer "review-only" over autonomous conclusions
   - Prefer omission over hallucination

4) Determinism-ready
   - All definitions must be replay-safe
   - Same inputs -> same outputs

---

## 5. Required Artifacts (Blocking Deliverables)

### 5.1 Domain Semantic Contracts
Each domain must produce a Semantic Contract defining:
- Domain purpose (one paragraph, human-readable)
- What events mean (not just what they contain)
- What the domain can assert
- What the domain must not infer

Example (illustrative only):
Calendar events represent declared intentions, not guaranteed behavior.

These contracts are binding for future work.
Canonical backend reference: `lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md`.

### 5.2 Event Semantics Freeze
For every event type:
- Define semantic meaning
- Define required fields
- Define optional fields
- Define versioning rules

Events must answer:
- What happened?
- When did it happen?
- Who asserted it?
- What certainty does it carry?

No event may be used for insights without a semantic definition.
Canonical backend reference: `lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md`.

### 5.3 Insight Contracts (Critical)
For every existing or planned insight, define an Insight Contract with:
- Insight name
- Human-readable description
- Required evidence (events + domains)
- Disallowed evidence
- Confidence bands
- Allowed system actions

Example structure:
- Insight: "Sustained schedule overload"
- Evidence: >= N overlapping calendar events across M days
- Confidence levels: low / medium / high
- Behavior:
- Low -> review-only
- Medium -> suggestion
- High -> highlight, never automate

No insight may exist without a contract.
Canonical backend reference: `lifeos/docs/semantics/INSIGHT_CONTRACTS.md`.

### 5.4 Confidence Vocabulary (System-Wide)
Define a shared confidence ontology, for example:
- Informational
- Suggested
- Needs Review
- Confirmed

Rules:
- No numeric probabilities in UI
- No autonomous actions without explicit user confirmation
- Confidence must be derivable deterministically
Canonical backend reference: `lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md`.

### 5.5 Cross-Domain Correlation Rules (Non-ML)
Define rule-based correlations only:
- Calendar <-> Personal Journal
- Finance <-> Stress / Mood (if present)
- Habits <-> Health

Rules must:
- Be explicit
- Be explainable
- Be reversible
- Avoid optimization or learning

ML is not allowed to invent correlations in this phase.

---

## 6. Explicit Non-Goals
Strictly forbidden in Phase 2.5:
- Projection optimization
- Replay hardening
- CQRS refactors
- ML model training or tuning
- Personalization
- Insight ranking
- UI redesign

If it improves speed or intelligence but not meaning, it is out of scope.

---

## 7. Team Responsibilities

### A. Architecture
- Own semantic consistency
- Resolve conflicts between domains
- Approve all contracts as canonical

### B. Backend
- Ensure event payload completeness
- Align emitters to semantic definitions
- Add tests enforcing required fields
- No projection changes

### C. ML / Data
- Define where ML may attach later
- Specify required logging fields:
  - model_version
  - payload_version
- No model training or inference changes
- ML canonical references:
  - lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md
  - lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md
  - lifeos/docs/semantics/INSIGHT_CONTRACTS.md
  - lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md

### D. QA
- Validate semantic contracts against real data
- Ensure insights never exceed allowed confidence behavior
- Test replay consistency at semantic level
- Verify review-only routing works
- QA canonical references:
  - lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md
  - lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md
  - lifeos/docs/semantics/INSIGHT_CONTRACTS.md
  - lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md

### E. Product / Documentation
- Publish:
  - Domain Semantic Contracts
  - Insight Contracts
  - Confidence Vocabulary
- These documents become reference law for LifeOS

---

## 8. Exit Criteria (Phase Gate)
Phase 2.5 is complete only when:
- All emitting domains have semantic contracts
- All insights have explicit contracts
- Confidence vocabulary is finalized
- No unresolved semantic ambiguity remains
- Architecture formally signs off

Phase 3a must not begin without this sign-off.

---

## 9. Architectural Note
Phase 2.5 defines what LifeOS believes to be true.
Phase 3a defines how reliably and efficiently it remembers and reasons about that truth.
Do not conflate the two.
