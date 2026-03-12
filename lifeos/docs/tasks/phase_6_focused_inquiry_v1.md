# LifeOS - Phase 6: Focused Inquiry v1

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps, ML (stub only)
**Owner:** LifeOS Architecture
**Preconditions:** Phase 5c readiness gates complete
**Status:** Complete (implemented and semantically aligned)
**Nature:** User-facing meaning surface (bounded, evidence-first)

---

## 1) Purpose

Focused Inquiry v1 lets a user ask one scoped life question and receive one bounded, evidence-based brief.

This phase exists to make LifeOS useful as an inquiry system, not as a generic assistant.

---

## 2) Non-Negotiable Product Position

- LifeOS remains a personal evidence-based inquiry system.
- Focused Inquiry v1 is not a chatbot, not a dashboard, and not a feed replacement.
- Domain boundaries stay strict; cross-domain synthesis requires explicit evidence references.
- User-provided context is allowed but is not promoted to system evidence.

---

## 3) Canonical User Flow

1. User opens **Focused Inquiry** surface.
2. User defines inquiry question.
3. User selects lens: single domain or explicit cross-domain.
4. User selects timeframe.
5. User optionally adds context text.
6. User confirms and generates brief.
7. System returns brief with findings, evidence, confidence, and caveats.
8. User may refine and regenerate.
9. User may revisit prior generated briefs in inquiry history.

---

## 4) Output Contract (Brief-First)

Every inquiry brief must include:
- Summary (1-2 lines)
- Findings list
- "Based on" evidence references per finding
- Confidence label per finding (canonical vocabulary only)
- Uncertainty/caveat note when evidence is partial or mixed
- Explicit block for user context labeled as non-evidence

---

## 5) Semantic and Epistemic Rules (Binding)

- Evidence: canonical events/records/read models already valid under semantic contracts.
- Context: user-supplied framing only; never treated as fact unless independently supported.
- Interpretation: deterministic synthesis over bounded evidence.
- Recommendation: optional follow-up inquiry prompt only; never an autonomous action.
- Forbidden:
  - speculative diagnosis or psychology
  - unsupported cross-domain causality
  - hidden evidence substitution
  - confidence inflation

---

## 6) Domain Lens Expectations

- Finance: cashflow/obligation/variance questions grounded in ledger + schedules.
- Health: baseline/trend questions grounded in health records only.
- Habits: adherence/streak questions grounded in logs and cadence.
- Skills: practice/progression questions grounded in logged sessions/metrics.
- Projects: execution/slippage questions grounded in project/task records.
- Relationships: interaction-gap/cadence questions grounded in interactions/calendar links.
- Journal: reflective-pattern questions grounded in entries/tags/mood.
- Cross-domain: allowed only with explicit per-domain evidence references.

---

## 7) Backend and Data Requirements

- Add inquiry orchestration layer (request -> evidence query -> brief assembly -> persistence).
- Reuse existing read models and insight artifacts where valid; no semantic bypass.
- Add inquiry history storage (request metadata + generated brief + provenance refs).
- Emit inquiry lifecycle events defined in semantic freeze.
- Keep generation deterministic and replay-auditable.
- Cache inquiry reads only with deterministic keying and explicit invalidation.

---

## 8) Contract Updates Required

- `lifeos/docs/lifeos_architecture.md` (phase and constitutional authority)
- `lifeos/docs/ui_ux_constitution.md` (surface behavior)
- `lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md`
- `lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md`
- `lifeos/docs/semantics/INSIGHT_CONTRACTS.md`
- `lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md`
- API/DSD/readmodel contract files to be updated by backend architecture implementation PR

---

## 9) Explicit Non-Goals

- No general chatbot
- No omniscient assistant behavior
- No autonomous actions
- No hidden personalization/ranking
- No user context promoted to evidence
- No feed replacement

---

## 10) Exit Criteria

Phase 6 closes when all are true:
- Inquiry flow works end-to-end for at least one domain lens and one cross-domain lens.
- Findings are evidence-cited and confidence-labeled.
- Context is always shown as non-evidence unless independently corroborated.
- Replay and deterministic checks pass for inquiry generation.
- No constitutional/semantic violations introduced.

---

## 11) Completion record

Phase 6 closure is recorded with:
- Inquiry creation, detail, refine, and history/versioning implemented.
- Deterministic evidence-based brief assembly in production path.
- Inquiry lifecycle semantics aligned and enforced.
- Confidence/uncertainty/context labeling verified by QA.
