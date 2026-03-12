# Confidence Vocabulary (Phase 2.5)

Canonical confidence terms used across events and insights. No numeric probabilities in UI.

## Vocabulary
- informational: factual, non-prescriptive status or record.
- suggested: system suggestion without commitment; never auto-acts.
- needs_review: review-only; user confirmation required.
- confirmed: explicit user/system-confirmed fact; safe to display as final.

## Rules
- No autonomous actions without explicit user confirmation.
- Confidence must be derivable deterministically.
- Confidence labels are human-legible and consistent across domains.

## Focused Inquiry Usage Rules (Binding)
- Inquiry findings must use only the canonical vocabulary above.
- User-provided context must never be assigned a confidence label as if it were system evidence; it must be labeled as user context.
- If a finding combines confirmed evidence with unconfirmed/interpretive material, the finding confidence is capped at `needs_review`.
- No numeric probability may be shown for inquiry findings.

## ML Scope
- Treat `confirmed` as strong labels; `needs_review` and `suggested` are weak labels unless explicitly confirmed downstream.
- Do not emit numeric probabilities in UI surfaces; map any internal scores to this vocabulary before exposure.
- Preserve confidence labels during replay and projection; ML must not rewrite or reclassify historical confidence.

## QA Scope
- Verify UI and API surfaces emit only the canonical vocabulary (no numeric probabilities).
- Ensure review_only routing is applied to needs_review items.
- Check that confidence labels remain stable across replay/projection.
