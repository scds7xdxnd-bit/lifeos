"""Insights API endpoints."""

from __future__ import annotations

from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from lifeos.core.insights.services import fetch_insights

insights_api_bp = Blueprint("insights_api", __name__)


@insights_api_bp.get("")
@jwt_required()
def list_insights():
    user_id = int(get_jwt_identity())
    records = fetch_insights(user_id, limit=50)
    return jsonify(
        {
            "ok": True,
            "insights": [
                {
                    "id": rec.id,
                    "type": rec.kind,
                    "message": rec.message,
                    "severity": rec.severity,
                    "event_type": rec.event_type,
                    "created_at": rec.created_at.isoformat(),
                    "data": rec.data,
                }
                for rec in records
            ],
        }
    )


@insights_api_bp.get("/proposals")
def list_proposals():
    """Legacy proposals endpoint (v1 fallback)."""
    from lifeos.core.insights.api_v1 import list_proposals_v1

    return list_proposals_v1()


@insights_api_bp.patch("/proposals/<int:interpretation_id>")
def decide_proposal(interpretation_id: int):
    """Legacy proposal decision endpoint (v1 fallback)."""
    from lifeos.core.insights.api_v1 import decide_proposal_v1

    return decide_proposal_v1(interpretation_id)
