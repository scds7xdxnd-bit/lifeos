Legacy finance ML artifacts (joblib/tfidf models) live in the original app tree:

- `flask_app/debit_account_suggester.joblib`
- `flask_app/credit_account_suggester.joblib`
- `flask_app/debit_account_label_encoder.joblib`
- `flask_app/credit_account_label_encoder.joblib`
- `flask_app/credit_account_label_vectorizer.joblib`
- `flask_app/debit_account_tfidf.joblib`

Point new ML loaders to these files (or move them here) via `MLSUGGESTER_MODEL_DIR`.

Example:
```
export MLSUGGESTER_MODEL_DIR=/Users/ammarhakimi/Dev/finance_app_clean/flask_app
export ENABLE_ML=true
```
