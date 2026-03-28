# HEALTH_OPTIMIZER_BUILD_SPEC.md

**Version:** 1.0
**Date:** 2026-03-28
**Author:** Opus (architectural specification)
**Executor:** Sonnet 4.6 (file-by-file implementation)
**Status:** Approved feature set only — no scope expansion permitted

---

## 0. Build Philosophy & Constraints

### What This Feature IS

A **standalone macro and cost optimizer** embedded as a sub-tab within the LifeOS health page. It is a pure planning/calculation tool — a personal linear programming solver that helps a user answer: "Given the foods I buy, what combination minimizes cost (or calories) while hitting my macro targets?"

It consists of two surfaces:
1. **Food Library** — a persistent, user-scoped database of foods with per-100g nutritional and cost data
2. **Optimizer** — a solver form where the user selects foods, sets an objective, adds constraints, and gets an optimal meal plan

### What This Feature Is NOT

- Not a meal planner or scheduler (single-solve calculator)
- Not a dietary recommendation engine (user controls all inputs)
- Not connected to `health_nutrition_log` (standalone — does not write to or read from existing health logs)
- Not a calorie counter or macro tracker (it is a one-shot optimization tool)
- Not a food database — uses Open Food Facts for macro lookup, but the user's library is local and cost is always manual

### Emotional Contract

Same as health domain (UI/UX Constitution §1, §9):
- **Allowed:** "Here's the optimal combination", "No solution found — try loosening a constraint"
- **Forbidden:** "You're eating too much", "You should reduce your intake", "Your diet is unhealthy"

### Breadth-First Rule

Every section ~20% depth before any section reaches 80%. Sonnet must build all backend files to functional state before starting any frontend work. All frontend files must reach skeleton state before polishing any single component.

### Later-Wave Domain Rules (Constitution §12.1)

Health is a later-wave domain. The optimizer does not interpret health data, but all UI copy must avoid clinical or prescriptive framing. The solver reports numbers; it does not make recommendations.

---

## 1. Solver Location Decision

### Decision: Client-Side (JavaScript)

### Justification

| Factor | Client-Side | Backend (Python) |
|--------|-------------|------------------|
| **Problem size** | Tiny: 10-50 variables, 5-10 constraints | Overkill for this scale |
| **Latency** | Instant (< 5ms) | Network round-trip (100-500ms) |
| **UX** | Immediate feedback as user adjusts | Requires loading state per solve |
| **New backend surface** | None (only food library CRUD) | New `/api/health/solve` endpoint |
| **Reliability** | `javascript-lp-solver` is mature, handles simplex | scipy.optimize.linprog is battle-tested but unnecessary |
| **Offline** | Works without network | Requires connectivity |
| **Bundle size** | ~15KB minified for `javascript-lp-solver` | N/A |

The LP problems in this feature are trivially small. A user's food library will have 10-50 items, with 5-10 constraints. The simplex method solves this in microseconds. Client-side execution eliminates network latency and reduces backend complexity. The `javascript-lp-solver` npm package provides a well-tested simplex implementation that maps directly to our problem formulation.

### Library: `javascript-lp-solver`

**npm:** `javascript-lp-solver`
**Install:** `npm install javascript-lp-solver`
**API shape:**

```typescript
import solver from 'javascript-lp-solver'

const model = {
  optimize: 'cost',        // field name to optimize
  opType: 'min',           // 'min' | 'max'
  constraints: {
    protein: { min: 150 },  // Σ(X_i × protein_i) >= 150
    calories: { max: 2500 },
  },
  variables: {
    chicken: { cost: 2.5, protein: 31, calories: 165 },
    rice: { cost: 0.5, protein: 2.7, calories: 130 },
  },
  ints: {},  // empty — all continuous
}

const result = solver.Solve(model)
// result = { feasible: true, bounded: true, result: 42.5, chicken: 4.8, rice: 3.2 }
```

The library returns:
- `feasible: boolean` — whether a solution exists
- `bounded: boolean` — whether the solution is finite
- `result: number` — optimal objective value
- `[variable_name]: number` — optimal quantity for each included variable (absent = 0)

Per-food bounds are expressed as additional constraints with min/max on the variable.

### Food Macro Lookup: Open Food Facts API

When creating a food item, the name input is a **search-enabled autocomplete**. As the user types, it queries the Open Food Facts API and shows matching products. Selecting a result pre-fills all macro fields. The user then only needs to enter **cost** (which is personal/local — no API has it).

**Why Open Food Facts:**
- Free, no API key required
- CORS-enabled (direct browser fetch, no backend proxy needed)
- Community-maintained database with millions of products
- Returns per-100g nutritional data in a standard format
- No rate limiting for reasonable usage (debounced search is fine)

**API endpoint:**

```
GET https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1&page_size=8&fields=product_name,brands,nutriments
```

**Response shape (relevant fields only):**

```json
{
  "products": [
    {
      "product_name": "Chicken Breast Fillets",
      "brands": "Woolworths",
      "nutriments": {
        "energy-kcal_100g": 110,
        "proteins_100g": 23.1,
        "carbohydrates_100g": 0,
        "fat_100g": 1.9,
        "fiber_100g": 0
      }
    }
  ]
}
```

**Field mapping (Open Food Facts -> FoodItem):**

| OFF field | FoodItem field | Fallback |
|-----------|---------------|----------|
| `product_name` | `name` | — |
| `brands` | display only (appended to name in dropdown) | omit |
| `nutriments.energy-kcal_100g` | `calories_per_100g` | `0` |
| `nutriments.proteins_100g` | `protein_per_100g` | `0` |
| `nutriments.carbohydrates_100g` | `carbohydrate_per_100g` | `0` |
| `nutriments.fat_100g` | `fat_per_100g` | `0` |
| `nutriments.fiber_100g` | `fiber_per_100g` | `null` |

**UX flow:**
1. User types in the food name field (e.g., "chicken breast")
2. After 300ms debounce, frontend fetches from Open Food Facts
3. Dropdown shows up to 8 results: `product_name — brand` with compact macro preview
4. User clicks a result → macro fields auto-fill, name field gets the product name
5. User can still edit any pre-filled macro value (they are editable, not locked)
6. User enters cost (the only field that is always manual)
7. If no results or user prefers manual entry, they can ignore the dropdown and type freely

**Edge cases:**
- No network / API down: search silently returns no results; form remains fully functional for manual entry
- Missing nutriment fields in API response: default to `0` (except fiber which defaults to `null`)
- User modifies name after selecting from dropdown: allowed — the name is just pre-filled, not locked

**No backend changes needed.** This is purely a frontend enhancement — the food library CRUD API and model remain unchanged.

---

## 2. LP Formulation Reference

This section is the mathematical specification. Sonnet must translate this directly into the solver model construction code.

### Decision Variables

```
X_i = quantity of food i in units of 100g (continuous, non-negative)
```

Each X_i corresponds to one food item from the user's library that they have selected for this optimization.

### Objective Function

The user selects ONE of six modes:

| Mode | Mathematical Form | `javascript-lp-solver` config |
|------|-------------------|-------------------------------|
| Minimize cost | min Σ(X_i × cost_per_100g_i) | `optimize: '_cost', opType: 'min'` |
| Maximize cost | max Σ(X_i × cost_per_100g_i) | `optimize: '_cost', opType: 'max'` |
| Minimize calories | min Σ(X_i × calories_per_100g_i) | `optimize: '_calories', opType: 'min'` |
| Maximize calories | max Σ(X_i × calories_per_100g_i) | `optimize: '_calories', opType: 'max'` |
| Target cost = T | Find feasible X s.t. Σ(X_i × cost_per_100g_i) = T | Add `_cost: { equal: T }` as constraint, optimize any feasible |
| Target calories = T | Find feasible X s.t. Σ(X_i × calories_per_100g_i) = T | Add `_calories: { equal: T }` as constraint, optimize any feasible |

For "target" modes: pin the objective as an equality constraint and use a dummy minimize (the solver finds any feasible solution). Implementation: set `optimize: '_dummy', opType: 'min'` where `_dummy = 0` for all variables (constant objective), and add the target as `{ equal: T }`.

### Constraints

Each user-defined constraint has:
- **Category:** one of `calories`, `protein`, `carbohydrate`, `fat`, `fiber`
- **Operator:** `>=` | `<=` | `=`
- **Value:** numeric RHS

Translated to solver model:

| Operator | Solver constraint |
|----------|-------------------|
| `>=` | `{ min: value }` |
| `<=` | `{ max: value }` |
| `=` | `{ equal: value }` |

**Budget constraint** (available when objective = calories): same pattern but on cost field.
**Calorie constraint** (available when objective = cost): treated as a regular constraint in the `calories` category.

### Per-Food Bounds

Optional min/max per food item. Expressed as individual constraints:

```
X_chicken >= 1.0   →  constraint: 'bound_chicken_min': { min: 1.0 }
                      variable chicken: { ..., bound_chicken_min: 1 }
X_chicken <= 5.0   →  constraint: 'bound_chicken_max': { max: 5.0 }
                      variable chicken: { ..., bound_chicken_max: 1 }
```

Each bound creates a constraint that only the target food contributes to (coefficient = 1 for the bounded food, 0 for all others).

### Solution Output

For a successful solve, display:
1. **Per-food quantities:** `X_i` value in grams (multiply by 100 for display), rounded to 1 decimal
2. **Per-food cost and macros:** computed from `X_i × per_100g` values
3. **Totals row:** sum of all per-food costs and macros
4. **Objective value:** the optimal cost or calories achieved
5. **Constraint satisfaction:** for each user constraint, show LHS value vs RHS value and whether tight (LHS = RHS) or slack (LHS > RHS or LHS < RHS depending on direction)

### Error States

| Condition | `solver.Solve()` output | User message |
|-----------|------------------------|--------------|
| Infeasible | `feasible: false` | "No combination of these foods can satisfy all constraints. Try loosening a constraint or adding more foods." |
| Unbounded | `bounded: false` | "The solution is unbounded — add a constraint to limit [cost/calories]." |
| No foods selected | N/A (pre-validation) | "Select at least one food from your library to optimize." |
| No objective | N/A (pre-validation) | "Choose what to optimize before solving." |

---

## 3. Backend Spec

The backend surface is limited to **Food Library CRUD** — a new table, model, schemas, service, controller, and events. The solver runs client-side and requires no backend endpoint.

### 3.1 Migration

**File:** `lifeos/migrations/versions/20260328_health_food_library.py`

**Action:** Create new table `health_food_library_item`.

```python
"""Add food library table for health optimizer.

Revision ID: 20260328_health_food_library
Revises: <CURRENT_HEAD>
Create Date: 2026-03-28
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260328_health_food_library"
down_revision = "<CURRENT_HEAD>"  # Sonnet: run `cd lifeos && alembic heads` to find this
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "health_food_library_item",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("cost_per_100g", sa.Numeric(10, 4), nullable=False),
        sa.Column("calories_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("protein_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("carbohydrate_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("fat_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("fiber_per_100g", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index(
        "ix_health_food_library_item_user_name",
        "health_food_library_item",
        ["user_id", "name"],
        unique=True,
    )


def downgrade():
    op.drop_index("ix_health_food_library_item_user_name")
    op.drop_table("health_food_library_item")
```

**Indexes:**
- `user_id` — individual index (created by `index=True` on the column)
- `(user_id, name)` — unique composite index (prevents duplicate food names per user)

**Sonnet instructions:** Before writing this file, run `cd lifeos && python -m alembic heads` to get the current head revision. Replace `<CURRENT_HEAD>` with the actual value.

### 3.2 Model

**File:** `lifeos/domains/health/models/food_library.py`

```python
"""Food library item model for macro/cost optimizer."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class FoodLibraryItem(db.Model):
    __tablename__ = "health_food_library_item"
    __table_args__ = (
        db.Index("ix_health_food_library_item_user_name", "user_id", "name", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(db.String(256), nullable=False)
    cost_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    calories_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    protein_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    carbohydrate_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fat_per_100g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fiber_per_100g: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Update `lifeos/domains/health/models/__init__.py`:** Add import of `FoodLibraryItem`.

### 3.3 Schemas

**File:** `lifeos/domains/health/schemas/food_library_schemas.py`

```python
"""Food library Pydantic DTOs."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


class FoodItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    cost_per_100g: float = Field(ge=0)
    calories_per_100g: float = Field(ge=0)
    protein_per_100g: float = Field(ge=0)
    carbohydrate_per_100g: float = Field(ge=0)
    fat_per_100g: float = Field(ge=0)
    fiber_per_100g: Optional[float] = Field(default=None, ge=0)


class FoodItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=256)
    cost_per_100g: Optional[float] = Field(default=None, ge=0)
    calories_per_100g: Optional[float] = Field(default=None, ge=0)
    protein_per_100g: Optional[float] = Field(default=None, ge=0)
    carbohydrate_per_100g: Optional[float] = Field(default=None, ge=0)
    fat_per_100g: Optional[float] = Field(default=None, ge=0)
    fiber_per_100g: Optional[float] = Field(default=None, ge=0)


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)
```

**Validation notes:**
- `FoodItemCreate`: all numeric fields required (except `fiber_per_100g`), all >= 0
- `FoodItemUpdate`: all fields optional (partial update). Only provided fields are applied.
- `name` uniqueness per user is enforced at the database level, not in the schema.

### 3.4 Service + Events

#### Events

**File:** `lifeos/domains/health/events.py` — **ADD** to existing file (do not replace):

Add three new event constants and their catalog entries:

```python
# --- Food Library Events ---
HEALTH_FOOD_LIBRARY_CREATED = "health.food_library.created"
HEALTH_FOOD_LIBRARY_UPDATED = "health.food_library.updated"
HEALTH_FOOD_LIBRARY_DELETED = "health.food_library.deleted"
```

Add to `EVENT_CATALOG`:

```python
HEALTH_FOOD_LIBRARY_CREATED: {
    "version": "v1",
    "payload": {
        "food_id": "int",
        "user_id": "int",
        "name": "str",
        "cost_per_100g": "decimal",
        "calories_per_100g": "decimal",
        "protein_per_100g": "decimal",
        "carbohydrate_per_100g": "decimal",
        "fat_per_100g": "decimal",
        "fiber_per_100g": "decimal?",
        "created_at": "datetime",
    },
},
HEALTH_FOOD_LIBRARY_UPDATED: {
    "version": "v1",
    "payload": {
        "food_id": "int",
        "user_id": "int",
        "fields": "dict",
        "updated_at": "datetime",
    },
},
HEALTH_FOOD_LIBRARY_DELETED: {
    "version": "v1",
    "payload": {
        "food_id": "int",
        "user_id": "int",
        "deleted_at": "datetime",
    },
},
```

Add all three constants to the `__all__` list.

#### Semantic Contracts

**File:** `lifeos/core/events/semantic_contracts.py` — **ADD** entries for the three new events:

```python
"health.food_library.created": EventSemanticContract(
    event_type="health.food_library.created",
    meaning="A food item was added to the user's personal food library.",
    asserted_by="user",
    certainty="confirmed",
),
"health.food_library.updated": EventSemanticContract(
    event_type="health.food_library.updated",
    meaning="A food item was modified in the user's personal food library.",
    asserted_by="user",
    certainty="confirmed",
),
"health.food_library.deleted": EventSemanticContract(
    event_type="health.food_library.deleted",
    meaning="A food item was removed from the user's personal food library.",
    asserted_by="user",
    certainty="confirmed",
),
```

#### Service

**File:** `lifeos/domains/health/services/food_library_service.py` (NEW)

```python
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
    fiber_per_100g: float | None = None,
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


def get_food_item(user_id: int, food_id: int) -> FoodLibraryItem | None:
    """Get a single food item by ID, scoped to user."""
    return FoodLibraryItem.query.filter_by(id=food_id, user_id=user_id).first()


def update_food_item(
    user_id: int,
    food_id: int,
    **fields,
) -> FoodLibraryItem | None:
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

    # Check name uniqueness if name changed
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
```

**Update `lifeos/domains/health/services/__init__.py`:** Add imports from `food_library_service`:

```python
from lifeos.domains.health.services.food_library_service import (
    create_food_item,
    delete_food_item,
    get_food_item,
    list_food_items,
    update_food_item,
)
```

Add all five to `__all__`.

#### Mapper

**Add to `lifeos/domains/health/mappers.py`:**

```python
def map_food_item(f: FoodLibraryItem) -> dict:
    return {
        "id": f.id,
        "name": f.name,
        "cost_per_100g": float(f.cost_per_100g),
        "calories_per_100g": float(f.calories_per_100g),
        "protein_per_100g": float(f.protein_per_100g),
        "carbohydrate_per_100g": float(f.carbohydrate_per_100g),
        "fat_per_100g": float(f.fat_per_100g),
        "fiber_per_100g": float(f.fiber_per_100g) if f.fiber_per_100g is not None else None,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "updated_at": f.updated_at.isoformat() if f.updated_at else None,
    }
```

Import `FoodLibraryItem` at the top of `mappers.py`.

### 3.5 Controller (API Contract)

**File:** `lifeos/domains/health/controllers/food_library_api.py` (NEW)

Blueprint name: `food_library_api_bp`

All routes are relative to the blueprint prefix. Blueprint will be registered at `/api/health/food-library`.

```python
"""Food library CRUD API controller."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.health import services
from lifeos.domains.health.mappers import map_food_item
from lifeos.domains.health.schemas.food_library_schemas import (
    FoodItemCreate,
    FoodItemUpdate,
    Pagination,
)

food_library_api_bp = Blueprint("food_library_api", __name__)


@food_library_api_bp.get("")
@jwt_required()
def list_foods():
    user_id = int(get_jwt_identity())
    try:
        params = Pagination.model_validate(dict(request.args))
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    items, total = services.list_food_items(user_id, page=params.page, per_page=params.per_page)
    pages = (total + params.per_page - 1) // params.per_page if params.per_page else 1
    return jsonify({"ok": True, "items": [map_food_item(f) for f in items], "page": params.page, "pages": pages, "total": total})


@food_library_api_bp.get("/<int:food_id>")
@jwt_required()
def get_food(food_id: int):
    user_id = int(get_jwt_identity())
    item = services.get_food_item(user_id, food_id)
    if not item:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "item": map_food_item(item)})


@food_library_api_bp.post("")
@jwt_required()
@csrf_protected
def create_food():
    payload = request.get_json(silent=True) or {}
    try:
        data = FoodItemCreate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    try:
        item = services.create_food_item(
            user_id,
            name=data.name,
            cost_per_100g=data.cost_per_100g,
            calories_per_100g=data.calories_per_100g,
            protein_per_100g=data.protein_per_100g,
            carbohydrate_per_100g=data.carbohydrate_per_100g,
            fat_per_100g=data.fat_per_100g,
            fiber_per_100g=data.fiber_per_100g,
        )
    except ValueError as exc:
        if str(exc) == "duplicate":
            return jsonify({"ok": False, "error": "duplicate"}), 409
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "item": map_food_item(item)}), 201


@food_library_api_bp.patch("/<int:food_id>")
@jwt_required()
@csrf_protected
def update_food(food_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = FoodItemUpdate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        return jsonify({"ok": False, "error": "no_fields"}), 400
    try:
        item = services.update_food_item(user_id, food_id, **fields)
    except ValueError as exc:
        if str(exc) == "duplicate":
            return jsonify({"ok": False, "error": "duplicate"}), 409
        return jsonify({"ok": False, "error": "validation_error"}), 400
    if not item:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "item": map_food_item(item)})


@food_library_api_bp.delete("/<int:food_id>")
@jwt_required()
@csrf_protected
def delete_food(food_id: int):
    user_id = int(get_jwt_identity())
    deleted = services.delete_food_item(user_id, food_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})
```

#### Blueprint Registration

**File:** `lifeos/__init__.py` — **ADD** in `_register_blueprints()`:

```python
from lifeos.domains.health.controllers.food_library_api import food_library_api_bp

app.register_blueprint(food_library_api_bp, url_prefix="/api/health/food-library")
```

Place this line immediately after the existing `health_api_bp` registration (line 284).

### 3.6 API Contract Summary

All endpoints under `/api/health/food-library`. Auth: JWT required. CSRF: required on POST/PATCH/DELETE.

| Method | Path | Purpose | Request | Response |
|--------|------|---------|---------|----------|
| `GET` | `/api/health/food-library` | List all food items | `?page=1&per_page=50` | `{ ok, items[], page, pages, total }` |
| `GET` | `/api/health/food-library/:id` | Get single item | — | `{ ok, item }` |
| `POST` | `/api/health/food-library` | Create item | Body: `FoodItemCreate` | `{ ok, item }` (201) or `{ ok: false, error: "duplicate" }` (409) |
| `PATCH` | `/api/health/food-library/:id` | Update item | Body: `FoodItemUpdate` (partial) | `{ ok, item }` or 404 or 409 |
| `DELETE` | `/api/health/food-library/:id` | Delete item | — | `{ ok: true }` or 404 |

**Response shape for a food item:**
```json
{
  "id": 1,
  "name": "Chicken breast 100g",
  "cost_per_100g": 1.2500,
  "calories_per_100g": 165.00,
  "protein_per_100g": 31.00,
  "carbohydrate_per_100g": 0.00,
  "fat_per_100g": 3.60,
  "fiber_per_100g": null,
  "created_at": "2026-03-28T10:00:00",
  "updated_at": "2026-03-28T10:00:00"
}
```

---

## 4. Frontend Component Registry

All new frontend files. These extend the existing health page surfaces.

| # | Component Name | File Path | Responsibility | Max Lines |
|---|---------------|-----------|----------------|-----------|
| 1 | `foodLibraryApi` | `frontend/lib/api/foodLibrary.ts` | TypeScript types + API methods for food library CRUD | 90 |
| 2 | `searchFoodDatabase` | `frontend/lib/api/foodSearch.ts` | Open Food Facts search: debounced fetch, response normalization, types | 70 |
| 3 | `solveLP` | `frontend/lib/optimizer/solveLP.ts` | Wraps `javascript-lp-solver` — builds model from food selection + constraints, returns typed result | 120 |
| 4 | `FoodLibraryManager` | `frontend/app/(app)/health/_components/optimizer/FoodLibraryManager.tsx` | Food library list with add/edit/delete — the persistent library view | 200 |
| 5 | `FoodItemForm` | `frontend/app/(app)/health/_components/optimizer/FoodItemForm.tsx` | Modal form with search-enabled name input that auto-fills macros from Open Food Facts; cost is always manual | 200 |
| 6 | `FoodSearchInput` | `frontend/app/(app)/health/_components/optimizer/FoodSearchInput.tsx` | Autocomplete input: debounced search, dropdown results, selection callback | 120 |
| 7 | `OptimizerPanel` | `frontend/app/(app)/health/_components/optimizer/OptimizerPanel.tsx` | Main optimizer surface: food selection, objective, constraints, solve button, results | 300 |
| 8 | `FoodSelector` | `frontend/app/(app)/health/_components/optimizer/FoodSelector.tsx` | Checkbox list of food items from library for inclusion in optimization | 80 |
| 9 | `ObjectiveSelector` | `frontend/app/(app)/health/_components/optimizer/ObjectiveSelector.tsx` | 6-option radio/pill selector for objective mode | 60 |
| 10 | `ConstraintBuilder` | `frontend/app/(app)/health/_components/optimizer/ConstraintBuilder.tsx` | Add/remove constraints with category, operator, value inputs | 120 |
| 11 | `FoodBoundsEditor` | `frontend/app/(app)/health/_components/optimizer/FoodBoundsEditor.tsx` | Optional per-food min/max bounds inputs for selected foods | 80 |
| 12 | `OptimizerResult` | `frontend/app/(app)/health/_components/optimizer/OptimizerResult.tsx` | Solution display: quantities table, totals, constraint satisfaction, error states | 150 |

**Total new frontend files: 12**
**Estimated total lines: ~1,590**

Additionally, modifications to existing files:
- `frontend/app/(app)/health/page.tsx` — Add top-level view toggle (Overview / Optimizer)
- `frontend/lib/translations/app.ts` — Extend `HealthPageTranslations` with optimizer keys
- `package.json` — Add `javascript-lp-solver` dependency

---

## 5. Surface Specs

### 5.1 Health Page — View Toggle (Modification to Existing Page)

The existing health page gains a top-level view toggle in the header area.

**Layout change to `page.tsx`:**

```
+----------------------------------------------------------+
| HEALTH (micro-label)            [Overview | Optimizer]   |
| Your Wellbeing                              [LOG v]      |
+----------------------------------------------------------+
| (active view renders here)                               |
+----------------------------------------------------------+
```

**Toggle implementation:**
- New state: `const [activeView, setActiveView] = useState<'overview' | 'optimizer'>('overview')`
- Toggle renders as two pill buttons side by side (same pattern as history tabs)
- Selected: `background: #fce8e4`, `color: #8b4a3a`, `border: none`
- Unselected: `background: transparent`, `color: #5a6157`
- When `activeView === 'overview'`: render the existing overview + history + detail panel
- When `activeView === 'optimizer'`: render `<OptimizerPanel />` instead (full width, no detail panel split)
- LOG dropdown only visible when `activeView === 'overview'`

**Mobile:** Toggle pills stack horizontally in header, same styling.

### 5.2 Food Library Manager (Surface 1)

**File:** `frontend/app/(app)/health/_components/optimizer/FoodLibraryManager.tsx`

**Purpose:** CRUD interface for the user's persistent food library. Shown as the top section of the optimizer panel.

#### Props Interface

```typescript
interface FoodLibraryManagerProps {
  foods: FoodItem[]
  isLoading: boolean
  onAddFood: () => void           // opens FoodItemForm in create mode
  onEditFood: (id: number) => void // opens FoodItemForm in edit mode
  onDeleteFood: (id: number) => void
}
```

#### Layout

```
+----------------------------------------------------------+
| YOUR FOOD LIBRARY (micro-label)          [+ Add Food]    |
|                                                          |
| +------------------------------------------------------+ |
| | Chicken breast    165 cal  31g P  0g C  3.6g F  $1.25| |
| |                                          [Edit] [Del] | |
| +------------------------------------------------------+ |
| | Brown rice        130 cal  2.7g P  28g C  1g F  $0.30| |
| |                                          [Edit] [Del] | |
| +------------------------------------------------------+ |
| | (empty state if no foods)                              | |
| +------------------------------------------------------+ |
+----------------------------------------------------------+
```

#### Design Tokens

- Container card: `surface-container-lowest` (#ffffff), `border-radius: 0 16px 16px 16px`, `padding: 32px`
- Section header: "YOUR FOOD LIBRARY" — Manrope Bold 700 uppercase, `0.6875rem`, `+0.05em`, `#8b4a3a`
- "Add Food" button: secondary pill (`background: #f1f5eb`, `color: #2e342b`, `border-radius: 100px`)
- Food rows: `background: #f8faf2`, `border-radius: 0 10px 10px 10px`, `padding: 12px 16px`, `margin-bottom: 6px`
- Macro labels: Manrope 400, `0.75rem`, `#5a6157`
- Food name: Manrope 600, `0.875rem`, `#2e342b`
- Cost: Manrope 600, `0.8125rem`, `#4b6646`
- Edit button: ghost pill, `color: #5a6157`, hover `color: #4b6646`
- Delete button: ghost pill, `color: #adb4a8`, hover `color: #e8735c`
- Empty state: "No foods yet. Add your first food to start optimizing." — Manrope 400, `0.875rem`, `#767d72`, centered

#### Interaction

- "Add Food" opens `FoodItemForm` in create mode
- "Edit" on a row opens `FoodItemForm` in edit mode, pre-filled
- "Delete" shows a confirmation (inline "Are you sure?" with confirm/cancel pills, same as habits delete pattern)
- All buttons 44px min touch target
- Staggered row entrance animation (35ms delay)
- Food rows are NOT selectable here (selection happens in FoodSelector within the optimizer form)

#### Mobile Behavior

- Single column, full width
- Macro values wrap to second line on narrow screens
- Edit/Delete buttons stack vertically on very narrow screens (< 400px)

### 5.3 Food Search Input (NEW — Search-Enabled Autocomplete)

**File:** `frontend/app/(app)/health/_components/optimizer/FoodSearchInput.tsx`

#### Props Interface

```typescript
interface FoodSearchResult {
  product_name: string
  brands: string | null
  calories_per_100g: number
  protein_per_100g: number
  carbohydrate_per_100g: number
  fat_per_100g: number
  fiber_per_100g: number | null
}

interface FoodSearchInputProps {
  value: string                              // current name text
  onChange: (name: string) => void            // free-text change
  onSelect: (result: FoodSearchResult) => void  // user picks a result → auto-fill macros
  disabled?: boolean
  placeholder?: string
}
```

#### Behavior

1. User types in the input field. After **300ms debounce**, `searchFoodDatabase(query)` fires.
2. While loading: small spinner icon inside the input (right side).
3. Results appear in a dropdown below the input: up to **8 items**.
4. Each result row shows:
   ```
   Chicken Breast Fillets — Woolworths
   110 cal · 23g P · 0g C · 1.9g F
   ```
   - Product name: Manrope 500, `0.8125rem`, `#2e342b`
   - Brand: Manrope 400, `0.8125rem`, `#767d72` (omitted if null)
   - Macro preview: Manrope 400, `0.6875rem`, `#5a6157`
5. Clicking a result calls `onSelect(result)` — parent form pre-fills macros — and closes dropdown.
6. Clicking outside or pressing Escape closes the dropdown.
7. If query is < 3 characters: no search. If API returns 0 results: show "No matches found — enter values manually." in muted text.
8. If API call fails (network error, timeout): silently ignore, no dropdown. Form remains fully usable for manual entry.

#### Layout

- Input: standard text input, full width, `border-radius: 4px`, ghost border `rgba(173,180,168,0.2)`
- Dropdown: absolute-positioned below input, `z-index: 80`, `background: #ffffff`, `border-radius: 0 12px 12px 12px`, `box-shadow: 0 8px 24px rgba(46,52,43,0.06)`, `max-height: 320px`, `overflow-y: auto`
- Each dropdown row: `padding: 10px 16px`, `min-height: 44px`, hover `background: #f8faf2`, `cursor: pointer`
- Spinner: 16px, `color: #8b4a3a`, positioned absolutely inside input, right side

#### Accessibility

- `role="combobox"` on the input, `aria-expanded` toggles with dropdown
- `role="listbox"` on the dropdown, `role="option"` on each result
- Arrow keys navigate results, Enter selects, Escape closes
- `aria-label="Search for food"` on the input

### 5.3b Food Search Utility

**File:** `frontend/lib/api/foodSearch.ts`

```typescript
export interface FoodSearchResult {
  product_name: string
  brands: string | null
  calories_per_100g: number
  protein_per_100g: number
  carbohydrate_per_100g: number
  fat_per_100g: number
  fiber_per_100g: number | null
}

/**
 * Search Open Food Facts for foods matching the query.
 * Returns normalized results with per-100g macro data.
 * Silently returns [] on network error (manual entry is always the fallback).
 */
export async function searchFoodDatabase(query: string): Promise<FoodSearchResult[]> {
  if (query.length < 3) return []

  const url = `https://world.openfoodfacts.org/cgi/search.pl?` +
    `search_terms=${encodeURIComponent(query)}&search_simple=1&action=process&json=1&page_size=8` +
    `&fields=product_name,brands,nutriments`

  try {
    const res = await fetch(url)
    if (!res.ok) return []
    const data = await res.json()
    return (data.products ?? [])
      .filter((p: any) => p.product_name)  // skip entries without a name
      .map((p: any) => ({
        product_name: p.product_name,
        brands: p.brands || null,
        calories_per_100g: p.nutriments?.['energy-kcal_100g'] ?? 0,
        protein_per_100g: p.nutriments?.proteins_100g ?? 0,
        carbohydrate_per_100g: p.nutriments?.carbohydrates_100g ?? 0,
        fat_per_100g: p.nutriments?.fat_100g ?? 0,
        fiber_per_100g: p.nutriments?.fiber_100g ?? null,
      }))
  } catch {
    return []  // network failure — degrade to manual entry
  }
}
```

No dependencies. No backend changes. Pure frontend utility.

### 5.3c Food Item Form (Surface 4 — Updated with Search)

**File:** `frontend/app/(app)/health/_components/optimizer/FoodItemForm.tsx`

#### Props Interface

```typescript
interface FoodItemFormProps {
  mode: 'create' | 'edit'
  initialData?: FoodItem | null    // null for create, populated for edit
  onClose: () => void
  onSuccess: () => void
}
```

#### Form Fields

| Field | Type | Label | Input | Auto-filled? | Required |
|-------|------|-------|-------|-------------|----------|
| `name` | string | "Food name" | **FoodSearchInput** (autocomplete) | From API selection | Yes |
| `cost_per_100g` | number | "Cost per 100g" | number, step 0.01 | **Never** (always manual) | Yes |
| `calories_per_100g` | number | "Calories per 100g" | number, step 1 | Yes, on selection | Yes |
| `protein_per_100g` | number | "Protein (g per 100g)" | number, step 0.1 | Yes, on selection | Yes |
| `carbohydrate_per_100g` | number | "Carbs (g per 100g)" | number, step 0.1 | Yes, on selection | Yes |
| `fat_per_100g` | number | "Fat (g per 100g)" | number, step 0.1 | Yes, on selection | Yes |
| `fiber_per_100g` | number | "Fiber (g per 100g)" | number, step 0.1 | Yes, on selection | No |

When the user selects a search result from `FoodSearchInput`, the `onSelect` callback triggers:

```typescript
function handleSearchSelect(result: FoodSearchResult) {
  setName(result.product_name)
  setCalories(result.calories_per_100g)
  setProtein(result.protein_per_100g)
  setCarbs(result.carbohydrate_per_100g)
  setFat(result.fat_per_100g)
  setFiber(result.fiber_per_100g ?? 0)
  // cost_per_100g is NOT set — user must always enter it manually
}
```

All auto-filled fields remain **editable** — the user can correct any value after auto-fill.

#### Layout

- Centered modal (same pattern as health log forms: fixed inset, z-index 70, blurred backdrop)
- Form card: `max-width: 520px`, specimen radius, `padding: 32px`
- Title: "Add Food" or "Edit Food" — Newsreader 400, `1.125rem`, `#4b6646`
- When in **create mode**, a subtle hint below the name input: "Search for a food to auto-fill nutrition data, or enter values manually." — Manrope 400, `0.6875rem`, `#767d72`
- When in **edit mode**, the name field is a plain text input (no search — macros already exist)
- Fields arranged as:
  - Row 1: Name / FoodSearchInput (full width)
  - Row 2: Cost per 100g (full width) — **highlighted** with a subtle `background: #fdf0ed` tint and "Enter your cost" helper text, since this is the only field the user MUST fill manually
  - Row 3: Calories per 100g (full width)
  - Row 4: Protein | Carbs (two columns)
  - Row 5: Fat | Fiber (two columns)
- Auto-filled fields show a brief flash animation (fade from `#fdf0ed` to `transparent`, 400ms) when populated from search, so the user sees what changed
- Submit: "Save Food" primary gradient pill
- Cancel: ghost pill
- Duplicate error: inline message below name field — "A food with this name already exists."

#### Data Source

- Create: `POST /api/health/food-library`
- Edit: `PATCH /api/health/food-library/:id`
- On success: invalidate `['health', 'food-library']`

### 5.4 Optimizer Form — Food Selection + Objective (Surface 2, upper)

**File:** `frontend/app/(app)/health/_components/optimizer/OptimizerPanel.tsx`

This is the main orchestrator component for the optimizer view.

#### Layout (full width, no detail panel split)

```
Desktop (>= 1024px):
+----------------------------------------------------------+
| MACRO & COST OPTIMIZER (micro-label)                     |
| Plan Your Nutrition (Newsreader Light 300)               |
| Find the optimal food combination. (Manrope)             |
+----------------------------------------------------------+
| [FoodLibraryManager — collapsible after initial setup]   |
+----------------------------------------------------------+
| ┌─────────────────────────┐  ┌─────────────────────────┐ |
| │ SELECT FOODS            │  │ OBJECTIVE               │ |
| │ [FoodSelector]          │  │ [ObjectiveSelector]     │ |
| │                         │  │                         │ |
| │                         │  │ CONSTRAINTS             │ |
| │                         │  │ [ConstraintBuilder]     │ |
| │                         │  │                         │ |
| │                         │  │ FOOD BOUNDS (optional)  │ |
| │                         │  │ [FoodBoundsEditor]      │ |
| └─────────────────────────┘  └─────────────────────────┘ |
|                                                          |
|                        [Solve]                           |
|                                                          |
| [OptimizerResult — appears after solve]                  |
+----------------------------------------------------------+

Mobile:
Everything stacks vertically. Same components, single column.
```

#### State Variables

```typescript
// Food library
const [editingFood, setEditingFood] = useState<number | null>(null)
const [showFoodForm, setShowFoodForm] = useState(false)
const [foodFormMode, setFoodFormMode] = useState<'create' | 'edit'>('create')

// Optimizer
const [selectedFoodIds, setSelectedFoodIds] = useState<Set<number>>(new Set())
const [objective, setObjective] = useState<ObjectiveMode | null>(null)
const [targetValue, setTargetValue] = useState<number>(0)
const [constraints, setConstraints] = useState<Constraint[]>([])
const [foodBounds, setFoodBounds] = useState<Record<number, { min?: number; max?: number }>>({})
const [result, setResult] = useState<SolveResult | null>(null)
const [solveError, setSolveError] = useState<string | null>(null)
const [foodLibraryCollapsed, setFoodLibraryCollapsed] = useState(false)
```

#### Data Sources

```typescript
const { data: foodData, isLoading } = useQuery({
  queryKey: ['health', 'food-library'],
  queryFn: () => foodLibraryApi.list(),
})
```

Mutations for create/update/delete food items use `useMutation` with `queryClient.invalidateQueries({ queryKey: ['health', 'food-library'] })` on success.

#### Design Tokens

- Optimizer panel container: `background: #f8faf2` (page background, no extra card wrapping at top level)
- Sub-sections (Food Selector, Objective, Constraints): individual specimen cards, `surface-container-lowest` (#ffffff), `padding: 24px`, `border-radius: 0 16px 16px 16px`
- Section labels: Manrope Bold 700 uppercase, `0.6875rem`, `#8b4a3a`
- Section gap: `24px`
- Solve button: primary gradient pill, centered, `padding: 12px 40px`, `min-height: 48px`
- Solve button disabled state: `opacity: 0.5`, `cursor: not-allowed`

### 5.5 Optimizer Sub-Components (Surfaces 2 cont., 5, 6)

#### FoodSelector

**File:** `frontend/app/(app)/health/_components/optimizer/FoodSelector.tsx`

```typescript
interface FoodSelectorProps {
  foods: FoodItem[]
  selectedIds: Set<number>
  onToggle: (id: number) => void
  onSelectAll: () => void
  onDeselectAll: () => void
}
```

- Renders a checkbox list of foods from the library
- Each row: checkbox (24px, `accent-color: #4b6646`) + food name + key macros (compact)
- "Select All" / "Deselect All" ghost buttons at top
- Selected rows get subtle `background: #fdf0ed` tint
- Empty state: "Add foods to your library first."
- Row height: 44px minimum (touch target)

#### ObjectiveSelector

**File:** `frontend/app/(app)/health/_components/optimizer/ObjectiveSelector.tsx`

```typescript
type ObjectiveMode = 'min_cost' | 'max_cost' | 'min_calories' | 'max_calories' | 'target_cost' | 'target_calories'

interface ObjectiveSelectorProps {
  value: ObjectiveMode | null
  targetValue: number
  onChange: (mode: ObjectiveMode) => void
  onTargetChange: (value: number) => void
}
```

- Six options as pill buttons arranged in a 3x2 grid (or wrapping row):
  - Row 1: "Minimize Cost" | "Maximize Cost" | "Target Cost"
  - Row 2: "Minimize Calories" | "Maximize Calories" | "Target Calories"
- Selected pill: `background: #fce8e4`, `color: #8b4a3a`
- Unselected pill: `background: #f1f5eb`, `color: #5a6157`
- When a "Target" mode is selected, a number input appears below: "Target value:" with the input field
- Target input: standard text input, `border-radius: 4px`, ghost border

#### ConstraintBuilder

**File:** `frontend/app/(app)/health/_components/optimizer/ConstraintBuilder.tsx`

```typescript
interface Constraint {
  id: string          // client-generated UUID for keying
  category: 'calories' | 'protein' | 'carbohydrate' | 'fat' | 'fiber' | 'cost'
  operator: '>=' | '<=' | '='
  value: number
}

interface ConstraintBuilderProps {
  constraints: Constraint[]
  onChange: (constraints: Constraint[]) => void
  objectiveMode: ObjectiveMode | null  // determines which categories are available
}
```

- Section starts collapsed: "Add Constraints" expandable header (chevron icon)
- When expanded: list of existing constraints + "Add Constraint" button
- Each constraint row: [Category dropdown] [Operator dropdown] [Value input] [Remove button]
- Category dropdown options: `Calories`, `Protein (g)`, `Carbs (g)`, `Fat (g)`, `Fiber (g)`
  - When objective = cost, `Budget` is also available
  - When objective = calories, cost constraints are not available (redundant with objective)
- Operator dropdown: `>=`, `<=`, `=`
- Value input: number, step varies by category
- Remove button: small X icon, `color: #adb4a8`, hover `#e8735c`
- "Add Constraint" button: secondary pill, `+ Add Constraint`
- New constraint starts with: category = `protein`, operator = `>=`, value = `0`

**Layout per row:**
```
[Category ▼]  [Op ▼]  [___value___]  [×]
```

Dropdowns: `background: #ffffff`, `border: 1px solid rgba(173,180,168,0.2)`, `border-radius: 4px`

#### FoodBoundsEditor

**File:** `frontend/app/(app)/health/_components/optimizer/FoodBoundsEditor.tsx`

```typescript
interface FoodBoundsEditorProps {
  selectedFoods: FoodItem[]
  bounds: Record<number, { min?: number; max?: number }>
  onChange: (bounds: Record<number, { min?: number; max?: number }>) => void
}
```

- Section starts collapsed: "Set Food Bounds (optional)" expandable header
- When expanded: list of selected foods, each with optional min/max inputs
- Each row: food name + "Min (100g units)" input + "Max (100g units)" input
- Empty inputs mean no bound (unbounded)
- Inputs: number, step 0.1, `min: 0`
- Label under each input explaining units: "units of 100g" in `0.6875rem`, `#767d72`

### 5.6 Optimizer Result Display (Surface 3)

**File:** `frontend/app/(app)/health/_components/optimizer/OptimizerResult.tsx`

#### Props Interface

```typescript
interface SolveResult {
  feasible: boolean
  bounded: boolean
  objectiveValue: number
  quantities: Array<{
    food: FoodItem
    quantity100g: number      // raw solver value (units of 100g)
    quantityGrams: number     // × 100 for display
    cost: number              // quantity × cost_per_100g
    calories: number
    protein: number
    carbohydrate: number
    fat: number
    fiber: number | null
  }>
  totals: {
    cost: number
    calories: number
    protein: number
    carbohydrate: number
    fat: number
    fiber: number | null
  }
  constraintSatisfaction: Array<{
    constraint: Constraint
    lhsValue: number           // computed LHS
    satisfied: boolean
    slack: number              // |LHS - RHS|
    tight: boolean             // slack < 0.01
  }>
}

interface OptimizerResultProps {
  result: SolveResult | null
  error: string | null          // infeasible/unbounded message
  objectiveMode: ObjectiveMode | null
}
```

#### Layout — Success State

```
+----------------------------------------------------------+
| OPTIMAL SOLUTION (micro-label)                           |
| "Here's the optimal combination." (Newsreader 400)       |
+----------------------------------------------------------+
| Objective: Minimum Cost = $12.45                         |
+----------------------------------------------------------+
| Food              Qty (g)   Cost    Cal    P     C     F |
| Chicken breast    480g      $5.76   792    149   0     17|
| Brown rice        300g      $0.90   390    8.1   84    3 |
| Broccoli          200g      $0.40   68     5.6   14    0 |
|──────────────────────────────────────────────────────────|
| TOTAL                       $7.06   1250   163   98    20|
+----------------------------------------------------------+
| CONSTRAINTS                                              |
| Protein >= 150g     ✓  163g (13g slack)                  |
| Calories <= 1500    ✓  1250 (250 slack)                  |
| Fat <= 25g          ✓  20g (5g slack)                    |
+----------------------------------------------------------+
```

#### Layout — Error State

```
+----------------------------------------------------------+
| ⚠ NO SOLUTION FOUND                                     |
|                                                          |
| No combination of these foods can satisfy all            |
| constraints. Try loosening a constraint or adding        |
| more foods.                                              |
|                                                          |
| [Adjust Constraints]                                     |
+----------------------------------------------------------+
```

#### Design Tokens

- Result container: specimen card, `padding: 32px`
- Success state:
  - Heading: Newsreader 400, `1.125rem`, `#4b6646`
  - Objective value: Newsreader 400, `1.25rem`, `#2e342b`
  - Table: no `<table>` tag — use CSS grid (5-7 columns). Headers in micro-label style.
  - Rows: `background: #f8faf2` alternating with `#ffffff`
  - Totals row: `background: #fdf0ed` (health accent tint), `font-weight: 700`
  - Quantities: Manrope 600, `0.875rem`, `#2e342b`
  - Constraint satisfaction: checkmark in `#4b6646` for satisfied, `#e8735c` for violated
  - Slack label: Manrope 400, `0.75rem`, `#767d72`
  - "Tight" constraints (slack < 0.01): bold, `#8b4a3a`
- Error state:
  - Card: `background: #fdf0ed` (clay rose tint)
  - Icon: triangle-alert from lucide-react, `color: #8b4a3a`
  - Message: Manrope 400, `0.875rem`, `#2e342b`
  - CTA: secondary pill button "Adjust Constraints" that scrolls to constraint section

#### Mobile Behavior

- Result table scrolls horizontally on narrow screens
- Quantities column always visible (sticky left)
- Constraint satisfaction stacks vertically

---

## 6. Boundaries

### 6.1 Forbidden

| # | Constraint | Rationale |
|---|-----------|-----------|
| F1 | Dietary recommendation or prescription language | Later-wave domain + emotional contract |
| F2 | Calorie/macro shaming ("you're eating too much...") | Emotional contract |
| F3 | Items from EXPLICITLY_CUT list | Scope boundary |
| F4 | Cross-domain imports (except User model via ForeignKey) | Architecture rule |
| F5 | Synchronous service-to-service calls | Architecture rule |
| F6 | Modifications to existing health tables | Scope boundary — additive only |
| F7 | "You should..." / "You must..." tone | Constitution §9 |
| F8 | Sensitivity analysis / shadow prices / dual values | Explicitly cut |
| F9 | Integer programming | Explicitly cut — all X_i continuous |
| F10 | Multi-objective optimization | Explicitly cut — user picks ONE |
| F11 | Meal planning / scheduling | This is single-solve, not a planner |
| F12 | Integration with health_nutrition_log | Optimizer is standalone |
| F13 | External food database / API | User inputs manually |
| F14 | Currency conversion | Out of scope |
| F15 | Recipe / composite food support | Each food is atomic |
| F16 | Export / share / save solutions | Explicitly cut |
| F17 | Optimization history | Explicitly cut |
| F18 | Pure black text or grey shadows | DESIGN.md rules |
| F19 | 1px borders, square buttons | DESIGN.md rules |
| F20 | Medical or dietary recommendation language | Health domain caution rule |

### 6.2 Required

| # | Constraint | Implementation |
|---|-----------|----------------|
| R1 | Read-first hierarchy for food library | List view is default; form appears on explicit intent |
| R2 | Progressive disclosure for constraints and bounds | Both sections start collapsed with expandable headers |
| R3 | Clear infeasibility/unbounded error messaging | Calm-tone messages per section 2 error states |
| R4 | 44px min touch targets, ARIA labels | All buttons, checkboxes, dropdowns |
| R5 | Editorial presentation | Newsreader headlines, Manrope body, specimen cards |
| R6 | All LifeOS layering rules respected | Controller → Service → Model → Schema → Events |
| R7 | Migration is additive-only | New table, no modifications to existing tables |
| R8 | Events follow catalog pattern with payload versioning | `version: "v1"` on all three new events |
| R9 | Semantic contracts added for new events | All three events get `EventSemanticContract` entries |
| R10 | Pill-shaped buttons only | `border-radius: 100px` everywhere |
| R11 | Specimen card pattern | `border-radius: 0 16px 16px 16px` on all cards |
| R12 | Sage-tinted shadows only | `rgba(46, 52, 43, 0.06)` |
| R13 | 2rem minimum card padding | `padding: 32px` |
| R14 | Domain accent only on selection | Health accent (#fce8e4/#8b4a3a) on selected pills/rows only |
| R15 | `prefers-reduced-motion` support | Disable animations when user prefers |
| R16 | Translations for all user-facing text | All strings via `getAppTranslations(lang).health.optimizer.*` |
| R17 | Client-side solver pre-validation | Validate food selection + objective before calling solver |

---

## 7. Dependency Map (Build Order DAG)

```
BACKEND (must complete before any frontend optimizer work)
═══════════════════════════════════════════════════════════

Step B1: Migration
   └─ 20260328_health_food_library.py (find current head first)
         │
Step B2: Model + Mapper (parallel)
   ├─ models/food_library.py
   ├─ models/__init__.py (update)
   └─ mappers.py (add map_food_item)
         │
Step B3: Schemas
   └─ schemas/food_library_schemas.py
         │
Step B4: Events (parallel with B3)
   ├─ events.py (add 3 constants + catalog entries)
   └─ core/events/semantic_contracts.py (add 3 contracts)
         │
Step B5: Service
   ├─ services/food_library_service.py
   └─ services/__init__.py (update)
         │
Step B6: Controller + Registration
   ├─ controllers/food_library_api.py
   └─ __init__.py (register blueprint)
         │
Step B7: Run migration + verify
   └─ cd lifeos && python -m alembic upgrade head
   └─ Manual test: curl the CRUD endpoints


FRONTEND (depends on B7 complete)
═══════════════════════════════════

Step F1: Install dependency + API client + food search utility (parallel)
   ├─ npm install javascript-lp-solver
   ├─ lib/api/foodLibrary.ts
   ├─ lib/api/foodSearch.ts (Open Food Facts search utility)
   └─ lib/translations/app.ts (extend HealthPageTranslations)
         │
Step F2: Solver utility
   └─ lib/optimizer/solveLP.ts
         │
Step F3: Leaf components (parallel, no inter-dependencies)
   ├─ FoodSearchInput.tsx (autocomplete — depends on foodSearch.ts)
   ├─ FoodSelector.tsx
   ├─ ObjectiveSelector.tsx
   ├─ ConstraintBuilder.tsx
   ├─ FoodBoundsEditor.tsx
   └─ OptimizerResult.tsx
         │
Step F3b: FoodItemForm (depends on FoodSearchInput)
   └─ FoodItemForm.tsx (uses FoodSearchInput for name field in create mode)
         │
Step F4: Composite components (depend on F3, F3b)
   ├─ FoodLibraryManager.tsx (uses FoodItemForm)
   └─ OptimizerPanel.tsx (uses all F3 components + FoodLibraryManager + solveLP)
         │
Step F5: Page integration
   └─ page.tsx (add activeView toggle, render OptimizerPanel when active)
```

---

## 8. Sonnet Execution Instructions

### Pre-flight Checks

Before starting, verify:
1. `lifeos/domains/health/` exists with controllers/, models/, schemas/, services/ dirs
2. `lifeos/migrations/versions/` exists
3. `lifeos/lifeos_platform/outbox/__init__.py` exports `enqueue`
4. `frontend/lib/api/client.ts` exports `apiFetch`, `apiGet`, `apiPost`
5. `frontend/app/(app)/health/page.tsx` exists (current health page — will be modified)
6. `frontend/app/(app)/health/_components/` exists
7. Run `cd lifeos && python -m alembic heads` — record the current head revision ID

### Backend Steps (B1-B7)

---

#### Step B1: Create migration

**Action:** Create `lifeos/migrations/versions/20260328_health_food_library.py`
**Max lines:** 50
**Implements:** `health_food_library_item` table with all columns and indexes per section 3.1
**Critical:** Set `down_revision` to the value from pre-flight check #7
**Verification:** `cd lifeos && python -m alembic upgrade head` succeeds without errors. `sqlite3 instance/lifeos.db ".schema health_food_library_item"` shows the table.

---

#### Step B2: Create model + update mapper

**Action:** Create `lifeos/domains/health/models/food_library.py` per section 3.2
**Max lines:** 30
**Action:** Edit `lifeos/domains/health/models/__init__.py` — add `from .food_library import FoodLibraryItem`
**Action:** Edit `lifeos/domains/health/mappers.py` — add `map_food_item` function per section 3.4, add import of `FoodLibraryItem`
**Verification:** `python -c "from lifeos.domains.health.models.food_library import FoodLibraryItem; print(FoodLibraryItem.__tablename__)"` prints `health_food_library_item`

---

#### Step B3: Create schemas

**Action:** Create `lifeos/domains/health/schemas/food_library_schemas.py` per section 3.3
**Max lines:** 35
**Verification:** `python -c "from lifeos.domains.health.schemas.food_library_schemas import FoodItemCreate; print(FoodItemCreate.model_json_schema())"` shows all fields

---

#### Step B4: Add events + semantic contracts

**Action:** Edit `lifeos/domains/health/events.py` — add 3 event constants, 3 catalog entries, update `__all__`
**Action:** Edit `lifeos/core/events/semantic_contracts.py` — add 3 `EventSemanticContract` entries to `EVENT_SEMANTIC_CONTRACTS` dict
**Verification:** `python -c "from lifeos.domains.health.events import HEALTH_FOOD_LIBRARY_CREATED; print(HEALTH_FOOD_LIBRARY_CREATED)"` prints `health.food_library.created`

---

#### Step B5: Create service

**Action:** Create `lifeos/domains/health/services/food_library_service.py` per section 3.4
**Max lines:** 110
**Action:** Edit `lifeos/domains/health/services/__init__.py` — add imports and `__all__` entries
**Verification:** With app context, `services.create_food_item(1, name="Test", cost_per_100g=1.0, calories_per_100g=100, protein_per_100g=20, carbohydrate_per_100g=5, fat_per_100g=3)` returns a `FoodLibraryItem`

---

#### Step B6: Create controller + register blueprint

**Action:** Create `lifeos/domains/health/controllers/food_library_api.py` per section 3.5
**Max lines:** 90
**Action:** Edit `lifeos/__init__.py` — add blueprint import and `app.register_blueprint(food_library_api_bp, url_prefix="/api/health/food-library")` after the existing health registration lines
**Verification:** Start the dev server. `curl -H "Authorization: Bearer <token>" http://localhost:5000/api/health/food-library` returns `{"ok": true, "items": [], ...}`

---

#### Step B7: Run migration + end-to-end test

**Action:** `cd lifeos && python -m alembic upgrade head`
**Verification:** All five CRUD endpoints work:
1. POST create → 201 with item
2. GET list → 200 with items array
3. GET by id → 200 with single item
4. PATCH update → 200 with updated item
5. DELETE → 200 with `ok: true`
6. POST duplicate name → 409

---

### Frontend Steps (F1-F5)

---

#### Step F1: Install dependency + create API client + food search utility + extend translations

**Action:** `cd frontend && npm install javascript-lp-solver`
**Action:** Create `frontend/lib/api/foodLibrary.ts`
**Max lines:** 90
**Action:** Create `frontend/lib/api/foodSearch.ts`
**Max lines:** 70
**Implements:** `searchFoodDatabase(query: string): Promise<FoodSearchResult[]>` per section 5.3b. Also exports the `FoodSearchResult` interface. No backend dependency — calls Open Food Facts directly from the browser.

Types to define (in foodLibrary.ts):
```typescript
export interface FoodItem {
  id: number
  name: string
  cost_per_100g: number
  calories_per_100g: number
  protein_per_100g: number
  carbohydrate_per_100g: number
  fat_per_100g: number
  fiber_per_100g: number | null
  created_at: string | null
  updated_at: string | null
}

export interface FoodItemCreateInput {
  name: string
  cost_per_100g: number
  calories_per_100g: number
  protein_per_100g: number
  carbohydrate_per_100g: number
  fat_per_100g: number
  fiber_per_100g?: number
}

export interface FoodItemUpdateInput {
  name?: string
  cost_per_100g?: number
  calories_per_100g?: number
  protein_per_100g?: number
  carbohydrate_per_100g?: number
  fat_per_100g?: number
  fiber_per_100g?: number
}
```

API methods:
```typescript
export const foodLibraryApi = {
  list: (params?) => apiGet<ListResponse>('/api/health/food-library?...'),
  get: (id) => apiGet<{ ok: boolean; item: FoodItem }>(`/api/health/food-library/${id}`),
  create: (data) => apiPost<{ ok: boolean; item: FoodItem }>('/api/health/food-library', data),
  update: (id, data) => apiFetch<{ ok: boolean; item: FoodItem }>(`/api/health/food-library/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id) => apiFetch<{ ok: boolean }>(`/api/health/food-library/${id}`, { method: 'DELETE' }),
}
```

**Action:** Edit `frontend/lib/translations/app.ts` — extend `HealthPageTranslations` with optimizer keys:

```typescript
// Add to HealthPageTranslations interface:
optimizer: string                    // "Optimizer"
overview: string                     // "Overview"
foodLibrary: string                  // "Your Food Library"
addFood: string                      // "Add Food"
editFood: string                     // "Edit Food"
saveFood: string                     // "Save Food"
foodName: string                     // "Food name"
costPer100g: string                  // "Cost per 100g"
caloriesPer100g: string              // "Calories per 100g"
proteinPer100g: string               // "Protein (g per 100g)"
carbsPer100g: string                 // "Carbs (g per 100g)"
fatPer100g: string                   // "Fat (g per 100g)"
fiberPer100g: string                 // "Fiber (g per 100g)"
duplicateFoodError: string           // "A food with this name already exists."
noFoodsYet: string                   // "No foods yet. Add your first food to start optimizing."
selectFoods: string                  // "Select Foods"
selectAll: string                    // "Select All"
deselectAll: string                  // "Deselect All"
objective: string                    // "Objective"
minimizeCost: string                 // "Minimize Cost"
maximizeCost: string                 // "Maximize Cost"
minimizeCalories: string             // "Minimize Calories"
maximizeCalories: string             // "Maximize Calories"
targetCost: string                   // "Target Cost"
targetCalories: string               // "Target Calories"
targetValue: string                  // "Target value"
constraints: string                  // "Constraints"
addConstraint: string                // "Add Constraint"
foodBounds: string                   // "Food Bounds (optional)"
minBound: string                     // "Min (100g)"
maxBound: string                     // "Max (100g)"
solve: string                        // "Solve"
solving: string                      // "Solving..."
optimalSolution: string              // "Optimal Solution"
optimalCombination: string           // "Here's the optimal combination."
noSolution: string                   // "No combination of these foods can satisfy all constraints. Try loosening a constraint or adding more foods."
unboundedSolution: string            // "The solution is unbounded — add a constraint to limit the objective."
selectFoodsFirst: string             // "Select at least one food to optimize."
chooseObjective: string              // "Choose what to optimize."
adjustConstraints: string            // "Adjust Constraints"
food: string                         // "Food"
quantity: string                     // "Qty (g)"
cost: string                         // "Cost"
total: string                        // "Total"
satisfied: string                    // "Satisfied"
slack: string                        // "slack"
tight: string                        // "tight"
protein: string                      // "Protein"
carbs: string                        // "Carbs"
fat: string                          // "Fat"
fiber: string                        // "Fiber"
budget: string                       // "Budget"
planNutrition: string                // "Plan Your Nutrition"
planNutritionSub: string             // "Find the optimal food combination for your goals."
deleteConfirmFood: string            // "Delete this food?"
searchFoodHint: string               // "Search for a food to auto-fill nutrition data, or enter values manually."
searchFoodPlaceholder: string        // "Search foods (e.g., chicken breast)..."
noSearchResults: string              // "No matches found — enter values manually."
enterYourCost: string                // "Enter your cost"
sourceApi: string                    // "Auto-filled"
sourceManual: string                 // "Manual entry"
sourceEdited: string                 // "Edited"
```

Provide Korean and Chinese translations for all new keys.

**Verification:** TypeScript compiles. `foodLibraryApi.list()` type-checks. `searchFoodDatabase('chicken')` returns a `Promise<FoodSearchResult[]>`.

---

#### Step F2: Create solver utility

**Action:** Create `frontend/lib/optimizer/solveLP.ts`
**Max lines:** 120

```typescript
import solver from 'javascript-lp-solver'
import type { FoodItem } from '@/lib/api/foodLibrary'

export type ObjectiveMode = 'min_cost' | 'max_cost' | 'min_calories' | 'max_calories' | 'target_cost' | 'target_calories'

export interface Constraint {
  id: string
  category: 'calories' | 'protein' | 'carbohydrate' | 'fat' | 'fiber' | 'cost'
  operator: '>=' | '<=' | '='
  value: number
}

export interface FoodBounds {
  min?: number  // in 100g units
  max?: number  // in 100g units
}

export interface SolveInput {
  foods: FoodItem[]
  objective: ObjectiveMode
  targetValue?: number
  constraints: Constraint[]
  bounds: Record<number, FoodBounds>  // keyed by food ID
}

export interface SolveResultQuantity {
  food: FoodItem
  quantity100g: number
  quantityGrams: number
  cost: number
  calories: number
  protein: number
  carbohydrate: number
  fat: number
  fiber: number | null
}

export interface ConstraintSatisfaction {
  constraint: Constraint
  lhsValue: number
  satisfied: boolean
  slack: number
  tight: boolean
}

export interface SolveResult {
  feasible: boolean
  bounded: boolean
  objectiveValue: number
  quantities: SolveResultQuantity[]
  totals: { cost: number; calories: number; protein: number; carbohydrate: number; fat: number; fiber: number }
  constraintSatisfaction: ConstraintSatisfaction[]
}

export function solveLP(input: SolveInput): SolveResult { ... }
```

**Implementation logic for `solveLP`:**

1. Build `variables` object: for each food, create entry with all nutrient fields plus `_cost` and `_calories` fields (prefixed with `_` to avoid collision with constraint categories). Also add `_dummy: 0` for target modes.

2. Build `constraints` object:
   - For each user constraint: map `category` to the field name, map `operator` to `{ min/max/equal: value }`
   - For per-food bounds: create unique constraint names (`_bound_{foodId}_min`, `_bound_{foodId}_max`) where only the bounded food has coefficient 1 and all others have 0

3. Set `optimize` and `opType`:
   - `min_cost` → `optimize: '_cost', opType: 'min'`
   - `max_cost` → `optimize: '_cost', opType: 'max'`
   - `min_calories` → `optimize: '_calories', opType: 'min'`
   - `max_calories` → `optimize: '_calories', opType: 'max'`
   - `target_cost` → `optimize: '_dummy', opType: 'min'`, add constraint `_cost: { equal: targetValue }`
   - `target_calories` → `optimize: '_dummy', opType: 'min'`, add constraint `_calories: { equal: targetValue }`

4. Call `solver.Solve(model)`

5. Parse result:
   - Extract `feasible`, `bounded` from result
   - For each food: look up `result[foodKey]` (0 if absent) → compute derived values
   - Compute totals across all foods
   - Evaluate each constraint's LHS against its RHS

**Variable key naming:** Use a sanitized version of the food name (replace spaces with underscores, prefix with `f_`) to avoid collisions with solver internals. Map back to food IDs using a lookup.

**Verification:** Unit test (manual): create a simple 2-food, 1-constraint problem and verify solver returns expected quantities. Test infeasible case returns `feasible: false`.

---

#### Step F3: Create leaf components (parallel)

All files under `frontend/app/(app)/health/_components/optimizer/`.

First ensure the directory exists: `mkdir -p frontend/app/(app)/health/_components/optimizer`

Build these six files simultaneously (no inter-dependencies):
- `FoodSearchInput.tsx` (120 lines) — per section 5.3. Uses `searchFoodDatabase` from `@/lib/api/foodSearch`. Implements debounced autocomplete with keyboard navigation.
- `FoodSelector.tsx` (80 lines) — per section 5.5
- `ObjectiveSelector.tsx` (60 lines) — per section 5.5
- `ConstraintBuilder.tsx` (120 lines) — per section 5.5
- `FoodBoundsEditor.tsx` (80 lines) — per section 5.5
- `OptimizerResult.tsx` (150 lines) — per section 5.6

**Per-component verification:** Each renders without TypeScript errors. Props interface matches the spec. `FoodSearchInput` shows dropdown results when typing "chicken" (requires network).

---

#### Step F3b: Create FoodItemForm (depends on FoodSearchInput)

**Action:** Create `FoodItemForm.tsx` (200 lines) — per section 5.3c
- In **create mode**: uses `FoodSearchInput` for the name field. On search result selection, auto-fills all macro fields. Cost is always manual.
- In **edit mode**: uses plain text input for name (search disabled — macros already exist).
- Tracks `source` state: `'api'` when auto-filled from search, `'manual'` when user typed everything, `'edited'` when user modified auto-filled values. Displays a subtle source badge next to the macro section header.
- All auto-filled macro fields remain fully editable.

**Verification:** Create mode: type "chicken breast" → see dropdown → select result → macros fill automatically → cost field empty and highlighted. Edit mode: search disabled, all fields pre-filled from existing data.

---

#### Step F4: Create composite components

**Action:** Create `FoodLibraryManager.tsx` (200 lines) — per section 5.2
- Uses `FoodItemForm` for add/edit modals
- Uses `useMutation` for delete
- Renders food list with edit/delete actions
- Each food row shows a source indicator: "Auto-filled" pill badge if macros came from API, "Manual" if user entered everything manually, "Edited" if user modified API values

**Action:** Create `OptimizerPanel.tsx` (300 lines) — per section 5.4
- Orchestrates all optimizer sub-components
- Manages optimizer state (selected foods, objective, constraints, bounds, result)
- Calls `solveLP()` on solve button press
- Passes results to `OptimizerResult`

**Verification:** `OptimizerPanel` renders with an empty food library, showing the library manager with empty state. Adding a food via search auto-fills macros and creates it in the API. Adding a food manually (ignoring search) also works.

---

#### Step F5: Integrate into health page

**Action:** Edit `frontend/app/(app)/health/page.tsx`
- Add `activeView` state (`'overview' | 'optimizer'`)
- Add view toggle pills in the header area (between title and LOG button)
- Conditionally render existing overview content or `<OptimizerPanel />`
- Hide LOG dropdown when optimizer view is active
- Import `OptimizerPanel` from `./_components/optimizer/OptimizerPanel`

**Verification checklist:**
1. Health page loads with "Overview" selected by default — existing functionality unchanged
2. Clicking "Optimizer" shows the optimizer panel
3. Food library CRUD works (add, edit, delete foods)
4. Selecting foods + setting objective + adding constraints + clicking Solve produces a result
5. Infeasible constraint set shows calm error message
6. Switching back to "Overview" shows the original health page content
7. Mobile view: toggle pills work, optimizer stacks vertically
8. All text from translation keys (no hardcoded English)
9. No TypeScript errors
10. No console warnings

---

### Post-Build Verification

After all steps complete:

1. **Backend:** All 5 food library endpoints return correct responses. Events appear in `platform_outbox` after CRUD operations. Migration applied cleanly.
2. **Frontend:** `npx tsc --noEmit` passes. Optimizer produces correct results for known test cases.
3. **Integration test:** Create 3 foods → select all → minimize cost with protein >= 100g constraint → verify solution quantities sum to >= 100g protein at minimum cost.
4. **Design:** No 1px borders, no grey shadows, all pills, all specimen corners, sage palette throughout.
5. **Tone:** No prescriptive language in any UI copy. Error messages are calm and actionable.
6. **Edge cases:** Empty food library shows correct empty state. Zero-value solve (all quantities 0) displays correctly. Single food selected works.
