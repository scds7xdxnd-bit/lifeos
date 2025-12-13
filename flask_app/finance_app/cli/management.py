"""CLI management commands."""
import datetime
import os
from pathlib import Path

import click
from flask.cli import with_appcontext

try:
    from alembic import command as alembic_command
    from alembic.config import Config
except ImportError:  # pragma: no cover - only hits when alembic is not installed
    alembic_command = None

    class Config:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise RuntimeError("Alembic is not installed; install it to run migration commands.")

from finance_app.extensions import db
from finance_app.lib.dates import _parse_date_tuple
from finance_app.models.accounting_models import (
    Account,
    AccountSuggestionHint,
    JournalEntry,
    Transaction,
)
from finance_app.services.account_service import assign_codes_for_user, ensure_account
from finance_app.services.journal_service import (
    JournalBalanceError,
    JournalLinePayload,
    _validate_balanced,
    create_journal_entry,
)


def _alembic_config(db_url: str | None = None) -> Config:
    """Build an Alembic Config anchored to the repository root."""
    repo_root = Path(__file__).resolve().parents[2]
    cfg = Config(str(repo_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(repo_root / "alembic"))
    env_url = os.environ.get("ALEMBIC_DATABASE_URL")
    if db_url:
        cfg.set_main_option("sqlalchemy.url", db_url)
    elif env_url:
        cfg.set_main_option("sqlalchemy.url", env_url)
    return cfg


@click.command("migrate-to-journal")
@click.option("--user-id", type=int, default=None, help="Only migrate transactions for this user id")
@click.option("--dry-run", is_flag=True, default=False, help="Do not write, only print a summary")
@click.option("--limit", type=int, default=None, help="Limit number of transactions to migrate")
@with_appcontext
def migrate_to_journal_cli(user_id, dry_run, limit):
    """Create JournalEntry + JournalLine rows from existing simple Transaction rows."""
    from decimal import ROUND_HALF_UP, Decimal

    q = Transaction.query
    if user_id is not None:
        q = q.filter(Transaction.user_id == int(user_id))
    q = q.order_by(Transaction.id.asc())
    if limit is not None:
        q = q.limit(int(limit))
    rows = q.all()
    created = 0
    skipped = 0
    imbalanced = 0
    for t in rows:
        ref = f"TX:{t.id}"
        exists = JournalEntry.query.filter_by(user_id=t.user_id, reference=ref).first()
        if exists:
            skipped += 1
            continue
        date_parsed = None
        try:
            if t.date_parsed:
                date_parsed = t.date_parsed
            else:
                y, m, d = _parse_date_tuple(t.date)
                if y and m and d:
                    import datetime as _dt

                    date_parsed = _dt.date(y, m, d)
        except Exception:
            date_parsed = None
        line_payloads: list[JournalLinePayload] = []
        if (t.debit_amount or 0) != 0:
            acc = Account.query.get(t.debit_account_id) if t.debit_account_id else None
            if not acc:
                acc = ensure_account(t.user_id, t.debit_account or "Unknown")
            amt = Decimal(str(t.debit_amount or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            line_payloads.append(JournalLinePayload(account_id=acc.id, dc="D", amount=amt, line_no=1))
        if (t.credit_amount or 0) != 0:
            acc = Account.query.get(t.credit_account_id) if t.credit_account_id else None
            if not acc:
                acc = ensure_account(t.user_id, t.credit_account or "Unknown")
            amt = Decimal(str(t.credit_amount or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            line_payloads.append(JournalLinePayload(account_id=acc.id, dc="C", amount=amt, line_no=2))
        try:
            _validate_balanced(line_payloads)
        except JournalBalanceError:
            imbalanced += 1
            continue
        if dry_run:
            created += 1
            continue
        try:
            create_journal_entry(
                user_id=t.user_id,
                date=t.date,
                date_parsed=date_parsed,
                description=t.description,
                reference=ref,
                lines=line_payloads,
            )
            created += 1
        except JournalBalanceError:
            imbalanced += 1
            db.session.rollback()
            continue
    if not dry_run:
        db.session.commit()
    click.echo(f"Journal migration: created={created}, skipped={skipped}, imbalanced={imbalanced}, total_considered={len(rows)}")


@click.command("merge-accounts")
@click.option("--dry-run", is_flag=True, default=False, help="Analyze and report without modifying the DB")
@with_appcontext
def merge_accounts_cli(dry_run):
    """Merge duplicate Account rows by name (case-insensitive) per user and update transactions."""
    user_ids = [row[0] for row in db.session.query(Account.user_id).distinct().all()]
    for uid in user_ids:
        accounts = Account.query.filter_by(user_id=uid, active=True).order_by(Account.id.asc()).all()
        buckets = {}
        for a in accounts:
            key = (a.name or "").strip().lower()
            if key:
                buckets.setdefault(key, []).append(a)
        for key, accs in buckets.items():
            if len(accs) <= 1:
                continue
            canonical = accs[0]
            if not canonical.code:
                for other in accs[1:]:
                    if other.code:
                        canonical.code = other.code
                        break
            dup_names = [a.name for a in accs[1:]]
            if not dry_run:
                for dn in dup_names:
                    Transaction.query.filter_by(user_id=uid, debit_account=dn).update(
                        {Transaction.debit_account: canonical.name, Transaction.debit_account_id: canonical.id}
                    )
                    Transaction.query.filter_by(user_id=uid, credit_account=dn).update(
                        {Transaction.credit_account: canonical.name, Transaction.credit_account_id: canonical.id}
                    )
                for d in accs[1:]:
                    db.session.delete(d)
        if not dry_run:
            db.session.commit()
    click.echo("Merge complete" + (" (dry-run)" if dry_run else ""))


@click.command("upgrade-schema")
@click.option("--backfill", is_flag=True, default=False, help="Populate new columns for existing data")
@click.option(
    "--db-url",
    default=None,
    help="Optional DB URL override for Alembic (defaults to alembic.ini or ALEMBIC_DATABASE_URL).",
)
@with_appcontext
def upgrade_schema_cli(backfill, db_url):
    """Run Alembic upgrade to head and optionally backfill legacy Transaction columns."""
    if alembic_command is None:
        raise click.ClickException("Alembic is not installed. Install alembic to run migrations.")
    cfg = _alembic_config(db_url)
    alembic_command.upgrade(cfg, "head")
    click.echo("Alembic upgrade to head completed.")

    if backfill:
        txs = Transaction.query.all()
        updated = 0
        for t in txs:
            try:
                y, m, d = _parse_date_tuple(t.date or "")
                t.date_parsed = datetime.date(y, m, d) if y and m and d else None
            except Exception:
                t.date_parsed = None
            if t.debit_account:
                acc = ensure_account(t.user_id, t.debit_account)
                if acc:
                    t.debit_account_id = acc.id
            if t.credit_account:
                acc = ensure_account(t.user_id, t.credit_account)
                if acc:
                    t.credit_account_id = acc.id
            updated += 1
        db.session.commit()
        click.echo(f"Backfilled {updated} transactions")


@click.command("prune-hints")
@click.option("--min-count", default=2, show_default=True, help="Delete hint tokens with count lower than this threshold")
@click.option("--dry-run", is_flag=True, default=False, help="Analyze only; do not delete")
@with_appcontext
def prune_hints_cli(min_count, dry_run):
    """Prune low-signal AccountSuggestionHint tokens to keep the table lean."""
    q = AccountSuggestionHint.query.filter((AccountSuggestionHint.count == None) | (AccountSuggestionHint.count < int(min_count)))
    to_delete = q.count()
    if dry_run:
        click.echo(f"Would delete {to_delete} hint rows with count < {min_count}")
        return
    q.delete(synchronize_session=False)
    db.session.commit()
    click.echo(f"Deleted {to_delete} hint rows with count < {min_count}")


@click.command("assign-account-ids")
@click.option("--user-id", type=int, default=None, help="Restrict to a specific user id")
@with_appcontext
def assign_account_ids_cli(user_id):
    """Assign debit/credit account FK ids for transactions based on names for all users or a specific user."""
    q = Transaction.query
    if user_id is not None:
        q = q.filter(Transaction.user_id == int(user_id))
    rows = q.all()
    updated = 0
    for t in rows:
        try:
            if t.debit_account and not t.debit_account_id:
                acc = ensure_account(t.user_id, t.debit_account)
                if acc:
                    t.debit_account_id = acc.id
            if t.credit_account and not t.credit_account_id:
                acc = ensure_account(t.user_id, t.credit_account)
                if acc:
                    t.credit_account_id = acc.id
            updated += 1
        except Exception:
            continue
    db.session.commit()
    click.echo(f"Assigned account ids for {updated} transactions")


@click.command("assign-codes")
@click.option("--user-id", type=int, default=None, help="Restrict to a specific user id")
@click.option("--refresh", is_flag=True, default=False, help="Recompute and overwrite existing codes")
@with_appcontext
def assign_codes_cli(user_id, refresh):
    """Assign or refresh account codes across all users or a specific user."""
    if user_id is not None:
        assign_codes_for_user(int(user_id), refresh=bool(refresh))
        click.echo(f"Codes assigned for user {user_id} (refresh={bool(refresh)})")
    else:
        uids = [row[0] for row in db.session.query(Account.user_id).distinct().all()]
        for uid in uids:
            assign_codes_for_user(int(uid), refresh=bool(refresh))
        click.echo(f"Codes assigned for {len(uids)} users (refresh={bool(refresh)})")


@click.command("money-schedule-fill")
@click.argument("start")
@click.argument("end")
@click.option("--user-id", type=int, required=True, help="User id to scope the schedule rows.")
@with_appcontext
def money_schedule_fill_cli(start: str, end: str, user_id: int) -> None:
    """Fill money schedule rows between two dates inclusive with zeroed placeholders."""
    from finance_app.services.money_schedule_service import ensure_row, recompute_from

    start_date = datetime.date.fromisoformat(start)
    end_date = datetime.date.fromisoformat(end)
    if end_date < start_date:
        raise click.BadParameter("end must be on or after start")

    current = start_date
    added = 0
    while current <= end_date:
        ensure_row(current, user_id)
        added += 1
        current += datetime.timedelta(days=1)
    db.session.commit()
    recompute_from(start_date, user_id)
    click.echo(f"Ensured {added} schedule rows between {start_date} and {end_date} for user {user_id}.")
