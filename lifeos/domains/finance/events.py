"""Finance domain event catalog."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Event name constants
# ---------------------------------------------------------------------------

FINANCE_ACCOUNT_CREATED = "finance.account.created"
FINANCE_ACCOUNT_UPDATED = "finance.account.updated"
FINANCE_ACCOUNT_DEACTIVATED = "finance.account.deactivated"
FINANCE_ACCOUNT_CATEGORY_UPDATED = "finance.account.category_updated"
FINANCE_ACCOUNTS_SEEDED = "finance.accounts.seeded"
FINANCE_EXCHANGE_RATE_SET = "finance.exchange_rate.set"

FINANCE_TRANSACTION_CREATED = "finance.transaction.created"
FINANCE_TRANSACTION_EDITED = "finance.transaction.edited"
FINANCE_TRANSACTION_VOIDED = "finance.transaction.voided"
FINANCE_TRANSACTION_INFERRED = "finance.transaction.inferred"

FINANCE_JOURNAL_POSTED = "finance.journal.posted"

FINANCE_SCHEDULE_CREATED = "finance.schedule.created"
FINANCE_SCHEDULE_UPDATED = "finance.schedule.updated"
FINANCE_SCHEDULE_DELETED = "finance.schedule.deleted"
FINANCE_SCHEDULE_RECOMPUTED = "finance.schedule.recomputed"

FINANCE_RECEIVABLE_CREATED = "finance.receivable.created"
FINANCE_RECEIVABLE_ENTRY_RECORDED = "finance.receivable.entry_recorded"

FINANCE_ML_SUGGEST_ACCOUNTS = "finance.ml.suggest_accounts"
FINANCE_ML_FEEDBACK = "finance.ml.feedback"

# ---------------------------------------------------------------------------
# Event catalog (authoritative payloads — documentation + consumer reference)
# ---------------------------------------------------------------------------

EVENT_CATALOG = {
    FINANCE_ACCOUNT_CREATED: {
        "version": "v1",
        "payload": {
            "account_id": "int",
            "user_id": "int",
            "name": "str",
            "account_type": "str",
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
    FINANCE_ACCOUNT_UPDATED: {
        "version": "v1",
        "payload": {
            "account_id": "int",
            "user_id": "int",
            "fields": "list[str]",
            "updated_at": "datetime",
            "payload_version": "str",
        },
    },
    FINANCE_ACCOUNT_DEACTIVATED: {
        "version": "v1",
        "payload": {
            "account_id": "int",
            "user_id": "int",
            "deactivated_at": "datetime",
            "payload_version": "str",
        },
    },
    FINANCE_ACCOUNTS_SEEDED: {
        "version": "v1",
        "payload": {
            "user_id": "int",
            "account_count": "int",
            "category_count": "int",
            "payload_version": "str",
        },
    },
    FINANCE_EXCHANGE_RATE_SET: {
        "version": "v1",
        "payload": {
            "rate_id": "int",
            "user_id": "int",
            "from_currency": "str",
            "to_currency": "str",
            "rate": "decimal",
            "effective_date": "date",
            "payload_version": "str",
        },
    },
    # v2 adds currency_code. Legacy v1 rows have no currency_code —
    # consumers must treat missing currency_code as the user's base currency.
    FINANCE_TRANSACTION_CREATED: {
        "version": "v2",
        "payload": {
            "transaction_id": "int",
            "user_id": "int",
            "amount": "decimal",
            "currency_code": "str?",
            "description": "str?",
            "category": "str?",
            "counterparty": "str?",
            "occurred_at": "datetime",
            "source": "str?",
            "calendar_event_id": "int?",
            "confidence_score": "float?",
            "inferred_status": "str?",
            "payload_version": "str",
        },
    },
    FINANCE_TRANSACTION_EDITED: {
        "version": "v1",
        "payload": {
            "transaction_id": "int",
            "user_id": "int",
            "changed_fields": "list[str]",
            "edited_at": "datetime",
            "payload_version": "str",
        },
    },
    FINANCE_TRANSACTION_VOIDED: {
        "version": "v1",
        "payload": {
            "transaction_id": "int",
            "reversal_entry_id": "int",
            "user_id": "int",
            "reason": "str?",
            "voided_at": "datetime",
            "payload_version": "str",
        },
    },
    FINANCE_TRANSACTION_INFERRED: {
        "version": "v1",
        "payload": {
            "transaction_id": "int",
            "calendar_event_id": "int",
            "user_id": "int",
            "confidence_score": "float",
            "amount": "decimal?",
            "description": "str?",
            "payload_version": "str",
            "model_version": "str?",
            "is_false_positive": "bool?",
            "is_false_negative": "bool?",
        },
    },
    # v2 adds currency_code. Legacy v1 rows have no currency_code.
    FINANCE_JOURNAL_POSTED: {
        "version": "v2",
        "payload": {
            "entry_id": "int",
            "user_id": "int",
            "debit_total": "decimal",
            "credit_total": "decimal",
            "line_count": "int",
            "currency_code": "str?",
            "payload_version": "str",
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
            "fields": "dict",
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
            "user_id": "int",
        },
    },
    FINANCE_ML_SUGGEST_ACCOUNTS: {
        "version": "v1",
        "payload": {
            "payload_version": "str",
            "user_id": "int",
            "description": "str",
            "suggestions": "list[int]",
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
    "FINANCE_ACCOUNT_UPDATED",
    "FINANCE_ACCOUNT_DEACTIVATED",
    "FINANCE_ACCOUNT_CATEGORY_UPDATED",
    "FINANCE_ACCOUNTS_SEEDED",
    "FINANCE_EXCHANGE_RATE_SET",
    "FINANCE_TRANSACTION_CREATED",
    "FINANCE_TRANSACTION_EDITED",
    "FINANCE_TRANSACTION_VOIDED",
    "FINANCE_TRANSACTION_INFERRED",
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
