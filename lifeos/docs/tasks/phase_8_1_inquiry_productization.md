# LifeOS - Phase 8.1: Inquiry Productization and Decision-Useful Briefs

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps, ML (contracts-only)
**Owner:** LifeOS Architecture
**Preconditions:** Phase 8 complete and QA-approved
**Status:** Approved to Open
**Nature:** Productization of deterministic inquiry outputs (depth, not breadth)

---

## 1) Purpose

Phase 8.1 improves inquiry output usefulness without expanding inference breadth.

Goal:
- make briefs more decision-useful,
- keep deterministic evidence-bounded reasoning,
- preserve constitutional trust guarantees.

---

## 2) Problem this phase solves

After Phase 8, inquiry is structurally safe and correct but often commercially weak:
- over-emphasis on counts and internal framing,
- repetitive limitation language,
- generic refine suggestions,
- weak direct-answer quality for user intent.

Phase 8.1 addresses usefulness quality while retaining safety and determinism.

---

## 3) Binding constraints

- No chatbot behavior.
- No assistant-first interaction model.
- No runtime ML scoring or generation.
- No hidden personalization/ranking.
- No autonomous recommendations/actions.
- No timeline intelligence or causal modeling in this phase.
- No confidence vocabulary changes.

---

## 4) Productization scope

- Add deterministic direct-answer shaping above strategy outputs.
- Add deterministic evidence relevance prioritization.
- Add limitation deduplication/compression rules.
- Add answerability classification (strong / partial / weak) using deterministic evidence criteria.
- Add refine-guidance strategy that is specific and high-value, not generic.

---

## 5) Architectural placement

- Introduce an inquiry productization stage between strategy output and final brief serialization.
- Keep domain and cross-domain strategies intact as evidence/findings producers.
- Productization stage may:
  - reorder findings deterministically by relevance,
  - compress repeated caveats,
  - synthesize concise direct answers bounded by evidence,
  - emit answerability metadata.
- Productization stage must not alter evidence provenance or truth boundaries.

---

## 6) Quality model (binding dimensions)

Required quality dimensions:
- directness
- relevance
- evidence usefulness
- limitation clarity
- refine usefulness
- redundancy reduction
- answerability clarity

These dimensions become:
- product metrics,
- QA verification criteria,
- observability signals.

---

## 7) Semantic safety rules

- Answer quality must not be presented as truth certainty.
- Correlation must never be presented as causation.
- Context remains non-evidence unless independently supported by canonical records.
- Evidence references remain mandatory and visible.
- Productized language must remain non-therapeutic, non-clinical, non-judgmental.

---

## 8) Observability and rollout

Required metrics:
- direct-answer presence rate
- relevance/coverage quality distribution
- refine-after-weak-answer lift
- limitation redundancy rate
- productization error rate and latency

Rollout:
1. staging validation
2. canary by profile/version
3. production staged enablement

Rollback:
- disable productization stage flags while keeping core inquiry generation online.

---

## 9) Exit criteria

Phase 8.1 closes only when:
- inquiry briefs are materially more decision-useful under defined quality dimensions,
- determinism/replay parity is preserved,
- semantic safety and contract parity remain intact,
- observability and rollout gates are green.

---

## 10) Explicit non-goals

- No timeline intelligence foundations.
- No recommendation layer.
- No causal explanation layer.
- No expansion of inference breadth beyond existing Phase 8 strategy scope.
- No assistant/chat UX conversion.
