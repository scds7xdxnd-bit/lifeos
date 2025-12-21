Legacy finance ML artifacts (joblib/tfidf models) live in the original app tree:

- `lifeos/ml_assets/debit_account_suggester.joblib`
- `lifeos/ml_assets/credit_account_suggester.joblib`
- `lifeos/ml_assets/debit_account_label_encoder.joblib`
- `lifeos/ml_assets/credit_account_label_encoder.joblib`
- `lifeos/ml_assets/credit_account_label_vectorizer.joblib`
- `lifeos/ml_assets/debit_account_tfidf.joblib`

Point new ML loaders to these files (or move them here) via `MLSUGGESTER_MODEL_DIR`.

Example:
```
export MLSUGGESTER_MODEL_DIR=/Users/ammarhakimi/Dev/finance_app_clean/lifeos/ml_assets
export ENABLE_ML=true
```
