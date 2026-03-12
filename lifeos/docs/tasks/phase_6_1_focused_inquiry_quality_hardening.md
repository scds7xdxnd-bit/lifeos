# LifeOS - Phase 6.1: Focused Inquiry Quality Hardening

**Audience:** Architecture, Backend, Frontend, QA, DevOps
**Owner:** LifeOS Architecture
**Status:** Open (quality hardening)

---

## 1) Purpose

Phase 6.1 hardens quality visibility for Focused Inquiry v1 without changing inquiry semantics.

---

## 2) Non-negotiable constraints

- No domain-truth reinterpretation.
- No chatbot behavior.
- No hidden product behavior change.
- No infrastructure redesign.
- Quality metadata is structural/evidence-derived only.

---

## 3) Operational visibility targets

Required operational tracking:
- low-coverage rate
- empty-brief rate
- refine-after-low-quality rate
- quality state distribution
- inquiry generation latency

---

## 4) Rollout expectations

- Feature-flagged rollout remains authoritative (`ENABLE_PHASE6_FOCUSED_INQUIRY`).
- Build identity remains visible through `/health` and `/api/bootstrap`.
- Rollout checks must verify metrics, alerts, and inquiry endpoint health.

---

## 5) Exit criteria

Phase 6.1 operational hardening closes when:
- quality metrics are emitted and queryable,
- dashboards/alerts are actionable,
- baseline alert noise is quiet,
- quality regressions trigger alerts,
- rollout checks are reproducible.
