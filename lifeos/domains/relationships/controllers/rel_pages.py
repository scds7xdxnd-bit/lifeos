"""Relationship HTML pages."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

from lifeos.domains.relationships.models.contact import Contact

rel_pages_bp = Blueprint("relationships_pages", __name__)


@rel_pages_bp.get("/")
@jwt_required(optional=True)
def relationships_home():
    contacts = Contact.query.all()
    return render_template("relationships/index.html", contacts=contacts)

