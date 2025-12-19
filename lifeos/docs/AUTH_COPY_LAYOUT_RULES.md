# Auth Copy & Layout Rules (Binding)

## Purpose
Provide enforceable copy and layout constraints for LifeOS authentication surfaces. This document is canonical for Auth UX decisions and must be followed even if backend exposes more data.

## Scope
- Login
- Registration
- Password recovery/reset

## Copy Rules
### Intent
- Assert safety and readiness; emphasize control, clarity, continuity.
- Avoid selling or explaining mechanics.

### Allowed Patterns (examples)
- Headlines: "Your life, made legible." / "Everything is in place." / "Welcome back."
- Support: "Private by default." / "Nothing changes without your intent." / "Designed for long-term use."

### Disallowed
- Technical terms (JWT, CSRF, tokens, encryption).
- Internal references (constitutions, protocols, system notes).
- UX meta-commentary ("one clear primary action").
- Doubt-raising questions ("Is your account safe?").

## Layout Rules
### Overall
- Two-panel layout retained.
- One dominant action per screen; recovery is visually secondary.

### Left Panel (Meaning)
Order (must follow):
1) Optional eyebrow: "LifeOS"
2) One dominant headline
3) One short orientation sentence (<=2 lines)
4) Exactly three standards (value statements, not features)

Must not include:
- Buttons or forms
- Demo credentials
- Technical references
- Internal documentation links

### Right Panel (Action)
- Only Login and Register as primary modes (max two tabs).
- Single dominant CTA ("Continue").
- Recovery flow as low-contrast inline link.
- No side-by-side primary actions.
- No demo credentials inline.

## Component Rules
- Tabs: max two; Auth only.
- CTAs: one dominant per view; secondary actions are quiet links.
- Recovery: inline, low contrast; never primary.
- Status messages: calm, factual, non-technical.

## Acceptance Criteria
- Left panel contains only eyebrow/headline/orientation/three standards.
- Right panel contains only Login/Register mode and one primary CTA.
- No technical or internal references in user-visible copy.
- Cognitive load reduced: <=2 primary choices visible.

## Enforcement
- All Auth PRs must cite: "Aligned with Auth Copy & Layout Rules."
- QA must check for forbidden terms and layout violations.
