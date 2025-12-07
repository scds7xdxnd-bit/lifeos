import pytest

from lifeos.core.events.event_bus import event_bus
from lifeos.core.events.event_service import log_event
from lifeos.extensions import db

pytestmark = pytest.mark.integration


def test_event_logging_and_subscription(app):
    received = []

    def handler(event):
        received.append(event.event_type)

    event_bus.subscribe("custom.test", handler)
    with app.app_context():
        log_event("custom.test", {"hello": "world"})
        db.session.commit()

    assert "custom.test" in received
