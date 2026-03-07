# Task: Auth Experience Refactor (Calm & Legible, Threshold-First)
Status: Completed (Archived) · Owner: Architecture → Frontend/Design, Backend, QA, DevOps/Security, Documentation/Product

## Purpose
Refactor the authentication experience to align with LifeOS principles of calm, legibility, trust, and continuity. Remove engineer-speak and meta-commentary, enforce a threshold-style entry (not a control panel), and establish clear copy/interface boundaries.

## Canonical Direction (Non-Optional)
- Direction: Calm & Legible (no alternative stylistic mixes).
- Human-first language; no technical vocabulary user-facing.
- Auth is a threshold: left = meaning/reassurance, right = action only.
- One dominant action; recovery is visually secondary.
- Restraint: fewer elements, more whitespace; no marketing tone.

## Interface Arrangement Rules
- Two-panel layout retained.
- Left (Meaning): optional eyebrow “LifeOS”; one headline; one short orientation sentence (≤2 lines); exactly three standards (value statements). No buttons/forms/demo creds/technical references.
- Right (Action): only Login/Register modes (max two tabs); one dominant CTA (“Continue”); recovery (“Forgot password”) as low-contrast inline link. No side-by-side primaries; no demo creds inline.

## Copy System (Must Follow)
- Allowed headline patterns: “Your life, made legible.” / “Everything is in place.” / “Welcome back.”
- Allowed support: “Private by default.” / “Nothing changes without your intent.” / “Designed for long-term use.”
- Disallowed: JWT/CSRF/tokens/encryption terms; internal references (constitutions/protocols); UX explanations; doubt-raising questions.

## Deliverables by Team
- **Frontend/Design**: Refactor auth screen to two-panel spec; enforce hierarchy; remove technical/meta copy; implement tabs (Login/Register only), single primary CTA, recovery as inline link; reduce interaction density; no extra buttons or demo creds.
- **Backend**: Keep auth logic/security unchanged; ensure recovery endpoints support inline/modal presentation; avoid coupling copy to backend responses.
- **QA**: Validate action count (only Login/Register primary, recovery secondary); ensure no technical terms in UI; regression on login/register/recovery; accessibility (focus order, labels, contrast); verify left panel content rules and right-panel constraints.
- **DevOps/Security**: Confirm security posture unchanged; ensure no security mechanism details exposed in UI/logs; monitoring/alerts unaffected.
- **Documentation/Product**: Publish “Auth Copy & Layout Rules”; record canonical copy and disallowed vocab; add PR checklist item: cite alignment with Auth Copy & Layout Rules for any Auth change.

## Acceptance Criteria
- Left panel: eyebrow (optional), one headline, one short orientation line, exactly three standards; no controls.
- Right panel: Login/Register only; one primary CTA; recovery as low-contrast inline link; no extra tabs/actions/demo creds.
- No technical/internal references in user-visible copy.
- Auth flows functionally unchanged; security posture unchanged.
- Cognitive load reduced: ≤2 primary choices visible; copy is calm, declarative, non-persuasive.

## Non-Goals
- No new auth mechanisms or token changes.
- No marketing/persuasive tone.
- No mobile/offline scope changes; no device/browser heuristics.

## Handoff Notes
- Frontend/Design: implement layout and copy per above; submit PR citing sections.
- Backend: verify endpoints already support required flows; no changes unless blocking UI presentation.
- QA: add tests/checklists per acceptance criteria.
- DevOps/Security: verify no leaks; posture intact.
- Documentation/Product: update guidelines and checklists; ensure future Auth changes reference this task.

## Canonical Calm & Legible Auth Refactor Plan (Contract; no code specified)

### Core Issues (to eliminate)
- Engineer-speak and meta-commentary in UI copy; technical terms visible to users.
- Control-panel feel: too many options, tabs, and actions; heavy cognitive load.
- Navigation and meaning blended; left/right panels lack clear roles.
- Recovery flows and secondary actions compete with primary entry.
- Auth feels like setup/config, not entry into a place.

### Direction (Decision, not options)
- Canonical approach: Calm & Legible.
- Human-first language; no technical vocabulary user-facing.
- Auth is a threshold: left = meaning/reassurance, right = action only.
- One dominant action; recovery is visually secondary.
- Restraint: fewer elements, more whitespace; no marketing tone.

### Copy System (must follow)
- Intent: assert safety/readiness; emphasize control, clarity, continuity; no selling or mechanic-explaining.
- Allowed patterns (examples):
  - Headlines: “Your life, made legible.” / “Everything is in place.” / “Welcome back.”
  - Support: “Private by default.” / “Nothing changes without your intent.” / “Designed for long-term use.”
- Disallowed: JWT/CSRF/tokens/encryption terms; internal references (constitutions/protocols); UX explanations; doubt-raising questions.

### Interface Arrangement (must follow)
- Two-panel layout retained.
- Left (Meaning) in order:
  - Optional eyebrow: “LifeOS”
  - One dominant headline
  - One short orientation sentence (≤2 lines)
  - Exactly three “standards” (value statements, not features)
  - Must not include buttons/forms/demo creds/technical references/docs.
- Right (Action):
  - Only Login and Register as modes (max two tabs).
  - One dominant CTA (“Continue”); recovery (“Forgot password”) as low-contrast inline link.
  - No side-by-side primary actions; no demo creds inline.
- Overall: no more than two visible primary choices; recovery de-emphasized.

### Team-Specific Deliverables
- **Frontend / Design**
  - Issues: Control-panel density, technical copy leaks, mixed meaning/action, recovery competing with primary CTA.
  - Deliverables: Refactored layout to two-panel spec; enforce left/right roles. Tabs: max two modes (Login/Register), no extra tabs. CTA hierarchy: one dominant CTA; recovery inline low-contrast. Remove technical/meta copy; inject approved calm copy. Reduce interaction density: no extra buttons, no side-by-side primaries. Visual hierarchy: whitespace, clear headline, subdued standards list; no marketing gloss.
- **Backend**
  - Issues: Coupling copy to backend, blocking UI changes.
  - Deliverables: No change to auth logic or security posture. Ensure endpoints support inline/modal recovery flows without UI coupling. Keep responses free of technical jargon intended for UI; frontend owns copy.
- **QA**
  - Issues: Cognitive load, copy leaks, auth regressions.
  - Deliverables: Validate visible actions count (Login/Register primary, recovery secondary). Verify no technical terms in UI strings. Regression: login, register, password reset, CSRF/rate-limit unchanged. Accessibility: focus order, label clarity, readable copy, primary vs secondary contrast. Clarity: left panel has headline + one orientation sentence + exactly three standards; right panel limited to action + recovery link.
- **DevOps / Security**
  - Issues: Security details exposed; posture drift.
  - Deliverables: Confirm no security mechanism details exposed in UI/logs/feature flags. No change to cookie/JWT/CSRF settings; monitor for leakage. Ensure monitoring/alerts unchanged; auth telemetry intact.
- **Documentation / Product**
  - Issues: Lack of enforceable guidance.
  - Deliverables: Update internal guidelines: “Auth Copy & Layout Rules” with human-first copy, restraint, panel roles. Document canonical copy snippets and disallowed vocab. Record interface rules: left = meaning only; right = action only; max two modes; one primary CTA; recovery de-emphasized. PR checklist: cite “Aligned with Auth Copy & Layout Rules” for any Auth change.

### Acceptance Criteria (all teams)
- Left panel: eyebrow (optional), one headline, one short orientation line, exactly three standards; no controls.
- Right panel: Login/Register only; one primary CTA; recovery as low-contrast inline link; no extra tabs/actions/demo creds.
- No technical or internal references in user-visible copy.
- Auth flows unchanged functionally; security posture unchanged.
- Cognitive load reduced: ≤2 primary choices visible.
- Copy tone: calm, declarative, no persuasion, no explanations of UX mechanics.

### Non-Goals
- No new auth mechanisms or token changes.
- No marketing flare or persuasive tone.
- No mobile/offline scope changes.
- No device/browser heuristics.

### Handoff Summary
- Frontend/Design: Rebuild layout to spec; apply canonical copy; enforce hierarchy and density constraints.
- Backend: Keep logic/security stable; ensure recovery endpoints usable inline; avoid UI copy leakage.
- QA: Validate layout rules, copy cleanliness, action counts, accessibility, and auth regressions.
- DevOps/Security: Confirm posture unchanged; no leaks of mechanisms in UI/logs.
- Documentation/Product: Publish and enforce “Auth Copy & Layout Rules” for all future Auth changes.
