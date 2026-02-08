#!/usr/bin/env python3
"""Phase 5c no-op personalization check."""

from __future__ import annotations

import argparse

from lifeos import create_app
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.personalization import rank_insights


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify no-op personalization ordering.")
    parser.add_argument("--user-id", type=int, default=None)
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        query = InsightRecord.query
        if args.user_id is not None:
            query = query.filter_by(user_id=args.user_id)
        items = (
            query.order_by(
                InsightRecord.priority.desc(),
                InsightRecord.confidence_band.desc(),
                InsightRecord.created_at.desc(),
            )
            .limit(args.limit)
            .all()
        )
        if not items:
            print("phase5c: no insights found for check")
            return
        original = [rec.id for rec in items]
        ranked = [rec.id for rec in rank_insights(items[0].user_id, items)]
        if original != ranked:
            print("phase5c: personalization changed order (FAIL)")
            raise SystemExit(1)
        print("phase5c: personalization no-op verified (PASS)")


if __name__ == "__main__":
    main()
