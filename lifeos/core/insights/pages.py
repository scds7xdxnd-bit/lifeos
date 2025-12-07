"""Insights pages."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

insights_pages_bp = Blueprint("insights_pages", __name__, template_folder="../../templates/insights")


@insights_pages_bp.get("")
@jwt_required(optional=True)
def insights_home():
    return render_template("insights/index.html")
