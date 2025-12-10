"""Pagination helper for SQLAlchemy queries."""

from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Query


def paginate(query: Query, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    page = max(page, 1)
    per_page = max(min(per_page, 100), 1)
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    total = query.order_by(None).count()
    return {"items": items, "page": page, "per_page": per_page, "total": total}
