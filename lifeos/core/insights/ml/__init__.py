from lifeos.core.insights.ml.contracts import (
    ML_ATTACHMENT_CONTRACTS,
    REQUIRED_ML_LOGGING_FIELDS,
    MLAttachmentContract,
    get_ml_attachment_contract,
    list_ml_attachment_contracts,
)
from lifeos.core.insights.ml.embeddings import embed_text
from lifeos.core.insights.ml.event_schemas import (
    INFERENCE_EVENT_MODELS,
    FinanceTransactionInferenceEvent,
    HabitsHabitInferenceEvent,
    HealthMealInferenceEvent,
    HealthWorkoutInferenceEvent,
    InteractionInference,
    MealInference,
    PracticeInference,
    ProjectsWorkSessionInferenceEvent,
    RelationshipsInteractionInferenceEvent,
    SkillsPracticeInferenceEvent,
    TransactionInference,
    WorkoutInference,
    WorkSessionInference,
)
from lifeos.core.insights.ml.feature_extractors import extract_event_features
from lifeos.core.insights.ml.ranking import cosine_similarity, rank_candidates

__all__ = [
    "REQUIRED_ML_LOGGING_FIELDS",
    "MLAttachmentContract",
    "ML_ATTACHMENT_CONTRACTS",
    "get_ml_attachment_contract",
    "list_ml_attachment_contracts",
    "embed_text",
    "extract_event_features",
    "cosine_similarity",
    "rank_candidates",
    "FinanceTransactionInferenceEvent",
    "HabitsHabitInferenceEvent",
    "HealthMealInferenceEvent",
    "HealthWorkoutInferenceEvent",
    "INFERENCE_EVENT_MODELS",
    "InteractionInference",
    "MealInference",
    "PracticeInference",
    "ProjectsWorkSessionInferenceEvent",
    "RelationshipsInteractionInferenceEvent",
    "SkillsPracticeInferenceEvent",
    "TransactionInference",
    "WorkSessionInference",
    "WorkoutInference",
]
