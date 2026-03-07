"""API response contracts for Phase 3b interface freeze."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Iterable, Optional

ALLOWED_SOURCES = {"user", "system", "imported"}
ALLOWED_STABILITY = {"stable", "conditional"}


@dataclass(frozen=True)
class ApiField:
    name: str
    type: str
    meaning: str
    source: str
    stability: str


@dataclass(frozen=True)
class ApiObject:
    name: str
    fields: list[ApiField]


@dataclass(frozen=True)
class ApiSchema:
    fields: list[ApiField]
    objects: list[ApiObject] = field(default_factory=list)


@dataclass(frozen=True)
class ApiContract:
    name: str
    method: str
    path: str
    version: str
    schema: ApiSchema
    schema_hash: str
    read_only: bool = True
    surface_key: Optional[str] = None


def _field_payload(field: ApiField) -> dict:
    return {
        "name": field.name,
        "type": field.type,
        "meaning": field.meaning,
        "source": field.source,
        "stability": field.stability,
    }


def _schema_payload(schema: ApiSchema) -> dict:
    fields = sorted((_field_payload(f) for f in schema.fields), key=lambda item: item["name"])
    objects = []
    for obj in sorted(schema.objects, key=lambda item: item.name):
        objects.append(
            {
                "name": obj.name,
                "fields": sorted((_field_payload(f) for f in obj.fields), key=lambda item: item["name"]),
            }
        )
    return {"fields": fields, "objects": objects}


def compute_schema_hash(schema: ApiSchema) -> str:
    payload = _schema_payload(schema)
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


INSIGHT_FEED_ITEM = ApiObject(
    name="InsightFeedItem",
    fields=[
        ApiField("id", "integer", "Insight record id", "system", "stable"),
        ApiField("user_id", "integer", "Owner user id", "system", "stable"),
        ApiField("message", "string", "Insight message", "system", "stable"),
        ApiField("insight_type", "string", "Insight type key", "system", "stable"),
        ApiField("severity", "string", "Insight severity", "system", "stable"),
        ApiField("data", "object", "Insight payload", "system", "conditional"),
        ApiField("source_event_type", "string", "Source event type", "system", "stable"),
        ApiField("source_event_id", "integer|null", "Source event id", "system", "stable"),
        ApiField("created_at", "string|null", "Insight creation time", "system", "stable"),
    ],
)

REVIEW_QUEUE_ITEM = ApiObject(
    name="ReviewQueueItem",
    fields=[
        ApiField("id", "integer", "Insight record id", "system", "stable"),
        ApiField("insight_type", "string", "Insight type key", "system", "stable"),
        ApiField("message", "string", "Insight message", "system", "stable"),
        ApiField("severity", "string", "Insight severity", "system", "stable"),
        ApiField("event_type", "string", "Source event type", "system", "stable"),
        ApiField("created_at", "string|null", "Insight creation time", "system", "stable"),
        ApiField("data", "object", "Insight payload", "system", "conditional"),
    ],
)

CALENDAR_INTERPRETATION_ITEM = ApiObject(
    name="CalendarInterpretationItem",
    fields=[
        ApiField("id", "integer", "Interpretation id", "system", "stable"),
        ApiField("calendar_event_id", "integer", "Calendar event id", "system", "stable"),
        ApiField("domain", "string", "Target domain", "system", "stable"),
        ApiField("record_type", "string", "Target record type", "system", "stable"),
        ApiField("record_id", "integer|null", "Linked record id", "system", "stable"),
        ApiField("confidence_score", "number", "Confidence score", "system", "stable"),
        ApiField("status", "string", "Interpretation status", "system", "stable"),
        ApiField("classification_data", "object", "Interpreter payload", "system", "conditional"),
        ApiField("created_at", "string", "Created timestamp", "system", "stable"),
        ApiField("updated_at", "string", "Updated timestamp", "system", "stable"),
    ],
)

CALENDAR_EVENT_ITEM = ApiObject(
    name="CalendarEventItem",
    fields=[
        ApiField("id", "integer", "Calendar event id", "system", "stable"),
        ApiField("user_id", "integer", "Owner user id", "system", "stable"),
        ApiField("title", "string", "Event title", "user", "stable"),
        ApiField("description", "string|null", "Event description", "user", "stable"),
        ApiField("start_time", "string", "Event start time", "user", "stable"),
        ApiField("end_time", "string|null", "Event end time", "user", "stable"),
        ApiField("all_day", "boolean", "All day flag", "user", "stable"),
        ApiField("location", "string|null", "Event location", "user", "stable"),
        ApiField("source", "string", "Event source", "system", "stable"),
        ApiField("external_id", "string|null", "External calendar id", "imported", "stable"),
        ApiField("color", "string|null", "Event color", "user", "stable"),
        ApiField("is_private", "boolean", "Privacy flag", "user", "stable"),
        ApiField("tags", "list[string]", "Event tags", "user", "stable"),
        ApiField("duration_minutes", "integer|null", "Duration minutes", "system", "stable"),
        ApiField("created_at", "string", "Created timestamp", "system", "stable"),
        ApiField("updated_at", "string", "Updated timestamp", "system", "stable"),
        ApiField(
            "interpretations", "list[CalendarInterpretationItem]|null", "Interpretations", "system", "conditional"
        ),
    ],
)

JOURNAL_ENTRY_ITEM = ApiObject(
    name="JournalEntryItem",
    fields=[
        ApiField("id", "integer", "Journal entry id", "system", "stable"),
        ApiField("entry_number", "integer", "User-scoped entry number", "system", "stable"),
        ApiField("description", "string|null", "Entry description", "user", "stable"),
        ApiField("posted_at", "string", "Posted timestamp", "system", "stable"),
        ApiField("lines", "integer", "Line count", "system", "stable"),
        ApiField("debit_total", "number", "Total debit", "system", "stable"),
        ApiField("credit_total", "number", "Total credit", "system", "stable"),
    ],
)

JOURNAL_LINE_ITEM = ApiObject(
    name="JournalLineItem",
    fields=[
        ApiField("id", "integer", "Journal line id", "system", "stable"),
        ApiField("account_id", "integer", "Account id", "system", "stable"),
        ApiField("account_name", "string|null", "Account name", "system", "stable"),
        ApiField("debit", "number", "Debit amount", "user", "stable"),
        ApiField("credit", "number", "Credit amount", "user", "stable"),
        ApiField("memo", "string|null", "Line memo", "user", "stable"),
    ],
)

TRIAL_BALANCE_ACCOUNT_ITEM = ApiObject(
    name="TrialBalanceAccountItem",
    fields=[
        ApiField("account_id", "integer", "Account id", "system", "stable"),
        ApiField("account_name", "string", "Account name", "system", "stable"),
        ApiField("account_code", "string|null", "Account code", "system", "stable"),
        ApiField("base_type", "string", "Account base type", "system", "stable"),
        ApiField("category_id", "integer|null", "Category id", "system", "stable"),
        ApiField("category_name", "string|null", "Category name", "system", "stable"),
        ApiField("normal_balance", "string", "Normal balance", "system", "stable"),
        ApiField("debit", "number", "Debit total", "system", "stable"),
        ApiField("credit", "number", "Credit total", "system", "stable"),
        ApiField("net", "number", "Net balance", "system", "stable"),
    ],
)

TRIAL_BALANCE_CATEGORY_ITEM = ApiObject(
    name="TrialBalanceCategoryItem",
    fields=[
        ApiField("base_type", "string", "Account base type", "system", "stable"),
        ApiField("category_id", "integer|null", "Category id", "system", "stable"),
        ApiField("category_name", "string", "Category name", "system", "stable"),
        ApiField("normal_balance", "string", "Normal balance", "system", "stable"),
        ApiField("debit", "number", "Debit total", "system", "stable"),
        ApiField("credit", "number", "Credit total", "system", "stable"),
        ApiField("net", "number", "Net balance", "system", "stable"),
    ],
)

RECEIVABLE_ITEM = ApiObject(
    name="ReceivableItem",
    fields=[
        ApiField("id", "integer", "Receivable id", "system", "stable"),
        ApiField("counterparty", "string", "Receivable counterparty", "user", "stable"),
        ApiField("principal", "number", "Receivable principal", "user", "stable"),
        ApiField("start_date", "string|null", "Start date", "user", "stable"),
        ApiField("due_date", "string|null", "Due date", "user", "stable"),
        ApiField("interest_rate", "number|null", "Interest rate", "user", "stable"),
    ],
)

RECEIVABLE_ENTRY_ITEM = ApiObject(
    name="ReceivableEntryItem",
    fields=[
        ApiField("id", "integer", "Receivable entry id", "system", "stable"),
        ApiField("tracker_id", "integer", "Receivable tracker id", "system", "stable"),
        ApiField("entry_date", "string", "Entry date", "user", "stable"),
        ApiField("amount", "number", "Entry amount", "user", "stable"),
        ApiField("memo", "string|null", "Entry memo", "user", "stable"),
    ],
)

FORECAST_ITEM = ApiObject(
    name="ForecastItem",
    fields=[
        ApiField("date", "string", "Forecast date", "system", "stable"),
        ApiField("projected_balance", "number", "Projected balance", "system", "stable"),
    ],
)


API_CONTRACTS: dict[str, ApiContract] = {
    "insights.feed.v1": ApiContract(
        name="insights.feed.v1",
        method="GET",
        path="/api/v1/insights/feed",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("page", "integer", "Current page", "system", "stable"),
                ApiField("per_page", "integer", "Items per page", "system", "stable"),
                ApiField("total", "integer", "Total items", "system", "stable"),
                ApiField("pages", "integer", "Total pages", "system", "stable"),
                ApiField("items", "list[InsightFeedItem]", "Insight records", "system", "stable"),
            ],
            objects=[INSIGHT_FEED_ITEM],
        ),
        schema_hash="8dbc9104cbff55bf00f7b7b7634a825ae6a8afe5b3e24d83c7926d10f44a0ab1",
        read_only=True,
    ),
    "insights.review_queue.v1": ApiContract(
        name="insights.review_queue.v1",
        method="GET",
        path="/api/v1/insights/review",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("items", "list[ReviewQueueItem]", "Review queue items", "system", "stable"),
                ApiField("limit", "integer", "Result limit", "system", "stable"),
                ApiField("offset", "integer", "Result offset", "system", "stable"),
            ],
            objects=[REVIEW_QUEUE_ITEM],
        ),
        schema_hash="8782b10d803c31e1ed1346ea7fdf7828273dbbdb94299894ee73cfb9c9de0d9c",
        read_only=True,
    ),
    "calendar.day_view.v1": ApiContract(
        name="calendar.day_view.v1",
        method="GET",
        path="/api/v1/calendar/day",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("window_start", "string", "Window start datetime", "system", "stable"),
                ApiField("window_end", "string", "Window end datetime", "system", "stable"),
                ApiField("events", "list[CalendarEventItem]", "Calendar events", "system", "stable"),
            ],
            objects=[CALENDAR_EVENT_ITEM, CALENDAR_INTERPRETATION_ITEM],
        ),
        schema_hash="af46907858bd6ccd63ac4990a98889d8cb47b04086ab7f8f478b2ca746bdf361",
        read_only=True,
    ),
    "calendar.week_view.v1": ApiContract(
        name="calendar.week_view.v1",
        method="GET",
        path="/api/v1/calendar/week",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("window_start", "string", "Window start datetime", "system", "stable"),
                ApiField("window_end", "string", "Window end datetime", "system", "stable"),
                ApiField("events", "list[CalendarEventItem]", "Calendar events", "system", "stable"),
            ],
            objects=[CALENDAR_EVENT_ITEM, CALENDAR_INTERPRETATION_ITEM],
        ),
        schema_hash="af46907858bd6ccd63ac4990a98889d8cb47b04086ab7f8f478b2ca746bdf361",
        read_only=True,
    ),
    "calendar.month_view.v1": ApiContract(
        name="calendar.month_view.v1",
        method="GET",
        path="/api/v1/calendar/month",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("window_start", "string", "Window start datetime", "system", "stable"),
                ApiField("window_end", "string", "Window end datetime", "system", "stable"),
                ApiField("spillover_days", "list[string]", "Spillover dates", "system", "stable"),
                ApiField("events", "list[CalendarEventItem]", "Calendar events", "system", "stable"),
            ],
            objects=[CALENDAR_EVENT_ITEM, CALENDAR_INTERPRETATION_ITEM],
        ),
        schema_hash="d98a3c7d6eb132cc06faf98c5ce853ef3727ba7074e69d0067565475bdf0f014",
        read_only=True,
    ),
    "calendar.ledger.v1": ApiContract(
        name="calendar.ledger.v1",
        method="GET",
        path="/api/v1/calendar/ledger",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("anchor", "string", "Anchor date", "system", "stable"),
                ApiField("direction", "string", "Paging direction", "system", "stable"),
                ApiField("cursor", "string|null", "Current cursor", "system", "stable"),
                ApiField("next_cursor", "string|null", "Next cursor", "system", "stable"),
                ApiField("prev_cursor", "string|null", "Previous cursor", "system", "stable"),
                ApiField("events", "list[CalendarEventItem]", "Calendar events", "system", "stable"),
            ],
            objects=[CALENDAR_EVENT_ITEM, CALENDAR_INTERPRETATION_ITEM],
        ),
        schema_hash="8197890b0ad0e4dfcf045f416f9b86bae331eba3f58987b0b6f6cac3d2db0b20",
        read_only=True,
    ),
    "finance.journal.list.v1": ApiContract(
        name="finance.journal.list.v1",
        method="GET",
        path="/api/finance/journal",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("entries", "list[JournalEntryItem]", "Journal entries", "system", "stable"),
                ApiField("total_entries", "integer", "Total entry count", "system", "stable"),
            ],
            objects=[JOURNAL_ENTRY_ITEM],
        ),
        schema_hash="bcbd495890e5eb2d02db32cb068b90d7057fe08fa5a95e9fe1eccfe1665afd98",
        read_only=True,
        surface_key="finance:journal",
    ),
    "finance.journal.detail.v1": ApiContract(
        name="finance.journal.detail.v1",
        method="GET",
        path="/api/finance/journal/entries/<id>",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("entry", "object", "Journal entry detail", "system", "stable"),
            ],
            objects=[
                ApiObject(
                    name="JournalEntryDetail",
                    fields=[
                        ApiField("id", "integer", "Journal entry id", "system", "stable"),
                        ApiField("description", "string|null", "Entry description", "user", "stable"),
                        ApiField("posted_at", "string", "Posted timestamp", "system", "stable"),
                        ApiField("debit_total", "number", "Total debit", "system", "stable"),
                        ApiField("credit_total", "number", "Total credit", "system", "stable"),
                        ApiField("lines", "list[JournalLineItem]", "Entry lines", "system", "stable"),
                    ],
                ),
                JOURNAL_LINE_ITEM,
            ],
        ),
        schema_hash="2fe6189694f38c9c543ca10306921b751cf3df41edb350c37139ea23ed5e8ace",
        read_only=True,
        surface_key="finance:journal",
    ),
    "finance.trial_balance.v1": ApiContract(
        name="finance.trial_balance.v1",
        method="GET",
        path="/api/finance/trial_balance",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("accounts", "list[TrialBalanceAccountItem]", "Account rows", "system", "stable"),
                ApiField("categories", "list[TrialBalanceCategoryItem]", "Category rows", "system", "stable"),
            ],
            objects=[TRIAL_BALANCE_ACCOUNT_ITEM, TRIAL_BALANCE_CATEGORY_ITEM],
        ),
        schema_hash="866bfc406f133632f47400a785e21174401b8cf6670ca3d9896b605577123f98",
        read_only=True,
        surface_key="finance:trial_balance",
    ),
    "finance.trial_balance.period.v1": ApiContract(
        name="finance.trial_balance.period.v1",
        method="GET",
        path="/api/finance/trial_balance/period",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField(
                    "totals",
                    "object",
                    "Account id -> debit/credit totals",
                    "system",
                    "stable",
                ),
            ],
        ),
        schema_hash="0d18f5bd4e54c26c093463b7c185743b72811525d1a063055840e6ef9d60935c",
        read_only=True,
        surface_key="finance:trial_balance",
    ),
    "finance.trial_balance.monthly.v1": ApiContract(
        name="finance.trial_balance.monthly.v1",
        method="GET",
        path="/api/finance/trial_balance/monthly",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField(
                    "months",
                    "object",
                    "YYYY-MM -> debit/credit totals",
                    "system",
                    "stable",
                ),
            ],
        ),
        schema_hash="f407116da146f90b4c5f8ba2ea5048eb6339fe31c3e123488a6cb6f8c380689c",
        read_only=True,
        surface_key="finance:trial_balance",
    ),
    "finance.receivables.list.v1": ApiContract(
        name="finance.receivables.list.v1",
        method="GET",
        path="/api/finance/receivables",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("items", "list[ReceivableItem]", "Receivables", "system", "stable"),
                ApiField("page", "integer", "Current page", "system", "stable"),
                ApiField("pages", "integer", "Total pages", "system", "stable"),
                ApiField("total", "integer", "Total items", "system", "stable"),
            ],
            objects=[RECEIVABLE_ITEM],
        ),
        schema_hash="3eca45eca9a0a6108ea119e9486480fcad60dc9d0d06363a056403848d9631af",
        read_only=True,
        surface_key="finance:receivables",
    ),
    "finance.receivables.detail.v1": ApiContract(
        name="finance.receivables.detail.v1",
        method="GET",
        path="/api/finance/receivables/<id>",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("tracker", "ReceivableItem", "Receivable detail", "system", "stable"),
            ],
            objects=[RECEIVABLE_ITEM],
        ),
        schema_hash="05995c3e7812c831619c0e4740cdfc151db207fa6f1904e2da8907e1f401e0a0",
        read_only=True,
        surface_key="finance:receivables",
    ),
    "finance.receivables.entries.v1": ApiContract(
        name="finance.receivables.entries.v1",
        method="GET",
        path="/api/finance/receivables/<id>/entries",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("items", "list[ReceivableEntryItem]", "Receivable entries", "system", "stable"),
                ApiField("page", "integer", "Current page", "system", "stable"),
                ApiField("pages", "integer", "Total pages", "system", "stable"),
                ApiField("total", "integer", "Total items", "system", "stable"),
            ],
            objects=[RECEIVABLE_ENTRY_ITEM],
        ),
        schema_hash="eb06bfa60052cfd20ef818f5f97002ab9e712d39526ca81fc1efc2c8eb9b2aae",
        read_only=True,
        surface_key="finance:receivables",
    ),
    "finance.forecast.v1": ApiContract(
        name="finance.forecast.v1",
        method="GET",
        path="/api/finance/forecast",
        version="1.0.0",
        schema=ApiSchema(
            fields=[
                ApiField("ok", "boolean", "Success flag", "system", "stable"),
                ApiField("forecast", "list[ForecastItem]", "Forecast rows", "system", "stable"),
            ],
            objects=[FORECAST_ITEM],
        ),
        schema_hash="0e9bfbcd1b432504d93cb14fee7af8daa223b0077dd886e91232974c86cdaff3",
        read_only=True,
        surface_key="finance:forecast",
    ),
}


def list_api_contracts() -> Iterable[ApiContract]:
    return API_CONTRACTS.values()


def get_api_contract(name: str) -> ApiContract | None:
    return API_CONTRACTS.get(name)


__all__ = [
    "ALLOWED_SOURCES",
    "ALLOWED_STABILITY",
    "ApiContract",
    "ApiField",
    "ApiObject",
    "ApiSchema",
    "API_CONTRACTS",
    "compute_schema_hash",
    "get_api_contract",
    "list_api_contracts",
]
