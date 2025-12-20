"""Phase 3b read-only endpoint guard tests."""

from __future__ import annotations

import pytest

from lifeos.core.users.models import User
from lifeos.core.utils.decorators import read_only_endpoint
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def test_read_only_endpoint_blocks_mutation(app):
    @read_only_endpoint
    def handler():
        db.session.add(User(email="readonly@example.com", password_hash="x"))
        db.session.flush()
        return {"ok": True}

    with app.test_request_context():
        response, status = handler()
        assert status == 409
        assert response.get_json()["error"] == "read_only_violation"

    assert User.query.filter_by(email="readonly@example.com").first() is None


def test_read_only_endpoint_allows_reads(app):
    @read_only_endpoint
    def handler():
        assert User.query.filter_by(email="test@example.com").first() is not None
        return {"ok": True}

    with app.test_request_context():
        response = handler()
        assert response == {"ok": True}
