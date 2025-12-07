"""Calendar domain controllers."""

from lifeos.domains.calendar.controllers.calendar_api import calendar_api_bp
from lifeos.domains.calendar.controllers.calendar_pages import calendar_pages_bp

__all__ = ["calendar_api_bp", "calendar_pages_bp"]
