"""Data schema definitions and validators for the Account Risk classification dataset."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
from pydantic import BaseModel, Field, ValidationError, field_validator

ALLOWED_MERCHANT_TYPES = {
    "utilities",
    "payroll",
    "supplies",
    "travel",
    "software",
}

AMOUNT_MIN = -1_000_000.0
AMOUNT_MAX = 1_000_000.0
HOUR_MIN = 0
HOUR_MAX = 23
RISK_MIN = 0
RISK_MAX = 1


class TransactionRecord(BaseModel):
    """Schema for a single transaction used for both training and inference."""

    transaction_id: str = Field(min_length=1, max_length=64)
    account_id: str = Field(min_length=1, max_length=64)
    amount: float = Field(ge=AMOUNT_MIN, le=AMOUNT_MAX)
    merchant_type: str
    transaction_hour: int = Field(ge=HOUR_MIN, le=HOUR_MAX)
    risk_label: Optional[int] = Field(default=None, ge=RISK_MIN, le=RISK_MAX)

    @field_validator("merchant_type")
    @classmethod
    def validate_merchant_type(cls, value: str) -> str:
        if value not in ALLOWED_MERCHANT_TYPES:
            raise ValueError(
                f"merchant_type '{value}' is not in the allowed set {sorted(ALLOWED_MERCHANT_TYPES)}"
            )
        return value

    @field_validator("transaction_id", "account_id")
    @classmethod
    def strip_and_validate_identifiers(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("identifier fields must be non-empty after stripping whitespace")
        return cleaned


NUMERIC_COLUMNS = ("amount", "transaction_hour")
CATEGORICAL_COLUMNS = ("merchant_type",)
IDENTIFIER_COLUMNS = ("transaction_id", "account_id")
FEATURE_COLUMNS = NUMERIC_COLUMNS + CATEGORICAL_COLUMNS
TARGET_COLUMN = "risk_label"


def iter_invalid_rows(df: pd.DataFrame) -> Iterable[dict]:
    """Yield row index and validation errors for rows that fail schema validation."""

    for idx, record in df.iterrows():
        data = record.to_dict()
        try:
            TransactionRecord.model_validate(data)
        except ValidationError as exc:  # pragma: no cover - structure exercised in tests
            yield {
                "index": int(idx),
                "errors": exc.errors(),
                "data": data,
            }


def validate_dataframe(df: pd.DataFrame, require_label: bool = True) -> List[dict]:
    """Validate a dataframe against the record schema.

    Returns a list of invalid row reports. If empty, the dataframe is valid.
    """

    required_columns = set(IDENTIFIER_COLUMNS + FEATURE_COLUMNS)
    if require_label:
        required_columns.add(TARGET_COLUMN)
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Dataframe missing required columns: {sorted(missing)}")

    invalid_rows = list(iter_invalid_rows(df))

    if require_label:
        null_target = df[df[TARGET_COLUMN].isna()]
        for idx in null_target.index:
            invalid_rows.append(
                {
                    "index": int(idx),
                    "errors": [
                        {
                            "type": "value_error.null",
                            "loc": [TARGET_COLUMN],
                            "msg": "risk_label is required for training rows",
                        }
                    ],
                    "data": df.loc[idx].to_dict(),
                }
            )

    return invalid_rows


def export_record_schema(path: Path) -> None:
    """Persist the JSON schema for a single record to ``path``."""

    schema = TransactionRecord.model_json_schema(mode="validation")
    path.write_text(json.dumps(schema, indent=2))


def summarize_table(df: pd.DataFrame) -> dict:
    """Return simple dataset summary metadata."""

    summary = {
        "row_count": int(len(df)),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "columns": {
            col: {
                "dtype": str(df[col].dtype),
                "null_fraction": float(df[col].isna().mean()),
            }
            for col in df.columns
        },
    }
    return summary


__all__ = [
    "TransactionRecord",
    "NUMERIC_COLUMNS",
    "CATEGORICAL_COLUMNS",
    "IDENTIFIER_COLUMNS",
    "TARGET_COLUMN",
    "validate_dataframe",
    "iter_invalid_rows",
    "export_record_schema",
    "summarize_table",
    "ALLOWED_MERCHANT_TYPES",
    "FEATURE_COLUMNS",
    "AMOUNT_MIN",
    "AMOUNT_MAX",
    "HOUR_MIN",
    "HOUR_MAX",
    "RISK_MIN",
    "RISK_MAX",
]
