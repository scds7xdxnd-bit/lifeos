"""CSV import endpoints for finance data."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.core.utils.decorators import csrf_protected, require_roles
from lifeos.domains.finance.services import import_service

import_api_bp = Blueprint("finance_import_api", __name__)


def _get_file():
    file = request.files.get("file")
    if not file:
        return None, (jsonify({"ok": False, "error": "missing_file"}), 400)
    return file, None


@import_api_bp.post("/import/preview")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def import_preview():
    file, err = _get_file()
    if err:
        return err
    try:
        rows = import_service.preview_csv(file)
        return jsonify({"ok": True, "rows": rows, "count": len(rows)})
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    except Exception as exc:
        return (
            jsonify({"ok": False, "error": "import_failed", "details": str(exc)}),
            400,
        )


@import_api_bp.post("/import/commit")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
def import_commit():
    user_id = int(get_jwt_identity())
    file, err = _get_file()
    if err:
        return err
    try:
        created, errors = import_service.commit_import(user_id, file)
        return jsonify({"ok": True, "created": created, "errors": errors})
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    except Exception as exc:
        return (
            jsonify({"ok": False, "error": "import_failed", "details": str(exc)}),
            400,
        )
