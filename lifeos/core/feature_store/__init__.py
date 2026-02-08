"""Feature store services (Phase 5c readiness)."""

from lifeos.core.feature_store.models import FeatureStoreEntry
from lifeos.core.feature_store.service import (
    FeatureWrite,
    build_feature_write,
    latest_feature,
    read_features,
    write_feature,
)

__all__ = [
    "FeatureStoreEntry",
    "FeatureWrite",
    "build_feature_write",
    "latest_feature",
    "read_features",
    "write_feature",
]
