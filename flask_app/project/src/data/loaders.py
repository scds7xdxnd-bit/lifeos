"""Data loading utilities with schema enforcement."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pandas as pd

from . import schema

STRING_COLUMNS = schema.IDENTIFIER_COLUMNS + schema.CATEGORICAL_COLUMNS


def _coerce_dtypes(df: pd.DataFrame, require_label: bool) -> pd.DataFrame:
    for column in STRING_COLUMNS:
        if column in df.columns:
            df[column] = df[column].astype("string").fillna("")
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    if "transaction_hour" in df.columns:
        df["transaction_hour"] = pd.to_numeric(df["transaction_hour"], errors="coerce", downcast="integer")
    if require_label and schema.TARGET_COLUMN in df.columns:
        df[schema.TARGET_COLUMN] = pd.to_numeric(
            df[schema.TARGET_COLUMN], errors="coerce", downcast="integer"
        )
    return df


def _validate_and_optionally_filter(
    df: pd.DataFrame,
    require_label: bool,
    drop_invalid: bool,
) -> Tuple[pd.DataFrame, List[dict]]:
    invalid_rows = schema.validate_dataframe(df, require_label=require_label)
    if drop_invalid and invalid_rows:
        bad_indices = [item["index"] for item in invalid_rows]
        df = df.drop(index=bad_indices).reset_index(drop=True)
    return df, invalid_rows


def load_csv(
    path: Path | str,
    require_label: bool = True,
    drop_invalid: bool = True,
) -> Tuple[pd.DataFrame, List[dict]]:
    """Load a CSV file enforcing the declared schema."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    df = pd.read_csv(path)
    df = _coerce_dtypes(df, require_label=require_label)
    df, invalid = _validate_and_optionally_filter(df, require_label, drop_invalid)
    return df, invalid


def load_parquet(
    path: Path | str,
    require_label: bool = False,
    drop_invalid: bool = True,
) -> Tuple[pd.DataFrame, List[dict]]:
    """Load a Parquet file enforcing the declared schema."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Parquet file not found: {path}")

    df = pd.read_parquet(path)
    df = _coerce_dtypes(df, require_label=require_label)
    df, invalid = _validate_and_optionally_filter(df, require_label, drop_invalid)
    return df, invalid


__all__ = ["load_csv", "load_parquet"]
