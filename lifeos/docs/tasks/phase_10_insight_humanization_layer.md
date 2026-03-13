# LifeOS - Phase 10: Insight Humanization Layer

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps, ML (advisory only)
**Owner:** LifeOS Architecture
**Preconditions:** Phase 9 complete and governance-aligned
**Status:** Approved to Open
**Nature:** Deterministic presentation transformation over canonical inquiry output

---

## SECTION 1 — Phase 9 Postmortem

### 1.1 What inquiry now does well
- Inquiry is now semantically disciplined, deterministic, evidence-bounded, and replay-safe.
- It can produce domain-specific, cross-domain, productized, and timeline-aware briefs without drifting into recommendation, causality, or prediction.
- It carries strong metadata, provenance, versioning, and auditability.
- It is structurally trustworthy.

### 1.2 What inquiry still fails to do well for ordinary users
- The output is still too long, too technical, and too dense for non-expert readers.
- Important meaning is often buried under categories, labels, caveats, metadata, and evidence structure.
- A normal user can still struggle to answer the simplest practical questions:
  - what happened,
  - why it matters,
  - how sure the system is,
  - what to review next.

### 1.3 Why technically correct output can still fail as product output
- Correctness guarantees truth discipline, not ease of understanding.
- A brief can be semantically perfect and still ask too much reading effort from the user.
- Product value depends on comprehension speed, not only semantic validity.

### 1.4 Why readability and interpretability are now the main bottleneck
- Inquiry is no longer mainly blocked on reasoning depth.
- The next bottleneck is translation from technically faithful output into ordinary-user-readable output.
- Until that translation exists, LifeOS will remain stronger as a system artifact than as a product surface.

### 1.5 Wrong next move
- The wrong next move is to add recommendations, causal explanation, or prediction before the system can reliably make existing insight understandable.
- That would compound unreadability with higher-stakes overreach.

### 1.6 Semantic correctness vs human comprehensibility
- Semantic correctness: the output faithfully reflects canonical evidence, boundaries, confidence, and limitations.
- Human comprehensibility: the user can quickly understand the answer without having to parse system-facing structure.
- Phase 9 solved more of the first.
- Phase 10 must solve the second without weakening the first.

---

## SECTION 2 — Phase Decision

### Decision
- Choose **A) Phase 10 — Insight Humanization Layer**.

### Why this is correct now
- The inquiry engine is now capable enough that readability is the dominant product bottleneck.
- Humanization directly improves value for ordinary users without expanding epistemic risk.
- Humanization can be done deterministically and audited against canonical output.

### Why the others are premature
- **Recommendation Layer Foundations** are premature because unreadable output makes advice harder to trust and easier to misuse.
- **Causal Explanation Layer** is premature because cause-language on top of already dense output will increase overclaim risk and user confusion.
- **Predictive / Forecasting Foundations** are premature because future-oriented outputs are higher stakes and should not be layered on top of a surface that still fails basic readability.

---

## SECTION 3 — Problem Definition

### 3.1 Product problem
- Current inquiry briefs still read like semantically careful system artifacts rather than calm user explanations.
- They contain too much machine-facing structure in the default reading path.
- Evidence transparency helps trust, but transparency by itself does not guarantee understanding.

### 3.2 Architecture problem
- If teams try to improve readability ad hoc in templates or strategy text, semantic drift will spread unevenly across inquiry types.
- LifeOS needs one shared, deterministic humanization layer with explicit equivalence rules.

### 3.3 Why current inquiry briefs are too technical
- Canonical section names are system-derived rather than user-derived.
- Metadata and guardrail structure are visible too early.
- Technical terminology is understandable to engineers but not ordinary users.
- Limitations and evidence details are correct but often framed in a way that sounds robotic.

### 3.4 Why metadata-heavy output is difficult for ordinary users
- It demands interpretation work the system should already be doing for presentation.
- It shifts the burden of translation onto the user.
- It obscures the main answer behind process details.

### 3.5 Why evidence transparency alone does not create understanding
- Showing evidence references proves grounding.
- It does not automatically explain why those references matter.
- Phase 10 must preserve evidence visibility while adding bounded explanation of significance.

### 3.6 Why this must be solved before recommendations or causality
- If users cannot easily understand the current descriptive layer, they should not be asked to trust higher-order interpretive layers.
- Humanization is the last required usability bridge before any more ambitious capability is safe to expose.

### 3.7 Definition: humanization in LifeOS terms
- Humanization is deterministic transformation of canonical inquiry output into simpler, shorter, clearer user-facing explanations.
- It does not mean:
  - hallucinated paraphrasing,
  - new inference,
  - assistant conversation,
  - recommendation logic,
  - semantic drift.
- It does mean:
  - bounded explanation of existing canonical content,
  - simpler phrasing,
  - clearer structure,
  - shorter presentation,
  - preserved meaning.

---

## SECTION 4 — Phase Goal

### Goal
- Add a deterministic humanization layer that transforms canonical inquiry briefs into user-readable explanations without changing the underlying semantic meaning, evidence boundaries, or confidence model.

### What gets better
- Shorter default inquiry output
- Clearer phrasing
- Better "why it matters" readability
- Lower metadata burden on the default surface
- Stronger ordinary-user comprehension

### What does not change
- Canonical inquiry reasoning
- Evidence selection
- Confidence vocabulary
- Timeline semantics
- Domain and cross-domain boundaries
- Auditability and replay requirements

### What remains forbidden
- New meaning
- Hidden evidence
- Advice or recommendation posture
- Causal or predictive wording
- Assistant/chat framing
- Runtime ML rewriting

---

## SECTION 5 — Canonical vs Humanized Output Model

### Decision
- LifeOS should have:
  - a canonical brief layer
  - a humanized brief layer

### 5.1 Canonical brief
- Purpose:
  - source of truth,
  - audit surface,
  - replay/debug surface,
  - QA comparison surface,
  - technical expansion surface in UI.

### 5.2 Humanized brief
- Purpose:
  - ordinary-user-readable default view,
  - calm explanation of what matters,
  - simpler structure over the same meaning.

### 5.3 Source of truth
- Canonical brief is the source of truth.
- Humanized brief is derived from canonical brief only.

### 5.4 Storage model
- Canonical brief must be stored.
- Humanized brief should be derived from canonical brief.
- Humanized output may be cached or materialized for performance, but only as a reconstructible derivative keyed by canonical brief hash and humanization version.

### 5.5 Default user visibility
- User sees the humanized brief by default.
- Canonical technical brief remains collapsed but accessible in the same inquiry surface.

### 5.6 Binding rules
- Humanization must not alter truth conditions.
- Humanization must not invent meaning.
- Humanization must not hide the existence of evidence.
- Humanization may reorder, compress, and simplify.

---

## SECTION 6 — Humanization Architecture

### 6.1 Placement in the pipeline
- Humanization comes after canonical inquiry assembly.
- In practice:
  - reasoning,
  - timeline interpretation,
  - canonical productization,
  - canonical brief persistence,
  - humanization transformation,
  - UI rendering.
- Humanization does not replace canonical reasoning.

### 6.2 Shared layer decision
- Humanization is a shared layer across all inquiry types.
- Domain and approved-pair adapters are allowed for phrasing specialization only.

### 6.3 Codebase location
```text
lifeos/core/insights/inquiry_humanization/
├── contracts.py
├── phrasebook.py
├── terminology.py
├── structure_compressor.py
├── section_prioritizer.py
├── duplication_reducer.py
├── evidence_explainer.py
├── assembler.py
└── adapters/
    ├── finance.py
    ├── habits.py
    ├── projects.py
    ├── skills.py
    ├── calendar.py
    ├── health.py
    ├── journal.py
    ├── relationships.py
    └── cross_domain/
```

### 6.4 Component responsibilities
- `contracts.py`: canonical-to-humanized contract types, hashes, mapping ids, version metadata
- `phrasebook.py`: approved plain-language phrases only
- `terminology.py`: technical-term substitution rules
- `structure_compressor.py`: shorter section/block rendering rules
- `section_prioritizer.py`: default order of humanized sections
- `duplication_reducer.py`: repeated caveat and metadata reduction
- `evidence_explainer.py`: deterministic "why this matters" text from canonical evidence roles
- `assembler.py`: produces final humanized brief
- `adapters/`: domain and approved-pair vocabulary/style overrides bounded to wording

### 6.5 Architectural constraints
- Deterministic template/rule-based only
- No free-form generative rewriting
- No hidden mutable phrasing
- No semantic recomputation
- No replacement of canonical inquiry as source of truth

---

## SECTION 7 — Semantic and Epistemic Rules

### 7.1 Allowed rewriting
- Shortening
- Plain-language substitution
- Section renaming
- Section reordering
- Duplication reduction
- Compression of non-essential technical metadata into expandable technical view
- Evidence-to-meaning explanation using pre-approved deterministic templates

### 7.2 Forbidden rewriting
- Adding motives, causes, or hidden intent
- Adding advice or recommendations
- Adding diagnosis or emotional interpretation
- Adding prediction or future expectation
- Intensifying confidence
- Removing material caveats
- Replacing specific evidence with vague claims
- Turning uncertainty into polished certainty

### 7.3 Required invariants between canonical and humanized output
- Same underlying claim set
- Same confidence ceiling
- Same limitation meaning
- Same evidence existence
- Same answerability status
- Same domain and cross-domain boundaries
- Same temporal boundaries

### 7.4 Binding equivalence rule
- Every humanized block must map to one or more canonical finding or limitation ids.
- If a humanized statement cannot be traced to canonical content, it is invalid.
- Humanization is a reversible explanation layer in audit terms, even if it is not textually reversible.

---

## SECTION 8 — Language Design Rules

### 8.1 Reading level and sentence style
- Target reading level: approximately grade 7 to 9.
- Sentences should be short, concrete, and neutral.
- Prefer one claim per sentence.
- Avoid stacked qualifiers and internal system jargon.

### 8.2 Terminology simplification policy
- Simplify technical terms when ordinary language preserves meaning.
- Keep technical terms only when they are legally or semantically necessary.
- If a technical term matters for traceability, move it to the expandable technical view.

### 8.3 Section naming policy
- Use plain section titles in the default surface.
- Technical taxonomy names belong in the technical brief, not the primary reading path.

### 8.4 Simple evidence description policy
- Evidence should be described in simple language such as:
  - "based on recent transaction records"
  - "based on logged habit entries"
  - "based on recent calendar events"
- The actual evidence links/refs must remain available.

### 8.5 Limitation language policy
- Limitations should sound plain and calm, not robotic.
- Example direction:
  - prefer "there is not much history for this pattern yet"
  - over "evidence coverage is insufficient for robust synthesis"

### 8.6 Confidence display policy
- Confidence remains canonical, but phrased simply.
- It should not sound fake-precise or overpolished.
- Confidence labels stay visible, but explanatory helper text may be simplified.

### 8.7 Technical term handling
- `canonical record`
  - primary surface: "record" or "saved record"
  - technical view: keep full term if needed
- `structural dependency observation`
  - primary surface: "these patterns show up together in the records"
  - technical view: retain taxonomy label
- `evidence coverage`
  - primary surface: "how much supporting history is available"
  - technical view: keep full term
- `profile version`
  - move to expandable technical view by default
- `synthesis`
  - primary surface: "combined reading" or "combined summary"
- `bounded pattern`
  - primary surface: "pattern seen in the selected time range"
- `event count`
  - primary surface: "how many times this was logged" when user-relevant

### 8.8 Visibility decisions
- Remain visible by default:
  - direct answer
  - plain-language findings
  - why it matters
  - confidence label
  - key evidence presence
  - limitations
  - what to review next
- Move into expandable technical view:
  - profile version
  - canonical finding categories
  - evidence ids and internal refs
  - hashes
  - source kinds
  - detailed count metadata
- Disappear from the primary reading surface:
  - internal taxonomy names
  - machine-facing serialization labels
  - system-oriented duplication

---

## SECTION 9 — UX / UI Model

### 9.1 Default pattern
- Human Insight is default visible.
- Technical Brief is collapsed but accessible in the same inquiry surface.

### 9.2 What the user sees first
- A short humanized answer
- Then plain-language sections:
  - What stands out
  - Why it matters
  - How sure this is
  - What to review next

### 9.3 Canonical brief access
- Canonical brief must not be removed.
- It should be collapsed, not hidden behind a separate workflow.
- Technical access must remain obvious and local to the inquiry surface.

### 9.4 Evidence traceability
- Humanized blocks must still link to evidence references.
- The user must never lose the ability to inspect support.

### 9.5 Read-first preservation
- Humanization should reduce reading burden, not increase UI complexity.
- Default view remains calm, brief-first, and non-chat.

### 9.6 Explicit anti-patterns
- No chat bubbles
- No assistant transcript interface
- No fake conversational framing
- No panel explosion
- No dashboard overload

---

## SECTION 10 — Domain and Cross-Domain Implications

### Decision
- Humanization should be **shared + domain + cross-domain adapters**.

### 10.1 Shared behavior
- All inquiry types use the same humanization pipeline, equivalence rules, and default section model.

### 10.2 Domain-specific customization
- Finance:
  - simplify accounting and ledger language
  - do not hide financial precision when it is materially relevant
- Habits:
  - simplify cadence/streak language
  - avoid moralizing tone
- Projects:
  - simplify throughput/slippage phrasing
  - avoid productivity-judgment framing
- Skills:
  - simplify practice-cadence language
  - avoid overclaiming improvement
- Calendar:
  - simplify scheduling pattern language
  - preserve distinction between planned and completed activity
- Health:
  - simplify descriptive metric language
  - do not become clinical
- Journal:
  - simplify reflective wording
  - avoid psychological interpretation
- Relationships:
  - simplify cadence wording
  - avoid relationship-quality inference

### 10.3 Cross-domain customization
- Cross-domain humanization may simplify pair-level observations and alignment language.
- It must not imply causality, dependency, or hidden mechanisms.

### 10.4 Where specialization stops
- Specialization may change wording, order, and examples.
- Specialization must not change:
  - claim meaning
  - evidence requirements
  - confidence semantics
  - limitation meaning

---

## SECTION 11 — Storage / Replay / Determinism Model

### 11.1 Persistence decision
- Canonical brief is persisted.
- Humanized brief is derived on demand.
- Humanized output may be cached/materialized for performance, but only as a deterministic derivative.

### 11.2 Versioning
- Humanization version must be explicit.
- Humanization version is part of replay identity.
- Humanized output must be byte-stable for the same:
  - canonical brief payload/hash
  - humanization version
  - locale/presentation mode if applicable

### 11.3 Auditability
- Canonical brief remains the audit artifact.
- Humanized output must record:
  - canonical brief hash
  - humanization version
  - humanized brief hash
- Audit trails must make it possible to prove which canonical brief produced which humanized rendering.

### 11.4 Prevented failure modes
- Hidden mutable rewriting
- Uncontrolled wording drift
- Semantic divergence between canonical and humanized output
- Non-replayable text changes

---

## SECTION 12 — Contract / Semantic / Docs Impact

### Required updates
- `lifeos/docs/lifeos_architecture.md`
  - add Phase 10 constitutional decision and layer placement
- `lifeos/docs/ui_ux_constitution.md`
  - define humanized default and technical expansion rules
- `lifeos/docs/semantics/INSIGHT_CONTRACTS.md`
  - add humanized brief contract and allowed/forbidden rewrite rules

### Additional updates needed
- `lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md`
  - yes, add a humanization equivalence rule
- `lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md`
  - yes, allow deterministic humanization metadata on existing inquiry lifecycle events

### No change by default
- `lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md`
  - no change

### New task document
- `lifeos/docs/tasks/phase_10_insight_humanization_layer.md`

---

## SECTION 13 — Non-Goals

- No assistant chat mode
- No recommendation engine
- No causal explanation engine
- No prediction / forecasting
- No emotional interpretation
- No hidden personalization
- No runtime ML scoring
- No semantic rewriting that changes truth conditions
- No new inference layer
- No hiding of the canonical technical brief

---

## SECTION 14 — Quality / Release Gates

### 14.1 Product criteria
- Humanized output is noticeably shorter and easier to scan than canonical output.
- Ordinary users can identify the main answer quickly.
- Default inquiry view feels calmer and less technical.

### 14.2 Semantic equivalence criteria
- Humanized output must preserve canonical meaning.
- Humanized output must not intensify confidence.
- Humanized output must not hide material caveats.
- Humanized output must remain evidence-traceable.

### 14.3 Readability criteria
- Reading level stays within target range.
- Technical jargon is materially reduced on the primary surface.
- Section naming is plain-language and stable.
- "Why it matters" text is understandable without becoming assistant-like.

### 14.4 QA requirements
- Canonical vs humanized equivalence fixtures
- term-simplification fixtures
- uncertainty-preservation fixtures
- evidence-traceability fixtures
- domain and approved-pair phrasing fixtures
- hidden-drift regression tests

### 14.5 Observability requirements
- humanization render latency
- fallback-to-canonical rate
- humanization equivalence violation counter
- technical-brief expansion rate
- refine-after-humanized-view rate

### 14.6 Rollout criteria
- staging validation
- canary on selected inquiry profiles
- production staged enablement
- rollback to canonical-default mode must remain available

### 14.7 Release blockers
- Humanized output changes meaning
- Humanized output hides uncertainty
- Evidence traceability becomes weaker
- Deterministic equivalence fails
- Technical brief access becomes too hidden or unavailable
- Humanized UI drifts into assistant/chat presentation

---

## SECTION 15 — Cross-Team Handoff Plan

### Backend
- Own the deterministic humanization pipeline and canonical-to-humanized mapping contracts.
- Must not introduce new inference or semantic rewriting.

### Frontend
- Own default humanized rendering, technical brief expansion, evidence visibility, and UI calmness.
- Must not introduce chat framing or hide canonical access.

### DB
- Own any additive persistence/cache support for humanization version/hash linkage.
- Must preserve replay and auditability.

### QA
- Own semantic-equivalence, uncertainty-preservation, evidence-traceability, and readability verification.
- Must treat meaning drift as a release blocker.

### DevOps
- Own rollout controls, observability, fallback-to-canonical mode, and version visibility.
- Must preserve rollback and build/version traceability.

### ML
- Advisory only.
- Review future-safe metadata and lineage needs without adding runtime rewriting or model scoring.

---

## SECTION 16 — Implementation Sequence

1. Architect ratifies the canonical vs humanized two-layer model.
2. Freeze equivalence rules and humanization boundaries.
3. Define the shared humanization layer and version contracts.
4. Update constitutional and semantic docs.
5. Implement backend deterministic humanization pipeline.
6. Implement frontend default humanized rendering with canonical expansion.
7. Add QA semantic-equivalence, readability, and traceability fixtures.
8. Add observability, rollout controls, and fallback mode.
9. Architecture signs off after semantic equivalence, UI stability, and replay safety all pass.

---

## Outcome

Phase 10 comes before recommendations, causality, or prediction because LifeOS must first make its existing insight understandable to ordinary users.

This phase materially increases product value by making canonical inquiry usable without weakening its evidence discipline.

It preserves constitutional discipline by keeping canonical output authoritative, humanized output deterministic, evidence visible, and semantic drift explicitly forbidden.

Canonical and humanized output should coexist as source-of-truth plus derived-reading-layer, not as competing truth surfaces.
