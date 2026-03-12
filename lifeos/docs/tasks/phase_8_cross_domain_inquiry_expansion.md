# LifeOS - Phase 8: Cross-Domain Inquiry Expansion

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps, ML (contracts-only)
**Owner:** LifeOS Architecture
**Preconditions:** Phase 7 and Phase 7.1 complete and QA-approved
**Status:** Complete (implemented and governance-approved)
**Nature:** Deterministic cross-domain synthesis (bounded, non-assistant)

---

## 1) Purpose

Phase 8 introduces deterministic cross-domain inquiry synthesis for approved domain pairs.

This phase exists to answer questions that single-domain expert briefs cannot answer safely:
- co-occurrence patterns
- temporal alignment between domains
- coverage/structural gaps across domains

---

## 2) Approved initial pair scope

Allowed in Phase 8:
- Finance + Habits
- Projects + Skills
- Journal + Habits
- Health + Habits
- Projects + Calendar
- Relationships + Journal

Not in scope:
- 3+ domain synthesis
- pair profiles requiring causal or clinical interpretation

---

## 3) Binding safety constraints

- No chatbot behavior.
- No omniscient assistant mode.
- No hidden personalization/ranking.
- No runtime ML scoring/generation.
- No autonomous action.
- No unsupported causal claims.
- No diagnosis, treatment recommendation, or psychological judgment.
- No intent inference about other people.

---

## 4) Allowed cross-domain claim categories

- `co_occurrence_observation`
- `temporal_alignment`
- `trend_alignment`
- `coverage_gap`
- `structural_dependency_observation`
- `inconsistency_flag`

Forbidden categories:
- psychological interpretation
- medical inference
- moral judgment
- intent inference of other people
- unsupported causal speculation

---

## 5) Architectural scope

- Add cross-domain strategy registry with pair-profile versioning.
- Add deterministic evidence aggregation layer across selected domains.
- Add deterministic synthesis rules engine with allowlisted claim categories.
- Keep single-domain strategy modules unchanged.
- Reuse inquiry lifecycle events; allow payload metadata enrichment for cross-domain profile/version if needed.
- Preserve inquiry read-first/non-chat rendering model.

---

## 6) Determinism and replay requirements

- Identical normalized input + timeframe + `as_of_ts` + profile version must produce identical output.
- Evidence ordering across domains must be deterministic.
- Synthesis rules must be static, versioned, and replay-auditable.
- Cross-domain brief hashes must be stable under replay.

---

## 7) Observability and rollout

Required per pair/profile metrics:
- generation latency
- error rate
- empty/low-coverage rate
- refine-after-low-coverage rate
- blocked unsafe-claim counters

Rollout order:
1. staging validation
2. pair-level canary
3. production staged enablement

Rollback:
- disable pair profiles (feature flags) without disabling single-domain inquiry.

---

## 8) Exit criteria

Phase 8 closes only when:
- approved pair profiles generate deterministic, evidence-referenced cross-domain briefs,
- forbidden claim classes are hard-blocked and QA-verified,
- contract and semantic parity is maintained,
- per-pair observability and rollout gates are green.

---

## 9) Explicit non-goals

- No timeline intelligence foundations.
- No predictive systems.
- No recommendation engines.
- No broad causal modeling.
- No assistant-first architecture.

---

## 10) Completion record

Phase 8 closure is recorded with:
- Deterministic cross-domain synthesis shipped for approved domain pairs.
- Cross-domain claim taxonomy and forbidden-claim guardrails verified by QA.
- Cross-domain replay determinism verified by profile/version.
- Per-pair observability and staged rollout controls validated by DevOps.

Next phase: `phase_8_1_inquiry_productization.md`
