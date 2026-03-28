"""Food library CRUD service."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from lifeos.domains.health.events import (
    HEALTH_FOOD_LIBRARY_CREATED,
    HEALTH_FOOD_LIBRARY_DELETED,
    HEALTH_FOOD_LIBRARY_UPDATED,
)
from lifeos.domains.health.models.food_library import FoodLibraryItem
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox


def create_food_item(
    user_id: int,
    *,
    name: str,
    cost_per_100g: float,
    calories_per_100g: float,
    protein_per_100g: float,
    carbohydrate_per_100g: float,
    fat_per_100g: float,
    fiber_per_100g: Optional[float] = None,
) -> FoodLibraryItem:
    """Create a food library item. Raises ValueError('duplicate') if name exists for user."""
    existing = FoodLibraryItem.query.filter_by(user_id=user_id, name=name).first()
    if existing:
        raise ValueError("duplicate")

    item = FoodLibraryItem(
        user_id=user_id,
        name=name.strip(),
        cost_per_100g=cost_per_100g,
        calories_per_100g=calories_per_100g,
        protein_per_100g=protein_per_100g,
        carbohydrate_per_100g=carbohydrate_per_100g,
        fat_per_100g=fat_per_100g,
        fiber_per_100g=fiber_per_100g,
    )
    db.session.add(item)
    db.session.flush()

    enqueue_outbox(
        HEALTH_FOOD_LIBRARY_CREATED,
        {
            "food_id": item.id,
            "user_id": user_id,
            "name": item.name,
            "cost_per_100g": float(item.cost_per_100g),
            "calories_per_100g": float(item.calories_per_100g),
            "protein_per_100g": float(item.protein_per_100g),
            "carbohydrate_per_100g": float(item.carbohydrate_per_100g),
            "fat_per_100g": float(item.fat_per_100g),
            "fiber_per_100g": float(item.fiber_per_100g) if item.fiber_per_100g is not None else None,
            "created_at": item.created_at.isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return item


def list_food_items(
    user_id: int,
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[FoodLibraryItem], int]:
    """List all food library items for a user, ordered by name."""
    query = FoodLibraryItem.query.filter_by(user_id=user_id).order_by(FoodLibraryItem.name)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_food_item(user_id: int, food_id: int) -> Optional[FoodLibraryItem]:
    """Get a single food item by ID, scoped to user."""
    return FoodLibraryItem.query.filter_by(id=food_id, user_id=user_id).first()


def update_food_item(
    user_id: int,
    food_id: int,
    **fields,
) -> Optional[FoodLibraryItem]:
    """Partial update of a food item. Returns None if not found."""
    item = FoodLibraryItem.query.filter_by(id=food_id, user_id=user_id).first()
    if not item:
        return None

    updated_fields = {}
    for key, value in fields.items():
        if value is not None and hasattr(item, key):
            setattr(item, key, value.strip() if isinstance(value, str) else value)
            updated_fields[key] = value

    if not updated_fields:
        return item

    if "name" in updated_fields:
        conflict = FoodLibraryItem.query.filter(
            FoodLibraryItem.user_id == user_id,
            FoodLibraryItem.name == updated_fields["name"],
            FoodLibraryItem.id != food_id,
        ).first()
        if conflict:
            raise ValueError("duplicate")

    item.updated_at = datetime.utcnow()
    db.session.flush()

    enqueue_outbox(
        HEALTH_FOOD_LIBRARY_UPDATED,
        {
            "food_id": item.id,
            "user_id": user_id,
            "fields": {k: float(v) if isinstance(v, (int, float)) else v for k, v in updated_fields.items()},
            "updated_at": item.updated_at.isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return item


def delete_food_item(user_id: int, food_id: int) -> bool:
    """Delete a food item. Returns True if deleted, False if not found."""
    item = FoodLibraryItem.query.filter_by(id=food_id, user_id=user_id).first()
    if not item:
        return False

    enqueue_outbox(
        HEALTH_FOOD_LIBRARY_DELETED,
        {
            "food_id": item.id,
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )

    db.session.delete(item)
    db.session.commit()
    return True
