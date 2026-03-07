# Task: Phase 1 UX Alignment Sprint (Legibility, Calm, Trust)
Status: Completed (Archived) | Owner: Architecture -> Frontend/Design, Backend, QA, DevOps/Security, Documentation/Product

## Strategic Objective
Align first-contact and core dashboards with LifeOS' philosophy: legible, calm, trustworthy. This sprint defines human-facing semantics before infra or ML work.

## In-Scope Surfaces
- **Auth**: login, registration, password recovery/reset

Dashboards (exactly three):
1) **Calendar Spine**: `lifeos/templates/calendar/index.html`
2) **Finance Overview**: `lifeos/templates/finance/dashboard.html`
3) **Insights/Review Queue**: `lifeos/templates/insights/index.html`

Justification:
- Calendar is the system's temporal spine and first-order navigation.
- Finance is the highest-stakes accountability surface (trust/clarity).
- Insights/Review queue is the system's guidance layer and cross-domain trust anchor.

## Non-Negotiable Principles
- Human-first language; no technical terms in user-facing copy.
- Legibility over density; remove elements that require explanation.
- Auth is a threshold (entering a place, not configuring a system).
- One dominant action per screen; secondary actions visually subordinate.
- Restraint: no marketing tone, no philosophical essays, no UI meta-commentary.

## Diagnosis (Architectural)
### Auth
- Technical or meta copy leaks into UI.
- Too many actions visible; recovery and alternate flows compete with entry.
- Left/right panel roles unclear; layout creates lateral competition and anxiety.

### Dashboards
- Treated like internal tools (CRUD emphasis), not truth surfaces.
- Users must infer meaning rather than being oriented.
- Copy explains mechanics instead of signaling state and next step.

### Systemic
- Tone and hierarchy inconsistent across surfaces.
- No enforceable copy/layout rules for Auth or dashboards.

## Required Improvements by Surface
### Auth (Login / Register / Recovery)
- Two-panel layout with meaning-left/action-right per Auth Copy & Layout Rules.
- One dominant CTA; recovery as low-contrast inline link.
- Remove technical and meta copy; replace with approved calm copy.
- No demo credentials or side-by-side primaries.

### Calendar Spine
- Single primary focus: "What's next and what needs confirmation?"
- Read-first summary block; actions secondary.
- Remove explanatory copy; replace with state signals and confidence cues.
- One dominant action (confirm/reject or create), not multiple competing CTAs.

### Finance Overview
- Single primary focus: "Where do I stand right now, and what changed recently?"
- Emphasize drift/variance summary; actions secondary.
- Remove dense tables from primary view; move to "review/manage."
- One dominant action (confirm/reclassify), not multiple primary CTAs.

### Insights/Review Queue
- Single primary focus: "What should I review now?"
- Prioritize review items; guidance secondary.
- No explanatory text for mechanics; use concise state signals.
- One dominant action (review/confirm), not multiple primaries.

## Component Rules (Sprint-Level)
- **CTAs**: one dominant per screen; secondary links muted and separated.
- **Tabs**: max two for Auth only (Login/Register); no additional tabs on dashboards.
- **Recovery flows**: inline/low-contrast; no modal-first or competing primary CTA.
- **Status messages**: factual, short, non-technical; no internal references.

## Team Deliverables
- **Frontend/Design**
  - Refactor Auth layout to two-panel spec; enforce hierarchy and action density.
  - Update Calendar/Finance/Insights dashboards to read-first, single-focus structure.
  - Implement CTA hierarchy and component rules (tabs, recovery, status).
- **Copy/Product**
  - Auth copy rewrite aligned with calm/legible rules.
  - Dashboard microcopy pass (headlines, labels, state cues).
  - Publish "Auth Copy & Layout Rules" doc (see `lifeos/docs/AUTH_COPY_LAYOUT_RULES.md`).
- **Backend**
  - No auth logic changes; ensure inline recovery works without UI coupling.
  - Confirm no copy dependencies in responses; frontend owns language.
- **QA**
  - Cognitive load checks (visible actions count).
  - UX regressions on auth and dashboards.
  - Accessibility: focus order, labels, contrast, clarity.
  - Verify no technical language in UI strings.
- **DevOps/Security**
  - Ensure no security mechanism details leak to UI/logs.
  - Security posture unchanged; monitoring/alerts intact.
- **Documentation/Governance**
  - Update guidelines to include human-first copy rules and UX restraint.
  - Reference this sprint as precedent-setting for future UI work.

## Acceptance Criteria (Sprint Complete)
- Auth: two-panel layout, one dominant CTA, recovery de-emphasized, no technical copy.
- Calendar/Finance/Insights: single primary focus, read-first summary, one dominant action.
- No technical/internal references in user-visible copy across scope.
- Visual hierarchy is calm and legible; density reduced.
- QA signoff on cognitive load, clarity, and accessibility.

## Non-Goals (Explicit)
- No performance or infra optimization.
- No ML/refinement work.
- No analytics expansion.
- No new features or UI novelty.

## Governance Artifacts
- `lifeos/docs/AUTH_COPY_LAYOUT_RULES.md` (binding)
- `lifeos/docs/ui_ux_constitution.md` remains authoritative; this sprint aligns with it.
