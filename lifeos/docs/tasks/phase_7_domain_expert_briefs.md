# LifeOS - Phase 7: Domain Expert Briefs

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps
**Owner:** LifeOS Architecture
**Status:** Complete (first-wave domains)
**Nature:** Deterministic domain-specific inquiry brief hardening

---

## 1) Purpose

Phase 7 introduces deterministic domain-expert brief profiles for Focused Inquiry, scoped to first-wave domains.

First-wave domains:
- Finance
- Habits
- Projects
- Skills

---

## 2) Binding constraints

- No chatbot behavior.
- No hidden personalization/ranking.
- No autonomous actions.
- No cross-domain expansion of domain-expert strategy behavior in this phase.
- No semantic reinterpretation of evidence or confidence vocabulary.
- Domain-expert outputs must remain deterministic for identical normalized input and `as_of_ts`.

---

## 3) Runtime expectations

- Domain strategy/profile metadata must be visible in inquiry brief payloads.
- Strategy/profile versions must be queryable for rollout safety.
- Existing inquiry lifecycle events remain authoritative:
  - `inquiry.requested`
  - `inquiry.context.submitted`
  - `inquiry.brief.generated`
  - `inquiry.brief.viewed`
  - `inquiry.refined`

---

## 4) Observability requirements

Phase 7 rollout must expose per-domain/profile-version signals for:
- inquiry generation latency
- inquiry error rate
- empty-brief rate
- low-coverage rate
- refine-after-low-quality rate
- quality state distribution

Per-domain checks must support first-wave domains without changing product semantics.

---

## 5) Rollout and rollback

- Rollout remains feature-gated by existing inquiry authority (`ENABLE_PHASE6_FOCUSED_INQUIRY`).
- Domain expert rollout is staged operationally by monitoring first-wave domain labels and profile versions.
- Rollback is performed by disabling focused inquiry and redeploying web runtime.

---

## 6) Exit criteria

Phase 7 operational readiness closes when:
- per-domain/profile-version signals are emitted and queryable,
- dashboards and alerts catch regressions with low false-positive noise,
- rollout checks are reproducible and include profile-version drift detection,
- rollback path is documented and verified.

---

## 7) Completion record

Phase 7 first-wave closure is recorded with:
- Deterministic domain expert briefs for:
  - Finance
  - Habits
  - Projects
  - Skills
- Domain strategy/profile metadata present and replay-stable.
- Domain-specific finding categories and limitation language verified by QA.
- Forbidden-claim guardrails validated for first-wave domains.
- DevOps per-domain/profile observability gates green.

Next phase: `phase_7_1_later_wave_domain_expert_briefs.md`
