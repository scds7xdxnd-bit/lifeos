# Phase 12d HAB-018 QA Matrix (Recorded)

Generated: 2026-03-22
Source: [phase12d_habits_manual_qa_matrix.json](phase12d_habits_manual_qa_matrix.json)

## Scope
- Viewports: 375px, 414px, 768px, 1024px, 1440px
- Target page: /habits
- Checks attempted:
  - horizontal overflow
  - log/undo button presence and touch-target sizing
  - desktop detail-panel visibility
  - browser console errors

## Summary
- 5/5 viewport runs executed.
- Horizontal overflow: none detected at all tested widths.
- 422 blocker eliminated by stabilizing QA auth flow (token-seeded context).
- Touch targets now satisfy >=44px for primary actions and log/undo actions across all tested breakpoints.

## Recorded Results
| Viewport | Horizontal Scroll | Log Button Detected | Detail Panel Detected | Console Error |
|---|---:|---:|---:|---|
| 375x812 | No | Yes | No | None |
| 414x896 | No | Yes | No | None |
| 768x1024 | No | Yes | No | None |
| 1024x768 | No | Yes | Yes | None |
| 1440x900 | No | Yes | Yes | None |

## Assessment
- HAB-018 is passable based on scripted matrix evidence for:
  - no horizontal scroll at all required breakpoints
  - log/undo touch targets >=44px
  - primary action touch targets >=44px
  - desktop split behavior present at >=1024 and hidden below 1024
  - no console/network 422 errors during run

## Next Manual QA Actions
1. Capture animation frame-time measurements (<16ms target) using browser performance tooling.
2. Spot-check Korean/Chinese copy expansion at 375px and 414px for truncation.
3. Keep this matrix in CI once a formal Playwright test harness is introduced.

## Post-Matrix Update (HAB-023)
- Habit creation now opens as a centered Habit Studio modal with split form/reflection layout.
- Create-form terminology uses Frequency (not Schedule) in the modal.
- Preferred time input now uses 12-hour controls (hour, minute, AM/PM) and serializes to backend `scheduled_time`.
- Reflection/tip copy is localized across English, Korean, and Chinese with rotating encouragement every ~5s.
- Modal close affordances are backdrop click, Escape key, and Cancel button (top-right close icon removed).

### Additional QA Follow-up
1. Verify modal keyboard flow: tab order, Escape close, and focus return to trigger.
2. Verify 12-hour time selection serializes correctly for edge times (12:00 AM, 12:00 PM).
3. Re-run viewport checks for modal overflow/truncation at 375px, 414px, and 768px.
