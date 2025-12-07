"""Calendar HTML pages."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

calendar_pages_bp = Blueprint("calendar_pages", __name__)


@calendar_pages_bp.get("/")
@jwt_required(optional=True)
def calendar_view():
    """Main calendar view page."""
    return render_template("calendar/index.html")


@calendar_pages_bp.get("/review")
@jwt_required(optional=True)
def review_interpretations():
    """Review pending interpretations page."""
    return render_template("calendar/review.html")
