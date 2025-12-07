"""Calendar Interpreter: classifies calendar events and creates inferred domain records."""

from lifeos.core.interpreter.calendar_interpreter import (
    CalendarInterpreter,
    calendar_interpreter,
)
from lifeos.core.interpreter.classification_rules import (
    CLASSIFICATION_RULES,
    classify_event,
)
from lifeos.core.interpreter.constants import (
    DOMAIN_FINANCE,
    DOMAIN_HABITS,
    DOMAIN_HEALTH,
    DOMAIN_PROJECTS,
    DOMAIN_RELATIONSHIPS,
    DOMAIN_SKILLS,
    MINIMUM_CONFIDENCE_THRESHOLD,
    STATUS_CONFIRMED,
    STATUS_INFERRED,
    STATUS_REJECTED,
)
from lifeos.core.interpreter.domain_adapters import DomainAdapter, get_adapter

__all__ = [
    "CalendarInterpreter",
    "calendar_interpreter",
    "classify_event",
    "CLASSIFICATION_RULES",
    "DomainAdapter",
    "get_adapter",
    # Constants
    "DOMAIN_FINANCE",
    "DOMAIN_HABITS",
    "DOMAIN_HEALTH",
    "DOMAIN_PROJECTS",
    "DOMAIN_RELATIONSHIPS",
    "DOMAIN_SKILLS",
    "MINIMUM_CONFIDENCE_THRESHOLD",
    "STATUS_CONFIRMED",
    "STATUS_INFERRED",
    "STATUS_REJECTED",
]
