# Calendar ML Consumption (Deterministic Views & Ledger)

Purpose: give ML/analysis code a stable, replayable interface to the refactored calendar views without depending on UI filters.

What to use
- `window_streams.py`: `day_slice_for_ml`, `week_slice_for_ml`, `month_slice_for_ml`, and `ledger_slice_for_ml` wrap the backend-owned window/ledger logic. Each returns a dataclass with `projection_version` (v1) so we can bump if overlap/spillover rules change.
- Inputs are pure time windows/cursors; no source/tag filters are applied. Outputs mirror the canonical service responses (`events`, `window_start`, `window_end`, `spillover_days` for month; ledger cursors).

Invariants (ML safety)
- Determinism: same inputs → same window/ledger results; no UI state or filters involved.
- Confidence/status fidelity: if events carry inference metadata, keep `status`, `confidence`, `model_version`, `payload_version`, and FP/FN flags unchanged. Never recompute or clamp for projections.
- Raw vs inferred: inferred interpretations remain separate; do not mix into raw event labels. Only user-confirmed states are strong labels.
- Projection versioning: treat `projection_version` as the contract for window/ledger semantics; bump when overlap/spillover/order rules change.
- Replay: training/eval should be reproducible from event log + deterministic windows. If fidelity is in doubt, train from the event log, not derived projections.

Label guidance
- Strong labels: confirmed interpretations only.
- Weak labels: inferred-only rows (status=inferred/ambiguous/ignored) should be flagged or excluded per recipe.
- FP/FN flags: pass through unchanged; do not infer or drop them.
