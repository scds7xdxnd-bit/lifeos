"""Seed 15 demo foods (snacks, red meat, white meat, veggies, carbs, fats) for the demo user."""

from __future__ import annotations

from lifeos import create_app
from lifeos.core.users.models import User
from lifeos.domains.health.services import create_food_item

FOODS = [
    # ── Snacks ──────────────────────────────────────────────────────────
    {
        "name": "Mixed Nuts",
        "cost_per_100g": 3.50,
        "calories_per_100g": 607,
        "protein_per_100g": 15.9,
        "carbohydrate_per_100g": 21.5,
        "fat_per_100g": 53.7,
        "fiber_per_100g": 6.8,
    },
    {
        "name": "Rice Cakes (plain)",
        "cost_per_100g": 0.80,
        "calories_per_100g": 387,
        "protein_per_100g": 8.2,
        "carbohydrate_per_100g": 81.0,
        "fat_per_100g": 3.0,
        "fiber_per_100g": 2.0,
    },
    # ── Red Meats ───────────────────────────────────────────────────────
    {
        "name": "Beef Mince (80/20)",
        "cost_per_100g": 1.80,
        "calories_per_100g": 254,
        "protein_per_100g": 26.0,
        "carbohydrate_per_100g": 0.0,
        "fat_per_100g": 17.0,
        "fiber_per_100g": None,
    },
    {
        "name": "Lamb Shoulder",
        "cost_per_100g": 2.20,
        "calories_per_100g": 282,
        "protein_per_100g": 24.0,
        "carbohydrate_per_100g": 0.0,
        "fat_per_100g": 20.0,
        "fiber_per_100g": None,
    },
    {
        "name": "Pork Belly",
        "cost_per_100g": 1.40,
        "calories_per_100g": 518,
        "protein_per_100g": 9.3,
        "carbohydrate_per_100g": 0.0,
        "fat_per_100g": 54.0,
        "fiber_per_100g": None,
    },
    # ── White Meats / Fish ──────────────────────────────────────────────
    {
        "name": "Chicken Breast",
        "cost_per_100g": 1.20,
        "calories_per_100g": 165,
        "protein_per_100g": 31.0,
        "carbohydrate_per_100g": 0.0,
        "fat_per_100g": 3.6,
        "fiber_per_100g": None,
    },
    {
        "name": "Salmon Fillet",
        "cost_per_100g": 3.00,
        "calories_per_100g": 208,
        "protein_per_100g": 20.0,
        "carbohydrate_per_100g": 0.0,
        "fat_per_100g": 13.0,
        "fiber_per_100g": None,
    },
    {
        "name": "Tuna (canned in water)",
        "cost_per_100g": 0.60,
        "calories_per_100g": 132,
        "protein_per_100g": 28.0,
        "carbohydrate_per_100g": 0.0,
        "fat_per_100g": 1.0,
        "fiber_per_100g": None,
    },
    # ── Vegetables ──────────────────────────────────────────────────────
    {
        "name": "Broccoli",
        "cost_per_100g": 0.40,
        "calories_per_100g": 34,
        "protein_per_100g": 2.8,
        "carbohydrate_per_100g": 7.0,
        "fat_per_100g": 0.4,
        "fiber_per_100g": 2.6,
    },
    {
        "name": "Spinach",
        "cost_per_100g": 0.50,
        "calories_per_100g": 23,
        "protein_per_100g": 2.9,
        "carbohydrate_per_100g": 3.6,
        "fat_per_100g": 0.4,
        "fiber_per_100g": 2.2,
    },
    {
        "name": "Sweet Potato",
        "cost_per_100g": 0.35,
        "calories_per_100g": 86,
        "protein_per_100g": 1.6,
        "carbohydrate_per_100g": 20.0,
        "fat_per_100g": 0.1,
        "fiber_per_100g": 3.0,
    },
    # ── Carbs ────────────────────────────────────────────────────────────
    {
        "name": "White Rice (cooked)",
        "cost_per_100g": 0.15,
        "calories_per_100g": 130,
        "protein_per_100g": 2.7,
        "carbohydrate_per_100g": 28.0,
        "fat_per_100g": 0.3,
        "fiber_per_100g": 0.4,
    },
    {
        "name": "Rolled Oats",
        "cost_per_100g": 0.25,
        "calories_per_100g": 389,
        "protein_per_100g": 16.9,
        "carbohydrate_per_100g": 66.3,
        "fat_per_100g": 6.9,
        "fiber_per_100g": 10.6,
    },
    # ── Fats ─────────────────────────────────────────────────────────────
    {
        "name": "Olive Oil",
        "cost_per_100g": 1.50,
        "calories_per_100g": 884,
        "protein_per_100g": 0.0,
        "carbohydrate_per_100g": 0.0,
        "fat_per_100g": 100.0,
        "fiber_per_100g": None,
    },
    {
        "name": "Avocado",
        "cost_per_100g": 1.20,
        "calories_per_100g": 160,
        "protein_per_100g": 2.0,
        "carbohydrate_per_100g": 8.5,
        "fat_per_100g": 14.7,
        "fiber_per_100g": 6.7,
    },
]


def main() -> None:
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email="demo@lifeos.test").first()
        if not user:
            print("Demo user not found. Run seed_demo.py first.")
            return

        added = skipped = 0
        for food in FOODS:
            try:
                create_food_item(user.id, **food)
                print(f"  + {food['name']}")
                added += 1
            except ValueError as exc:
                if str(exc) == "duplicate":
                    print(f"  ~ {food['name']} (already exists, skipped)")
                    skipped += 1
                else:
                    raise

        print(f"\nDone — {added} added, {skipped} skipped for {user.email}")


if __name__ == "__main__":
    main()
