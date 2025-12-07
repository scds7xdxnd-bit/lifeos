import pytest
from flask import Blueprint
from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.utils.decorators import require_roles


def test_require_roles_blocks_without_claims(app, client):
    bp = Blueprint("perm_test", __name__)

    @bp.get("/protected")
    @require_roles({"admin"})
    def protected():
        return {"ok": True}

    app.register_blueprint(bp)
    with app.app_context():
        token = create_access_token(identity="1", additional_claims={"roles": []})
    resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_require_roles_allows_with_claims(app, client):
    bp = Blueprint("perm_test2", __name__)

    @bp.get("/protected2")
    @require_roles({"admin"})
    def protected2():
        return {"ok": True}

    app.register_blueprint(bp)
    with app.app_context():
        token = create_access_token(identity="1", additional_claims={"roles": ["admin"]})
    resp = client.get("/protected2", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
