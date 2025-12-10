"""Habit HTML pages."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

from lifeos.domains.habits.models.habit import Habit

habit_pages_bp = Blueprint("habit_pages", __name__)


@habit_pages_bp.get("/")
@jwt_required(optional=True)
def list_habits():
    habits = Habit.query.all()
    return render_template("habits/index.html", habits=habits)
