"""Journal HTML pages."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.domains.journal.services import journal_service

journal_pages_bp = Blueprint("journal_pages", __name__)


@journal_pages_bp.get("/")
@jwt_required(optional=True)
def journal_home():
    user_id = get_jwt_identity()
    entries = []
    if user_id:
        entries, _ = journal_service.list_entries(user_id=user_id)
    return render_template("journal/index.html", entries=entries)
