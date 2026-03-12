from __future__ import annotations

from datetime import date

import pytest
from flask_jwt_extended import create_access_token

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.finance.services import forecast_service
from lifeos.extensions import db


pytestmark = pytest.mark.unit


def _auth_header(app, user_id: int):
    with app.app_context():
        token = create_access_token(identity=str(user_id), additional_claims={"roles": []})
    return {"Authorization": f"Bearer {token}"}


def _create_user(app) -> int:
    with app.app_context():
        user = User(email="forecast-unit@test.com", password_hash=hash_password("pw"))
        db.session.add(user)
        db.session.commit()
        return int(user.id)


def test_forecast_endpoint_accepts_days_query_param(app, client):
    user_id = _create_user(app)
    headers = _auth_header(app, user_id)

    resp = client.get("/api/finance/forecast?days=30", headers=headers)
    assert resp.status_code == 200

    body = resp.get_json()
    assert body["ok"] is True
    assert isinstance(body["forecast"], list)
    assert body["forecast"][0]["date"] == date.today().isoformat()


def test_generate_forecast_returns_cached_payload_when_available(app, monkeypatch):
    with app.app_context():
        cached = [{"date": date.today().isoformat(), "projected_balance": 12.5}]
        monkeypatch.setattr(forecast_service.read_cache, "get", lambda scope, uid, key: cached)

        result = forecast_service.generate_forecast(user_id=1, days=30)
        assert result == cached
