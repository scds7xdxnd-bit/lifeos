# Architectural Decisions

1. **Registry backend (local JSON index with optional MLflow mirror).** Selected a filesystem-backed registry stored under `ARTIFACT_DIR` to simplify bootstrap and guarantee deployability in air-gapped runtimes. MLflow integration is gated by `USE_MLFLOW` so teams can opt-in without changing code paths.
2. **Model format (scikit-learn + joblib for baseline).** The initial use-case favours tabular data and quick iteration. Joblib artifacts keep dependencies light. Torch/TensorFlow backends can slot in later via registry metadata without rewriting services.
3. **Transport protocols (JSON over HTTP, Parquet for batch).** REST with JSON keeps prediction clients simple and contract-driven. Batch inference writes Parquet for efficient columnar analytics and straightforward downstream ingestion.
4. **Deterministic splits and seeding.** Global `SEED` environment variable seeds Python, NumPy, and scikit-learn to ensure reproducibility. `src/data/split.py` performs stratified splits so experiments are comparable.
5. **Strict contract testing.** Contract-focused pytest suites (`tests/contract`) fail the CI pipeline if schemas or I/O columns change unintentionally, protecting downstream integrations.
6. **Feature pipeline as explicit ColumnTransformer.** Centralising feature logic in a saved transformer guarantees training/serving parity and keeps preprocessing auditable.
7. **Error envelopes are immutable.** Online services always respond with the documented `{status, error_code, message, request_id}` payload to allow consistent retry/error handling across clients.
8. **Single source of truth for contracts and runtime constants.** Project-wide identifiers (model name, primary metric, data file names) now live in `src/common/settings.py`, while schema-bound limits reside in `src/data/schema.py`, preventing divergence across services and tests.
