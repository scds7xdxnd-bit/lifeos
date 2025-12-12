"""CSV import service for journal entries."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import List, Tuple

from lifeos.domains.finance.services.accounting_service import post_journal_entry


class ImportRow:
    def __init__(
        self,
        description: str,
        amount: float,
        debit_account_id: int,
        credit_account_id: int,
        posted_at: datetime | None = None,
    ):
        self.description = description
        self.amount = amount
        self.debit_account_id = debit_account_id
        self.credit_account_id = credit_account_id
        self.posted_at = posted_at

    def to_dict(self) -> dict:
        return {
            "description": self.description,
            "amount": self.amount,
            "debit_account_id": self.debit_account_id,
            "credit_account_id": self.credit_account_id,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
        }


def parse_csv(file_obj) -> List[ImportRow]:
    """Parse uploaded CSV into ImportRow list."""
    try:
        file_obj.seek(0)
    except Exception:
        pass
    try:
        content = file_obj.read().decode("utf-8")
    except AttributeError:
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    rows: List[ImportRow] = []
    for idx, row in enumerate(reader, start=1):
        try:
            amount = float(row.get("amount") or 0)
            debit_account_id = int(row.get("debit_account_id"))
            credit_account_id = int(row.get("credit_account_id"))
        except (TypeError, ValueError):
            raise ValueError("validation_error")
        desc = (row.get("description") or "").strip()
        posted_at_raw = row.get("posted_at") or row.get("date")
        posted_at = None
        if posted_at_raw:
            try:
                posted_at = datetime.fromisoformat(posted_at_raw)
            except ValueError:
                raise ValueError("validation_error")
        rows.append(
            ImportRow(desc, amount, debit_account_id, credit_account_id, posted_at)
        )
        if idx > 1000:
            break
    if not rows:
        raise ValueError("validation_error")
    return rows


def preview_csv(file_obj) -> List[dict]:
    return [row.to_dict() for row in parse_csv(file_obj)]


def commit_import(user_id: int, file_obj) -> Tuple[int, List[dict]]:
    """Create journal entries from CSV rows. Returns (created_count, errors)."""
    rows = parse_csv(file_obj)
    created = 0
    errors: List[dict] = []
    for idx, row in enumerate(rows, start=1):
        try:
            post_journal_entry(
                user_id=user_id,
                description=row.description or f"Imported txn {idx}",
                lines=[
                    {
                        "account_id": row.debit_account_id,
                        "debit": row.amount,
                        "credit": 0,
                        "memo": row.description,
                    },
                    {
                        "account_id": row.credit_account_id,
                        "debit": 0,
                        "credit": row.amount,
                        "memo": row.description,
                    },
                ],
                posted_at=row.posted_at,
            )
            created += 1
        except Exception as exc:
            errors.append({"row": idx, "error": str(exc)})
    return created, errors
