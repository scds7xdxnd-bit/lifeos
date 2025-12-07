"""Constants for calendar interpretation."""

from __future__ import annotations

# Minimum confidence score to create an inferred record
MINIMUM_CONFIDENCE_THRESHOLD = 0.5

# Maximum interpretations per calendar event
MAX_INTERPRETATIONS_PER_EVENT = 3

# Domain identifiers
DOMAIN_FINANCE = "finance"
DOMAIN_HEALTH = "health"
DOMAIN_HABITS = "habits"
DOMAIN_SKILLS = "skills"
DOMAIN_PROJECTS = "projects"
DOMAIN_RELATIONSHIPS = "relationships"

# Record type identifiers
RECORD_TYPE_TRANSACTION = "transaction"
RECORD_TYPE_WORKOUT = "workout"
RECORD_TYPE_MEAL = "meal"
RECORD_TYPE_HABIT_LOG = "habit_log"
RECORD_TYPE_PRACTICE = "practice"
RECORD_TYPE_WORK_SESSION = "work_session"
RECORD_TYPE_INTERACTION = "interaction"

# Interpretation statuses
STATUS_INFERRED = "inferred"
STATUS_CONFIRMED = "confirmed"
STATUS_REJECTED = "rejected"
STATUS_IGNORED = "ignored"

# Default meal type mappings based on time of day
MEAL_TIME_MAPPINGS = {
    (5, 10): "breakfast",
    (10, 14): "lunch",
    (14, 17): "snack",
    (17, 22): "dinner",
}

# Workout intensity mappings
INTENSITY_KEYWORDS = {
    "high": ["hiit", "intense", "hard", "heavy", "sprint"],
    "medium": ["moderate", "regular", "standard"],
    "low": ["light", "easy", "gentle", "stretch", "yoga"],
}
