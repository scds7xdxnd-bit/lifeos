"""Feature engineering pipeline for the baseline classifier."""
from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .. import schema


def build_feature_transformer() -> ColumnTransformer:
    """Create the column transformer used across training and inference."""

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )
    transformer = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, schema.NUMERIC_COLUMNS),
            ("categorical", categorical_pipeline, schema.CATEGORICAL_COLUMNS),
        ],
        remainder="drop",
    )
    return transformer


def fit_transformer(
    transformer: ColumnTransformer,
    features: pd.DataFrame,
) -> Tuple[np.ndarray, ColumnTransformer]:
    """Fit the transformer and return transformed features."""

    transformed = transformer.fit_transform(features)
    return transformed, transformer


def apply_transformer(
    transformer: ColumnTransformer,
    features: pd.DataFrame,
) -> np.ndarray:
    """Apply a pre-fitted transformer to a dataframe."""

    return transformer.transform(features)


__all__ = [
    "build_feature_transformer",
    "fit_transformer",
    "apply_transformer",
]
