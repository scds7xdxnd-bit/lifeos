# LifeOS - Phase 3a.5: Domain UX and Semantic Surface Alignment

Audience: Architecture, Frontend, Product, Backend, QA
Owner: Systems Architecture
Phase Context: Phase 3a.5 (Pre-Interface Freeze)
Status: Completed (Archived)

---

## 1. Purpose
Phase 3a.5 stabilizes all remaining user-facing domain surfaces before API schemas,
projections, and contracts are hardened in Phase 3b.

At this point:
- System semantics are frozen (Phase 2.5)
- Cross-domain intelligence is reliable and deterministic (Phase 3a)

However, many domain interfaces still leak instability through:
- unclear page purpose
- inconsistent interaction patterns
- ambiguous read/write boundaries
- UI-driven schema drift

Phase 3a.5 ensures what the user sees and how they interact with it becomes stable,
so Phase 3b can safely lock interfaces without rework.

---

## 2. Strategic Objective
Stabilize human-facing domain semantics so interface contracts can be frozen without regret.

This phase defines:
- what each domain page is
- what it claims
- what actions are allowed
- what is read-only vs editable
- how confidence and review appear in the UI

This is not a visual redesign phase. This is semantic and interaction consolidation.

---

## 3. Scope (Strictly In-Scope)

### A. Domains Covered
All remaining first-class LifeOS domains and sub-pages, including:
- Habits
- Relationships
- Skills
- Health
- Journal
- Projects
- Profile

Finance (all sub-surfaces):
- Finance / Journal
- Finance / Trial Balance
- Finance / Receivables
- Finance / Forecast
- Finance / Import

No domain may be skipped.

---

## 3.1 Domain Prioritization Order (Execution Rule)

Guiding criteria (in order):
1) Schema blast radius (APIs, projections, insights depending on the domain)
2) Cross-domain coupling (feeds or constrains other domains)
3) Semantic ambiguity risk (risk of later contract changes)
4) User trust impact (damage from inconsistency or confusion)

Domains that are upstream, coupled, and semantically fragile must be stabilized first.

### Tier 0 - Absolute prerequisites
1) **Profile**
   Goal: Freeze "who the user is" and "what defaults apply everywhere."
2) **Journal (core, non-finance)**
   Goal: Establish journal as a truth record, not a dumping ground.

### Tier 1 - Temporal and intent drivers
3) **Projects**
   Goal: Clarify projects as containers of sustained intent.
4) **Habits**
   Goal: Habits as observed patterns, not moral judgments.

### Tier 2 - Interpretive and sensitive domains
5) **Health**
   Goal: Health as reported or correlated signals, never conclusions.
6) **Relationships**
   Goal: Relationships as contextual metadata, not scores.

### Tier 3 - Skill and capability surfaces
7) **Skills**
   Goal: Skills as descriptive state, not certification.

### Tier 4 - Finance (must be done as a group)
8) **Finance / Journal**
9) **Finance / Trial Balance**
10) **Finance / Receivables**
11) **Finance / Forecast**
12) **Finance / Import**

Finance goal: Make finance boring, explicit, and unambiguous - never clever.

Hard rule: Do not start a lower tier until all higher tiers have signed Domain Surface Definitions.

---

## 4. Core Principles (Non-Negotiable)
1) Single-purpose surfaces
   - Every page must have one primary reason to exist

2) Read-first bias
   - Observation precedes action
   - Editing is intentional, not ambient

3) Explicit authority
   - Pages must never imply certainty beyond their domain contract

4) Consistency over novelty
   - Shared interaction patterns across domains
   - No one-off UX inventions

5) Stability over completeness
   - Prefer removing ambiguous features over keeping unstable ones

---

## 5. Required Deliverables (Blocking)

### 5.1 Domain Surface Definition (Per Page)
For each domain page, produce a Domain Surface Definition containing:
- Page purpose (1-2 sentences)
- Primary question the page answers
- Primary user action (if any)
- Read-only vs editable sections
- Relationship to Insight Contracts (if applicable)

This document is binding.

### 5.2 Interaction Pattern Normalization
Across all domains, standardize:
- Edit entry points (explicit "Edit", never ambient)
- Save / cancel behavior
- Empty states
- Review / confirmation states
- Error and uncertainty signaling

No domain may invent its own interaction grammar.

### 5.3 Copy and Language Alignment
Perform a copy pass to ensure:
- No technical language
- No internal system references
- No speculative or persuasive tone
- No over-explaining

Copy must:
- describe what is shown
- not justify why it exists
- not describe how it works

### 5.4 Read / Write Boundary Enforcement
For every page, explicitly define:
- Which data is:
  - read-only
  - user-editable
  - system-derived
- Which edits require:
  - confirmation
  - review
  - justification (if any)

UI must reflect these boundaries visually and behaviorally.

### 5.5 Confidence and Review Presentation
Where insights or derived data appear:
- Confidence vocabulary must match Phase 2.5
- Low-confidence items must surface as:
  - suggestions
  - review-only
- No implied certainty
- No auto-actions

This applies even outside the main insight feed.

### 5.6 Schema Shape Stabilization (Human-Facing)
While Phase 3b will formalize API schemas, Phase 3a.5 must:
- Stabilize human-visible data shape
- Reduce field churn caused by UI iteration
- Remove experimental or unused fields

After this phase, page-level data structures should not change without explicit
architectural review.

---

## 6. Explicit Non-Goals
Strictly forbidden in Phase 3a.5:
- API versioning
- Backward-compatibility guarantees
- Projection refactors
- Performance tuning
- ML behavior changes
- New insights
- Visual re-branding

If it changes contracts, it belongs in Phase 3b.

---

## 7. Team Responsibilities

### A. Architecture
- Own semantic consistency across domains
- Approve Domain Surface Definitions
- Gate Phase 3b entry

### B. Frontend
- Implement normalized interaction patterns
- Remove ambiguous UI states
- Align layouts to read-first principles
- Ensure visual cues match authority boundaries

### C. Product
- Author Domain Surface Definitions
- Resolve conflicts between domain meanings
- Approve copy changes
- Ensure user intent is correctly assumed

### D. Backend
- Support stabilized data shapes
- Remove legacy fields no longer surfaced
- Avoid schema changes during this phase unless approved

### E. QA
- Validate page purpose clarity
- Verify read/write boundaries
- Test confidence presentation
- Ensure no domain over-claims certainty

---

## 8. Exit Criteria (Phase Gate)
Phase 3a.5 is complete only when:
- Every listed domain has a signed Domain Surface Definition
- Interaction patterns are consistent across domains
- Copy is aligned and free of system leakage
- Human-visible data shapes are stable
- Architecture formally approves readiness for Phase 3b

Phase 3b must not begin without this sign-off.

---

## 9. Architectural Note
Phase 3a.5 is where LifeOS stops changing its mind in public.

After this phase:
- Interfaces are stable
- Semantics are visible
- Contracts can be frozen safely

This phase protects you from expensive regret later.

---

## 10. Domain Surface Definition (DSD) Template

**Domain:**
**Surface / Page Name:**
**Owner:**
**Phase:** 3a.5 - Domain UX and Semantic Surface Alignment
**Status:** Draft / Reviewed / Approved
**Last Updated:**

---

### 1. Purpose (Non-Negotiable)
In one or two sentences, state why this page exists.
- What human need does this surface serve?
- Why does LifeOS need this page at all?

This must be understandable to a non-technical user.

---

### 2. Primary Question Answered
This page answers the following primary question:
> "__________________________________________?"

Rules:
- Exactly one primary question.
- If there are multiple, the page must be split or simplified.

---

### 3. Intended User State
When a user arrives at this page, they are likely:
- ☐ Observing
- ☐ Reviewing
- ☐ Deciding
- ☐ Editing
- ☐ Correcting
- ☐ Reflecting

Select one dominant state.

---

### 4. Primary Action (If Any)
Primary action on this page (if applicable):
- Action name:
- Trigger mechanism (button / link / inline / none)

Rules:
- Zero or one primary action only.
- If there is no primary action, explicitly state "Read-only surface".

---

### 5. Read / Write Boundary

#### 5.1 Read-Only Sections
List sections or data that are:
- system-derived
- historical
- observational

These must not appear editable in the UI.

#### 5.2 User-Editable Sections
List sections or data that users may change.

For each editable section:
- Edit entry point (explicit)
- Save / cancel behavior
- Confirmation required? (Yes / No)

---

### 6. Authority and Confidence Constraints
This surface is allowed to assert:
- (What claims are valid here)

This surface must NOT assert:
- (What claims would exceed domain authority)

Confidence rules:
- ☐ Informational only
- ☐ Suggestive
- ☐ Review-only
- ☐ Confirmed (never autonomous)

This must align with Phase 2.5 Confidence Vocabulary.

---

### 7. Relationship to Insights (If Applicable)
- Does this surface display insights? (Yes / No)
- Does it generate evidence for insights? (Yes / No)

If yes:
- Which Insight Contracts does it touch?
- Is the surface authoritative or contributory?

---

### 8. Data Shape (Human-Facing)
List the human-visible data fields on this page.

For each field:
- Name (human label)
- Meaning (plain language)
- Source:
  - ☐ User-entered
  - ☐ System-derived
  - ☐ Imported
- Stability expectation:
  - ☐ Stable
  - ☐ Likely to change (must justify)

After Phase 3a.5, fields marked "Stable" should not change without architectural review.

---

### 9. Interaction Patterns Used
Select all that apply (must match system-wide patterns):
- ☐ Explicit Edit Mode
- ☐ Inline Confirmation
- ☐ Review Queue Integration
- ☐ Read-First Layout
- ☐ Progressive Disclosure
- ☐ Empty State Guidance

No custom interaction patterns allowed.

---

### 10. Explicit Non-Goals for This Surface
List behaviors or interpretations this page must never attempt.

Examples:
- No prediction
- No scoring
- No ranking
- No automation
- No persuasion

---

### 11. Open Questions / Risks
List any unresolved issues that could:
- cause schema churn
- break contracts
- confuse users
- require follow-up decisions

This section must be empty before approval.

---

### 12. Approval
- Product: ☐ Approved
- Architecture: ☐ Approved
- Frontend: ☐ Reviewed
- QA: ☐ Reviewed

Approval Date:

---

## Architectural Note
Once approved, this Domain Surface Definition becomes:
- the semantic authority for this page
- the UX reference for Phase 3b
- the guardrail against future regression

Changing this document after Phase 3a.5 requires explicit architectural sign-off.
