"""Insights pages."""

from __future__ import annotations

from flask import Blueprint, abort, current_app, redirect, render_template, url_for
from flask_jwt_extended import jwt_required
from flask_login import current_user

insights_pages_bp = Blueprint("insights_pages", __name__, template_folder="../../templates/insights")


def _alpha_shell_mode() -> bool:
    if not current_app.config.get("ENABLE_PRIVATE_ALPHA", False):
        return False
    if not current_app.config.get("ALPHA_HIDE_DOMAIN_CRUD", False):
        return False
    if current_user.is_authenticated and "admin" in getattr(current_user, "role_codes", []):
        return False
    return True


@insights_pages_bp.get("")
@insights_pages_bp.get("/")
@jwt_required(optional=True)
def insights_home():
    if _alpha_shell_mode():
        return redirect(url_for("insights_pages.inquiry_home"))
    return render_template("insights/index.html")


@insights_pages_bp.get("/inquiry")
@jwt_required(optional=True)
def inquiry_home():
    if not current_app.config.get("ENABLE_PHASE6_FOCUSED_INQUIRY", False):
        abort(404)
    return render_template("insights/inquiry.html")


@insights_pages_bp.get("/history")
@jwt_required(optional=True)
def inquiry_history():
    if not current_app.config.get("ENABLE_PHASE6_FOCUSED_INQUIRY", False):
        abort(404)
    return render_template("insights/history.html")


@insights_pages_bp.get("/data")
@jwt_required(optional=True)
def inquiry_data():
    if not current_app.config.get("ENABLE_PHASE6_FOCUSED_INQUIRY", False):
        abort(404)
    return render_template("insights/data.html")


@insights_pages_bp.get("/account-help")
@jwt_required(optional=True)
def inquiry_account_help():
    if not current_app.config.get("ENABLE_PHASE6_FOCUSED_INQUIRY", False):
        abort(404)
    return render_template("insights/account_help.html")
