"""Project HTML pages."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

from lifeos.domains.projects.models.project import Project

project_pages_bp = Blueprint("project_pages", __name__)


@project_pages_bp.get("/")
@jwt_required(optional=True)
def projects_home():
    projects = Project.query.all()
    return render_template("projects/index.html", projects=projects)
