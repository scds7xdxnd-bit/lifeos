"""Skill HTML pages."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

from lifeos.domains.skills.models.skill_models import Skill

skill_pages_bp = Blueprint("skill_pages", __name__)


@skill_pages_bp.get("/")
@jwt_required(optional=True)
def list_skills():
    skills = Skill.query.all()
    return render_template("skills/index.html", skills=skills)
