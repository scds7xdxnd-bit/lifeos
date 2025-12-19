# Auth Copy & Layout Rules (Calm & Legible)

Purpose: enforce the canonical “calm & legible” auth experience while keeping backend/security unchanged.

## Panel Structure (UI contract)
- Two panels only.
- Left (Meaning): optional eyebrow “LifeOS”; one headline; one short orientation line (≤2 lines); exactly three standards (value statements). No buttons/forms/demo creds/technical terms.
- Right (Action): only Login and Register modes; one primary CTA (“Continue”); recovery as a low-contrast inline link (“Forgot password”). No extra tabs/actions/demo creds.
- Keep interaction density low; whitespace > controls; no persuasive/marketing tone.

## Allowed Copy Snippets
- Headlines: “Your life, made legible.” / “Everything is in place.” / “Welcome back.”
- Support: “Private by default.” / “Nothing changes without your intent.” / “Designed for long-term use.”

## Disallowed (user-facing)
- Technical vocabulary: JWT, CSRF, tokens, encryption, cookies, sessions, backend/internal docs.
- Meta copy about UX/mechanics.
- Doubt-raising questions or marketing fluff.

## Backend Guidance
- Do not change auth logic or security posture.
- Keep recovery endpoints (forgot-username/forgot-password/reset-password) stable; responses remain generic (no existence leaks).
- Avoid UI copy in responses; surface only neutral error codes (`bad_request`, `invalid_credentials`, `invalid_token`, `validation_error`).
- No new auth mechanisms; no token/cookie/device changes.

## QA Checklist
- Left panel: eyebrow (optional), 1 headline, 1 orientation sentence, exactly 3 standards, no controls.
- Right panel: only Login/Register tabs, one primary CTA, recovery inline/secondary; no extra actions.
- Copy free of technical terms/internal references.
- Accessibility: focus order, labels, contrast between primary vs recovery link.
- Functional regression: login, register, recovery flows unchanged; rate limits and CSRF behavior unchanged.

## DevOps/Security
- Verify no security mechanism details are exposed in UI/logs.
- No change to cookies/JWT/CSRF settings; monitoring unchanged.

## PR Checklist (Auth changes)
- Cite alignment with this document.
- Confirm no new technical terms in UI.
- Confirm action layout meets panel rules; recovery is secondary.
