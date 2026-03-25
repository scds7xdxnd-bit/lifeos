#!/usr/bin/env python3
"""Sync private-alpha invite state to Google Sheets.

Usage:
  PYTHONPATH=. DATABASE_URL=... GOOGLE_SERVICE_ACCOUNT_JSON='{"type": ...}' \
    python scripts/ops/private_alpha_invite_sheet_sync.py \
      --sheet-id <google-sheet-id> \
      --worksheet invites
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from lifeos import create_app
from lifeos.core.auth.models import PrivateAlphaInvite


def _iso(value: datetime | None) -> str:
    return value.isoformat() if value else ""


def _status(invite: PrivateAlphaInvite, now: datetime) -> str:
    if invite.revoked_at is not None:
        return "revoked"
    if invite.accepted_at is not None:
        return "accepted"
    if invite.expires_at is not None and invite.expires_at < now:
        return "expired"
    return "pending"


def _rows() -> list[list[str]]:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    invites = PrivateAlphaInvite.query.order_by(PrivateAlphaInvite.created_at.desc()).all()

    header = [
        "invite_id",
        "invited_email",
        "status",
        "created_at",
        "expires_at",
        "accepted_at",
        "revoked_at",
        "issued_by_user_id",
        "accepted_by_user_id",
        "token_hash_tail",
        "updated_sync_utc",
    ]
    rows: list[list[str]] = [header]
    synced_at = datetime.now(timezone.utc).isoformat()
    for invite in invites:
        rows.append(
            [
                str(invite.id),
                invite.invited_email,
                _status(invite, now),
                _iso(invite.created_at),
                _iso(invite.expires_at),
                _iso(invite.accepted_at),
                _iso(invite.revoked_at),
                str(invite.issued_by_user_id or ""),
                str(invite.accepted_by_user_id or ""),
                (invite.token_hash[-6:] if invite.token_hash else ""),
                synced_at,
            ]
        )
    return rows


def _sheet_service(creds_env_var: str):
    raw = os.environ.get(creds_env_var, "").strip()
    if not raw:
        raise RuntimeError(f"Missing required env var: {creds_env_var}")
    info = json.loads(raw)
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def sync_sheet(*, sheet_id: str, worksheet: str, creds_env_var: str) -> None:
    service = _sheet_service(creds_env_var)
    values = _rows()
    body = {"values": values}

    service.spreadsheets().values().clear(
        spreadsheetId=sheet_id,
        range=f"{worksheet}!A:Z",
        body={},
    ).execute()

    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=f"{worksheet}!A1",
        valueInputOption="RAW",
        body=body,
    ).execute()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync private-alpha invites to Google Sheets")
    parser.add_argument("--sheet-id", required=True, help="Google Sheet id")
    parser.add_argument("--worksheet", default="invites", help="Worksheet/tab name (default: invites)")
    parser.add_argument(
        "--creds-env-var",
        default="GOOGLE_SERVICE_ACCOUNT_JSON",
        help="Env var containing service-account JSON (default: GOOGLE_SERVICE_ACCOUNT_JSON)",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    app = create_app()
    with app.app_context():
        sync_sheet(sheet_id=args.sheet_id, worksheet=args.worksheet, creds_env_var=args.creds_env_var)
    print(f"Synced private_alpha_invite to Google Sheet {args.sheet_id} / worksheet {args.worksheet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
