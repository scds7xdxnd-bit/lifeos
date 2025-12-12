"""Health HTML pages."""

from __future__ import annotations

from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

from lifeos.domains.health.models.biometrics import Biometric

health_pages_bp = Blueprint("health_pages", __name__)


@health_pages_bp.get("/")
@jwt_required(optional=True)
def health_dashboard():
    biometrics = Biometric.query.order_by(Biometric.date.desc(), Biometric.created_at.desc()).limit(20).all()
    return render_template("health/index.html", biometrics=biometrics)
