"""Finance domain event catalog."""

from __future__ import annotations

FINANCE_ACCOUNT_CREATED = "finance.account.created"
FINANCE_ACCOUNT_CATEGORY_UPDATED = "finance.account.category_updated"
FINANCE_TRANSACTION_CREATED = "finance.transaction.created"
FINANCE_JOURNAL_POSTED = "finance.journal.posted"
FINANCE_SCHEDULE_CREATED = "finance.schedule.created"
FINANCE_SCHEDULE_UPDATED = "finance.schedule.updated"
FINANCE_SCHEDULE_DELETED = "finance.schedule.deleted"
FINANCE_SCHEDULE_RECOMPUTED = "finance.schedule.recomputed"
FINANCE_RECEIVABLE_CREATED = "finance.receivable.created"
FINANCE_RECEIVABLE_ENTRY_RECORDED = "finance.receivable.entry_recorded"
FINANCE_ML_SUGGEST_ACCOUNTS = "finance.ml.suggest_accounts"
FINANCE_ML_FEEDBACK = "finance.ml.feedback"

EVENT_CATALOG = {
    FINANCE_ACCOUNT_CREATED: {
        "version": "v1",
        "payload": {
            "account_id": "int",
            "user_id": "int",
            "name": "str",
            "account_type": "str",  # 'asset', 'liability', 'equity', 'income', 'expense'
            "account_subtype": "str?",
            "category_id": "int?",
            "category_name": "str?",
            "category_base_type": "str?",
            "created_at": "datetime",
        },
    },
    FINANCE_ACCOUNT_CATEGORY_UPDATED: {
        "version": "v1",
        "payload": {
            "account_id": "int",
            "user_id": "int",
            "category_id": "int?",
            "category_name": "str?",
            "category_base_type": "str",
            "updated_at": "datetime",
        },
    },
    FINANCE_TRANSACTION_CREATED: {
        "version": "v1",
        "payload": {
            "transaction_id": "int",
            "user_id": "int",
            "amount": "decimal",
            "description": "str?",
            "category": "str?",
            "counterparty": "str?",
            "occurred_at": "datetime",
        },
    },
    FINANCE_JOURNAL_POSTED: {
        "version": "v1",
        "payload": {
            "entry_id": "int",
            "user_id": "int",
            "debit_total": "decimal",
            "credit_total": "decimal",
            "line_count": "int",
        },
    },
    FINANCE_SCHEDULE_CREATED: {
        "version": "v1",
        "payload": {
            "row_id": "int",
            "user_id": "int",
            "amount": "decimal",
            "account_id": "int",
            "event_date": "date",
        },
    },
    FINANCE_SCHEDULE_UPDATED: {
        "version": "v1",
        "payload": {
            "row_id": "int",
            "user_id": "int",
            "amount": "decimal?",
            "account_id": "int?",
            "event_date": "date?",
            "memo": "str?",
        },
    },
    FINANCE_SCHEDULE_DELETED: {
        "version": "v1",
        "payload": {
            "row_id": "int",
            "user_id": "int",
        },
    },
    FINANCE_SCHEDULE_RECOMPUTED: {
        "version": "v1",
        "payload": {
            "user_id": "int",
            "days": "int",
        },
    },
    FINANCE_RECEIVABLE_CREATED: {
        "version": "v1",
        "payload": {
            "tracker_id": "int",
            "user_id": "int",
            "principal": "decimal",
            "counterparty": "str",
            "start_date": "date",
            "due_date": "date?",
        },
    },
    FINANCE_RECEIVABLE_ENTRY_RECORDED: {
        "version": "v1",
        "payload": {
            "tracker_id": "int",
            "amount": "decimal",
            "entry_date": "date",
        },
    },
    FINANCE_ML_SUGGEST_ACCOUNTS: {
        "version": "v1",
        "payload": {
            "payload_version": "str",
            "user_id": "int",
            "description": "str",
            "suggestions": "list[int]",  # account_id candidates
            "model": "str",
            "model_version": "str?",
            "context": "dict?",
        },
    },
    FINANCE_ML_FEEDBACK: {
        "version": "v1",
        "payload": {
            "user_id": "int",
            "suggestion_id": "str",
            "accepted": "bool",
            "score": "float?",
        },
    },
}

__all__ = [
    "EVENT_CATALOG",
    "FINANCE_ACCOUNT_CREATED",
    "FINANCE_ACCOUNT_CATEGORY_UPDATED",
    "FINANCE_TRANSACTION_CREATED",
    "FINANCE_JOURNAL_POSTED",
    "FINANCE_SCHEDULE_CREATED",
    "FINANCE_SCHEDULE_UPDATED",
    "FINANCE_SCHEDULE_DELETED",
    "FINANCE_SCHEDULE_RECOMPUTED",
    "FINANCE_RECEIVABLE_CREATED",
    "FINANCE_RECEIVABLE_ENTRY_RECORDED",
    "FINANCE_ML_SUGGEST_ACCOUNTS",
    "FINANCE_ML_FEEDBACK",
]
