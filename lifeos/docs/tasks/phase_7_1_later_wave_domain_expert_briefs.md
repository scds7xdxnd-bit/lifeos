# LifeOS - Phase 7.1: Later-Wave Domain Expert Briefs

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps, ML (contracts-only)
**Owner:** LifeOS Architecture
**Preconditions:** Phase 7 first-wave complete and QA-approved
**Status:** Complete (later-wave domains delivered)
**Nature:** Deterministic domain depth expansion (high-semantic-risk domains)

---

## 1) Purpose

Phase 7.1 expands deterministic domain expert briefs to later-wave domains while preserving semantic safety.

Later-wave domains:
- Journal
- Relationships
- Health

This phase deepens domain coverage without introducing cross-domain expert synthesis.

---

## 2) Why this phase exists

After Phase 7, LifeOS has strong expert depth in structured domains but incomplete expert coverage in semantically sensitive domains.

Phase 7.1 closes that gap through strict, bounded, deterministic strategies.

---

## 3) Binding constraints

- No chatbot behavior.
- No omniscient assistant mode.
- No hidden personalization or ranking.
- No autonomous action or recommendation execution.
- No runtime ML scoring or generation.
- No cross-domain expert synthesis expansion in this phase.
- Determinism and replay equivalence are non-negotiable.

---

## 4) Domain safety model

### Journal
- Allowed:
  - Explicit tag/mood/time-window summaries
  - Reflection cadence and recurrence summaries
- Forbidden:
  - Psychological diagnosis
  - Hidden-intent inference
  - Personality labeling

### Relationships
- Allowed:
  - Interaction cadence/recency summaries
  - Channel/method distribution summaries from explicit logs
- Forbidden:
  - Relationship quality judgments
  - Intent inference about other people
  - Moral scoring of social behavior

### Health
- Allowed:
  - Descriptive baseline/trend summaries from recorded metrics
  - Coverage and consistency summaries
- Forbidden:
  - Medical diagnosis or treatment suggestion
  - Clinical risk claims beyond recorded descriptive evidence

---

## 5) Architectural scope

- Add deterministic strategy modules for Journal, Relationships, Health.
- Extend inquiry brief contract metadata with later-wave domain profile/version categories.
- Add strict allowed-claim and forbidden-claim enforcement per later-wave domain.
- Reuse existing inquiry lifecycle events; enrich payload metadata only if required.
- Preserve inquiry flow and read-first rendering model.

---

## 6) Observability requirements

Per later-wave domain/profile version, expose:
- inquiry generation latency
- inquiry error rate
- empty-brief and low-coverage rates
- refine-after-low-quality rate
- forbidden-claim block counters

Dashboards and alerts must support Journal, Relationships, and Health independently.

---

## 7) Exit criteria

Phase 7.1 closes only when:
- Later-wave domain briefs are deterministic and replay-stable.
- Domain-specific forbidden claims are hard-blocked and verified by QA fixtures.
- Per-domain observability gates are green in staged rollout.
- No semantic drift is introduced in confidence vocabulary or evidence boundaries.

---

## 8) Explicit non-goals

- No cross-domain expert synthesis expansion.
- No timeline intelligence foundations.
- No broad causal reasoning.
- No assistant-first interaction model.

---

## 9) Completion record

Phase 7.1 closure is recorded with:
- Deterministic domain expert strategies shipped for:
  - Journal
  - Relationships
  - Health
- Later-wave forbidden-claim guardrails verified by QA.
- Profile/version metadata and replay determinism validated.
- Per-domain observability gates green in staged rollout.

Next phase: `phase_8_cross_domain_inquiry_expansion.md`
