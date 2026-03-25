#!/usr/bin/env python3
"""Private alpha invite admin helper for Product/Admin Ops."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from urllib.parse import urlencode

from sqlalchemy import or_

from lifeos import create_app
from lifeos.core.auth.auth_service import issue_private_alpha_invite
from lifeos.core.auth.models import PrivateAlphaInvite, Role
from lifeos.core.private_alpha import alpha_flags, hash_invite_token
from lifeos.core.users.models import User
from lifeos.extensions import db


def _active_alpha_user_count() -> int:
    return (
        db.session.query(User.id)
        .join(User.roles)
        .filter(Role.name == "alpha_user", User.is_active.is_(True))
        .distinct()
        .count()
    )


def _pending_invite_count(now: datetime) -> int:
    return (
        PrivateAlphaInvite.query.filter(
            PrivateAlphaInvite.accepted_at.is_(None),
            PrivateAlphaInvite.revoked_at.is_(None),
            or_(PrivateAlphaInvite.expires_at.is_(None), PrivateAlphaInvite.expires_at >= now),
        )
        .count()
    )


def _print_capacity(cohort_target: int | None) -> tuple[int, int, int]:
    now = datetime.utcnow()
    flags = alpha_flags()
    accepted_users = _active_alpha_user_count()
    pending_invites = _pending_invite_count(now)
    max_users = int(flags.max_users or 0)
    cohort_limit = max(int(cohort_target or max_users), 0)
    issue_allowed = max(min(cohort_limit, max_users) - accepted_users - pending_invites, 0)

    print(f"accepted_users={accepted_users}")
    print(f"pending_invites={pending_invites}")
    print(f"alpha_max_users={max_users}")
    if cohort_target is not None:
        print(f"cohort_target={cohort_target}")
    print(f"issue_allowed={issue_allowed}")
    return accepted_users, pending_invites, max_users


def _cmd_status(args: argparse.Namespace) -> int:
    _print_capacity(args.cohort_target)
    return 0


def _resolve_status(invite: PrivateAlphaInvite, now: datetime) -> str:
    if invite.revoked_at is not None:
        return "revoked"
    if invite.accepted_at is not None:
        return "accepted"
    if invite.expires_at is not None and invite.expires_at < now:
        return "expired"
    return "pending"


def _cmd_list(args: argparse.Namespace) -> int:
    now = datetime.utcnow()
    query = PrivateAlphaInvite.query.order_by(PrivateAlphaInvite.created_at.desc())
    if args.status:
        filter_status = args.status.strip().lower()
        if filter_status == "accepted":
            query = query.filter(PrivateAlphaInvite.accepted_at.isnot(None), PrivateAlphaInvite.revoked_at.is_(None))
        elif filter_status == "revoked":
            query = query.filter(PrivateAlphaInvite.revoked_at.isnot(None))
        elif filter_status == "expired":
            query = query.filter(
                PrivateAlphaInvite.accepted_at.is_(None),
                PrivateAlphaInvite.revoked_at.is_(None),
                PrivateAlphaInvite.expires_at.isnot(None),
                PrivateAlphaInvite.expires_at < now,
            )
        elif filter_status == "pending":
            query = query.filter(
                PrivateAlphaInvite.accepted_at.is_(None),
                PrivateAlphaInvite.revoked_at.is_(None),
                or_(PrivateAlphaInvite.expires_at.is_(None), PrivateAlphaInvite.expires_at >= now),
            )
        else:
            print(f"ERROR: unknown status filter '{args.status}'; use pending/accepted/expired/revoked.", file=sys.stderr)
            return 2

    invites = query.all()
    if not invites:
        print("No invites found.")
        return 0

    print(f"{'id':<6} {'email':<30} {'status':<10} {'created':<20} {'expires':<20} {'token_hash_tail':<15}")
    print("-" * 101)
    for inv in invites:
        status = _resolve_status(inv, now)
        created = inv.created_at.strftime("%Y-%m-%d %H:%M") if inv.created_at else "-"
        expires = inv.expires_at.strftime("%Y-%m-%d %H:%M") if inv.expires_at else "never"
        tail = inv.token_hash[-6:] if inv.token_hash else "-"
        print(f"{inv.id:<6} {inv.invited_email:<30} {status:<10} {created:<20} {expires:<20} {tail:<15}")

    print(f"\ntotal={len(invites)}")
    return 0


def _cmd_issue(args: argparse.Namespace) -> int:
    flags = alpha_flags()
    if not flags.enabled:
        print("ERROR: ENABLE_PRIVATE_ALPHA is false.", file=sys.stderr)
        return 2
    if not flags.invite_only:
        print("ERROR: ALPHA_INVITE_ONLY is false.", file=sys.stderr)
        return 2

    accepted_users, pending_invites, max_users = _print_capacity(args.cohort_target)
    cohort_target = int(args.cohort_target or max_users)
    if accepted_users + pending_invites >= cohort_target:
        print("ERROR: cohort target reached; issue blocked.", file=sys.stderr)
        return 2
    if accepted_users + pending_invites >= max_users:
        print("ERROR: ALPHA_MAX_USERS reached; issue blocked.", file=sys.stderr)
        return 2

    expires_at = None
    if args.expires_days and args.expires_days > 0:
        expires_at = datetime.utcnow() + timedelta(days=args.expires_days)

    invite, raw_token = issue_private_alpha_invite(
        args.email.strip(),
        issued_by_user_id=args.issued_by_user_id,
        expires_at=expires_at,
    )
    base_url = args.base_url.rstrip("/")
    print(f"invite_id={invite.id}")
    print(f"invite_token={raw_token}")
    invite_query = urlencode({"token": raw_token, "email": invite.invited_email})
    print(f"invite_url={base_url}/login?{invite_query}")
    print(f"token_tail={raw_token[-6:]}")
    return 0


def _find_invite(args: argparse.Namespace) -> PrivateAlphaInvite | None:
    if args.invite_id is not None:
        return PrivateAlphaInvite.query.filter_by(id=args.invite_id).first()
    if args.invite_token:
        return PrivateAlphaInvite.query.filter_by(token_hash=hash_invite_token(args.invite_token.strip())).first()
    return None


def _cmd_revoke(args: argparse.Namespace) -> int:
    invite = _find_invite(args)
    if invite is None:
        print("ERROR: invite not found.", file=sys.stderr)
        return 2
    if invite.accepted_at is not None and not args.force:
        print("ERROR: invite already accepted; pass --force to mark revoked anyway.", file=sys.stderr)
        return 2
    if invite.revoked_at is not None:
        print(f"invite_id={invite.id} already_revoked_at={invite.revoked_at.isoformat()}")
        return 0
    invite.revoked_at = datetime.utcnow()
    db.session.add(invite)
    db.session.commit()
    print(f"invite_id={invite.id} revoked_at={invite.revoked_at.isoformat()}")
    if args.reason:
        print(f"reason={args.reason.strip()}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Private alpha invite admin helper.")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="Show invite capacity counters.")
    status.add_argument("--cohort-target", type=int, default=None, help="Current cohort target cap.")
    status.set_defaults(func=_cmd_status)

    list_cmd = sub.add_parser("list", help="List invite tokens.")
    list_cmd.add_argument("--status", default=None, help="Filter by status: pending, accepted, expired, revoked.")
    list_cmd.set_defaults(func=_cmd_list)

    issue = sub.add_parser("issue", help="Issue an invite token.")
    issue.add_argument("--email", required=True, help="Invited user email.")
    issue.add_argument("--issued-by-user-id", type=int, default=None, help="Operator user id for audit fields.")
    issue.add_argument("--expires-days", type=int, default=7, help="Invite expiry days; 0 disables expiry.")
    issue.add_argument("--cohort-target", type=int, required=True, help="Current cohort target cap.")
    issue.add_argument("--base-url", default="http://127.0.0.1:8000", help="App base URL for invite link output.")
    issue.set_defaults(func=_cmd_issue)

    revoke = sub.add_parser("revoke", help="Revoke an invite token.")
    revoke.add_argument("--invite-id", type=int, default=None, help="Invite row id.")
    revoke.add_argument("--invite-token", default=None, help="Raw invite token.")
    revoke.add_argument("--reason", default="", help="Revocation reason for operator logs.")
    revoke.add_argument("--force", action="store_true", help="Allow revoking accepted invites.")
    revoke.set_defaults(func=_cmd_revoke)
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    app = create_app()
    with app.app_context():
        return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
