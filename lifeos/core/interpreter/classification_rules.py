"""Classification rules for calendar event interpretation."""

from __future__ import annotations

import re
from typing import List, Pattern

from lifeos.core.interpreter.constants import (
    DOMAIN_FINANCE,
    DOMAIN_HABITS,
    DOMAIN_HEALTH,
    DOMAIN_PROJECTS,
    DOMAIN_RELATIONSHIPS,
    DOMAIN_SKILLS,
    RECORD_TYPE_HABIT_LOG,
    RECORD_TYPE_INTERACTION,
    RECORD_TYPE_MEAL,
    RECORD_TYPE_PRACTICE,
    RECORD_TYPE_TRANSACTION,
    RECORD_TYPE_WORK_SESSION,
    RECORD_TYPE_WORKOUT,
)


def _compile_patterns(keywords: List[str]) -> Pattern:
    """Compile keywords into a case-insensitive regex pattern."""
    escaped = [re.escape(kw) for kw in keywords]
    return re.compile(r"\b(" + "|".join(escaped) + r")\b", re.IGNORECASE)


# ==================== Classification Rules ====================

CLASSIFICATION_RULES = {
    DOMAIN_FINANCE: {
        RECORD_TYPE_TRANSACTION: {
            "keywords": _compile_patterns(
                [
                    "buy",
                    "bought",
                    "purchase",
                    "purchased",
                    "pay",
                    "paid",
                    "shop",
                    "shopping",
                    "store",
                    "market",
                    "grocery",
                    "groceries",
                    "bill",
                    "bills",
                    "payment",
                    "expense",
                    "spend",
                    "spent",
                    "subscription",
                    "fee",
                    "cost",
                    "price",
                    "charge",
                ]
            ),
            "location_keywords": _compile_patterns(
                [
                    "mall",
                    "store",
                    "shop",
                    "market",
                    "supermarket",
                    "walmart",
                    "target",
                    "costco",
                    "amazon",
                    "ebay",
                ]
            ),
            "base_confidence": 0.7,
            "extract_fields": ["amount", "description", "counterparty"],
        },
    },
    DOMAIN_HEALTH: {
        RECORD_TYPE_MEAL: {
            "keywords": _compile_patterns(
                [
                    "breakfast",
                    "lunch",
                    "dinner",
                    "meal",
                    "eat",
                    "eating",
                    "food",
                    "brunch",
                    "snack",
                    "cafe",
                    "restaurant",
                    "dining",
                    "cook",
                    "cooking",
                    "recipe",
                ]
            ),
            "location_keywords": _compile_patterns(
                [
                    "restaurant",
                    "cafe",
                    "diner",
                    "bistro",
                    "kitchen",
                    "mcdonald",
                    "starbucks",
                    "chipotle",
                    "subway",
                ]
            ),
            "base_confidence": 0.75,
            "extract_fields": ["meal_type", "items", "quality_score"],
        },
        RECORD_TYPE_WORKOUT: {
            "keywords": _compile_patterns(
                [
                    "gym",
                    "workout",
                    "exercise",
                    "run",
                    "running",
                    "jog",
                    "jogging",
                    "swim",
                    "swimming",
                    "bike",
                    "biking",
                    "cycling",
                    "yoga",
                    "pilates",
                    "fitness",
                    "training",
                    "cardio",
                    "weights",
                    "lifting",
                    "crossfit",
                    "hiit",
                    "stretch",
                    "stretching",
                    "walk",
                    "walking",
                    "hike",
                    "hiking",
                    "tennis",
                    "basketball",
                    "football",
                    "soccer",
                    "golf",
                ]
            ),
            "location_keywords": _compile_patterns(
                [
                    "gym",
                    "fitness",
                    "sport",
                    "pool",
                    "court",
                    "field",
                    "park",
                    "trail",
                ]
            ),
            "base_confidence": 0.8,
            "extract_fields": ["workout_type", "duration_minutes", "intensity"],
        },
    },
    DOMAIN_HABITS: {
        RECORD_TYPE_HABIT_LOG: {
            "keywords": _compile_patterns(
                [
                    "habit",
                    "routine",
                    "daily",
                    "weekly",
                    "morning routine",
                    "evening routine",
                    "meditation",
                    "meditate",
                    "journal",
                    "journaling",
                    "read",
                    "reading",
                    "water",
                    "hydrate",
                    "sleep",
                    "wake",
                ]
            ),
            "base_confidence": 0.6,
            "extract_fields": ["habit_name", "value", "note"],
        },
    },
    DOMAIN_SKILLS: {
        RECORD_TYPE_PRACTICE: {
            "keywords": _compile_patterns(
                [
                    "practice",
                    "practicing",
                    "study",
                    "studying",
                    "learn",
                    "learning",
                    "lesson",
                    "class",
                    "course",
                    "tutorial",
                    "training",
                    "workshop",
                    "piano",
                    "guitar",
                    "violin",
                    "music",
                    "instrument",
                    "language",
                    "coding",
                    "programming",
                    "drawing",
                    "painting",
                    "art",
                ]
            ),
            "base_confidence": 0.7,
            "extract_fields": ["skill_name", "duration_minutes", "notes"],
        },
    },
    DOMAIN_PROJECTS: {
        RECORD_TYPE_WORK_SESSION: {
            "keywords": _compile_patterns(
                [
                    "work",
                    "working",
                    "project",
                    "task",
                    "deadline",
                    "sprint",
                    "meeting",
                    "standup",
                    "review",
                    "planning",
                    "brainstorm",
                    "focus",
                    "deep work",
                    "pomodoro",
                ]
            ),
            "base_confidence": 0.65,
            "extract_fields": [
                "project_name",
                "task_name",
                "duration_minutes",
                "notes",
            ],
        },
    },
    DOMAIN_RELATIONSHIPS: {
        RECORD_TYPE_INTERACTION: {
            "keywords": _compile_patterns(
                [
                    "meet",
                    "meeting",
                    "lunch with",
                    "dinner with",
                    "coffee with",
                    "call with",
                    "chat with",
                    "visit",
                    "visiting",
                    "hangout",
                    "party",
                    "gathering",
                    "birthday",
                    "anniversary",
                    "date",
                ]
            ),
            "person_pattern": re.compile(
                r"(?:with|meet(?:ing)?|call(?:ing)?|visit(?:ing)?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
                re.IGNORECASE,
            ),
            "base_confidence": 0.7,
            "extract_fields": ["person_name", "method", "notes"],
        },
    },
}


def classify_event(
    title: str,
    description: str | None,
    start_time,
    end_time,
    location: str | None,
) -> List[dict]:
    """
    Classify a calendar event into potential domain records.

    Returns list of classification results sorted by confidence (descending).
    Each result contains: domain, record_type, confidence_score, extracted_data
    """
    text = f"{title} {description or ''} {location or ''}".lower()
    results = []

    for domain, record_types in CLASSIFICATION_RULES.items():
        for record_type, rules in record_types.items():
            confidence = 0.0
            extracted_data = {}

            # Check title/description keywords
            keywords_pattern = rules.get("keywords")
            if keywords_pattern and keywords_pattern.search(text):
                confidence = rules.get("base_confidence", 0.5)

            # Boost for location keywords
            location_keywords = rules.get("location_keywords")
            if (
                location_keywords
                and location
                and location_keywords.search(location.lower())
            ):
                confidence = min(confidence + 0.1, 1.0)

            # Extract person name for relationships
            person_pattern = rules.get("person_pattern")
            if person_pattern:
                match = person_pattern.search(title)
                if match:
                    extracted_data["person_name"] = match.group(1)
                    confidence = min(confidence + 0.15, 1.0)

            # Calculate duration if available
            if start_time and end_time:
                duration = (end_time - start_time).total_seconds() / 60
                extracted_data["duration_minutes"] = int(duration)

            # Only include if confidence above threshold
            if confidence >= 0.5:
                results.append(
                    {
                        "domain": domain,
                        "record_type": record_type,
                        "confidence_score": round(confidence, 2),
                        "extracted_data": extracted_data,
                    }
                )

    # Sort by confidence descending
    results.sort(key=lambda x: x["confidence_score"], reverse=True)
    return results[:3]  # Max 3 interpretations per event
