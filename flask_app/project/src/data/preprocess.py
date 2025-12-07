"""Preprocessing utilities for cleaning and preparing datasets."""
from __future__ import annotations

from typing import Tuple

import pandas as pd

from . import schema


def clean_dataframe(df: pd.DataFrame, require_label: bool = True) -> pd.DataFrame:
    """Apply deterministic cleaning operations before feature building."""

    cleaned = df.copy()
    cleaned["merchant_type"] = cleaned["merchant_type"].str.lower().str.strip()
    cleaned["amount"] = cleaned["amount"].fillna(0.0).clip(-1_000_000.0, 1_000_000.0)
    cleaned["transaction_hour"] = (
        cleaned["transaction_hour"].fillna(0).astype(int).clip(lower=0, upper=23)
    )
    for column in schema.IDENTIFIER_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].astype(str).str.strip()
    if require_label and schema.TARGET_COLUMN in cleaned.columns:
        cleaned[schema.TARGET_COLUMN] = cleaned[schema.TARGET_COLUMN].astype(int)
    return cleaned


def split_features_target(
    df: pd.DataFrame,
    target_column: str = schema.TARGET_COLUMN,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Split a dataframe into feature matrix and target vector."""

    features = df[[
        *schema.IDENTIFIER_COLUMNS,
        *schema.NUMERIC_COLUMNS,
        *schema.CATEGORICAL_COLUMNS,
    ]].copy()
    target = df[target_column].astype(int)
    return features, target


__all__ = ["clean_dataframe", "split_features_target"]
