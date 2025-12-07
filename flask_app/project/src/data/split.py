"""Dataset splitting utilities with deterministic seeds."""
from __future__ import annotations

from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from . import schema


def stratified_split(
    df: pd.DataFrame,
    seed: int = 42,
    test_size: float = 0.2,
    validation_size: float = 0.1,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split the dataframe into train/validation/test subsets deterministically."""

    if not 0 < test_size < 0.5:
        raise ValueError("test_size must be between 0 and 0.5")
    if not 0 < validation_size < 0.5:
        raise ValueError("validation_size must be between 0 and 0.5")

    stratify_col = df[schema.TARGET_COLUMN]
    train_val, test = train_test_split(
        df,
        test_size=test_size,
        random_state=seed,
        shuffle=True,
        stratify=stratify_col,
    )

    relative_val_size = validation_size / (1 - test_size)
    train, val = train_test_split(
        train_val,
        test_size=relative_val_size,
        random_state=seed,
        shuffle=True,
        stratify=train_val[schema.TARGET_COLUMN],
    )

    return (
        train.reset_index(drop=True),
        val.reset_index(drop=True),
        test.reset_index(drop=True),
    )


__all__ = ["stratified_split"]
