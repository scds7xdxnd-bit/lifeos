# LifeOS - Phase 4: Calendar Time-Canvas UI & Interaction Grammar

**Audience:** Architecture, Frontend, Backend, QA, DevOps, DB
**Owner:** LifeOS Architecture
**Preconditions:** Phase 3b, 3b.1, 3c-1 completed and signed off
**Status:** Verification-Complete (QA sign-off recorded)
**Nature:** User-facing UI/UX transformation (semantics frozen)

---

## 1. Situation & Justification

LifeOS has completed all prerequisite hardening phases:

- Interface contracts are frozen (Phase 3b)
- Semantics and confidence vocabulary are canonical (Phase 2.5)
- Domain UX surfaces are aligned and stabilized (Phase 3a.5)
- Read paths are scaled, cached, and verified under load (Phase 3c-1)

As a result:

- Read latency ceilings are known
- Determinism is proven
- Projection correctness is enforced
- Backend behavior is boring and reliable

This creates the first safe window to redesign a primary surface.

---

## 2. Purpose of Phase 4

**Transform the Calendar from a grid scheduler into a time canvas that matches Apple Calendar's visual grammar and interaction model, without changing meaning, data, or contracts.**

Phase 4 exists to improve:

- Temporal legibility
- Visual hierarchy
- Interaction ergonomics
- Density handling (all-day, multi-day, overflow)

It does not exist to:

- Add features
- Change semantics
- Introduce intelligence
- Reinterpret data

---

## 3. Definition of Done (Non-Negotiable)

Phase 4 is complete when:

1. The Calendar visually and behaviorally operates as a time canvas
2. All Apple-style reference behaviors are met:
   - De-emphasized grid
   - Translucent event cards with accent identity
   - Dedicated all-day track with spanning bars
   - Stable multi-day bars in month view
   - Overflow handling via "+N more"
3. No API, projection, or contract changes are required
4. No new correctness, determinism, or latency regressions appear
5. All Phase 3 metrics remain green throughout rollout

---

## 4. Scope (Strictly In-Scope)

### 4.1 Views Covered

- Day view (time canvas)
- Week view (time canvas + all-day row)
- Month view (dense multi-day bars)
- Event hover / quick-view popovers

### 4.2 Interaction Grammar

- Visual hierarchy
- Layout and stacking
- Overflow behavior
- Hover / selection states
- Navigation emphasis (Today / Prev / Next / View mode)

---

## 5. WHAT MUST NOT CHANGE (Hard Guardrails)

This section is binding.

### 5.1 Semantics (Frozen)

- Event meaning
- All-day vs timed rules
- Multi-day boundary logic
- Confidence semantics
- Review vs confirmed status

No reinterpretation is allowed.

### 5.2 Data & APIs (Frozen)

- Event schemas
- Calendar view/ledger APIs
- Recurrence expansion logic
- Timezone storage rules
- Projection payloads

No new fields. No renamed fields. No version bumps.

### 5.3 Backend Responsibilities (Frozen)

- No layout logic moves to backend
- No new precomputed geometry
- No UI-specific hints added to APIs

Backend remains render-agnostic.

### 5.4 Intelligence (Explicitly Forbidden)

- No ML
- No NLP quick-add
- No conflict detection
- No auto-rescheduling
- No smart suggestions

Phase 4 is visual and ergonomic only.

### 5.5 Performance Targets (Must Not Regress)

- Read p95 latency must not exceed Phase 3c-1 baselines
- Determinism failures must remain zero
- Projection correctness errors must remain zero

If a UI change causes regressions, it must be rolled back.

---

## 6. Target Architecture (UI-Only)

### 6.1 Layout Responsibility

**Client-side layout only.**

Rationale:

- Geometry is presentation-specific
- Keeps contracts stable
- Allows iteration without backend churn

### 6.2 Frontend Component Model

Canonical components (no one-off inventions):

- `CalendarHeader`
- `TimeCanvas`
- `AllDayTrack`
- `EventCard`
- `MultiDayBar`
- `OverflowPopover`
- `QuickViewPopover`

All components must use shared design tokens.

### 6.3 Design Tokens (Required)

- Grid line hierarchy (major/minor, low contrast)
- Event alpha / translucency
- Accent edge styling
- Typography hierarchy (Title > Meta)
- Radius, padding, spacing
- Dark / light parity

Tokens must be centralized.

---

## 7. Team-by-Team Responsibilities

### A. Frontend (Primary Owner)

**Scope**

- Full Calendar UI rewrite
- Apple-style visual grammar
- Layout algorithms

**Deliverables**

- New calendar components
- Overlap & stacking logic
- All-day track rendering
- Overflow handling
- Visual parity with reference screenshots

**Acceptance Criteria**

- Matches Apple-style behaviors
- No API changes
- Smooth interaction at scale

---

### B. Backend

**Scope**

- None, except support

**Deliverables**

- Contract stability
- Bug fixes only if exposed by UI (no feature changes)

**Acceptance Criteria**

- Zero contract diffs

**Backend Implementation Plan (Phase 4)**

- No code changes required for Phase 4 UI rollout.
- Maintain existing calendar view/ledger APIs unchanged.
- Preserve read-through cache behavior and invalidation (Phase 3c-1).
- If UI reveals a backend bug, patch minimally without altering contracts.

---

### C. DB

**Scope**

- None

**Deliverables**

- None

---

### D. QA

**Scope**

- Visual + behavioral verification

**Deliverables**

- View x event-type test matrix
- Visual regression snapshots
- Edge-case coverage:
  - DST
  - overlaps
  - overflow thresholds
  - multi-day spanning

**Acceptance Criteria**

- No visual regressions
- No correctness regressions

---

### E. DevOps

**Scope**

- Safe rollout

**Deliverables**

- Feature flag
- Staged rollout plan
- Monitoring during release

**Acceptance Criteria**

- Metrics remain green during rollout

---

### F. ML

**Explicitly Not Required**

- No ML participation in Phase 4

---

## 8. Milestones

### Phase 4.0 - Renderer Prototype

- Design tokens
- Static fixtures
- Time canvas proof

### Phase 4.1 - All-Day + Multi-Day

- All-day track
- Spanning bars
- Overflow logic

### Phase 4.2 - Month Density

- Stable multi-day bars
- Overflow behavior

### Phase 4.3 - Polish & QA

- Interaction polish
n- Accessibility
- Performance validation

Each milestone must keep contracts untouched.

---

## 9. Exit Criteria

Phase 4 is complete when:

- Calendar UI meets Apple-style parity
- No backend or semantic changes occurred
- Metrics remain boring
- Architecture signs off

---

## 10. Architectural Note

Phase 4 is where LifeOS becomes visually trustworthy.

The system already knows the truth.
Now it must look like it does.

Any change that threatens correctness, determinism, or meaning must be rejected, no matter how attractive.

Phase 4 succeeds only if it is beautiful, restrained, and boring underneath.
