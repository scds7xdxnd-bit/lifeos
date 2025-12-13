"""CSV import service for transactions and journal entries."""
import csv
import datetime
import re
from decimal import ROUND_HALF_UP, Decimal
from typing import Dict, List

from finance_app.extensions import db
from finance_app.lib.dates import _parse_date_tuple
from finance_app.models.accounting_models import Transaction
from finance_app.services.account_service import ensure_account
from finance_app.services.journal_service import JournalBalanceError, JournalLinePayload, create_journal_entry
from finance_app.services.ml_service import record_suggestion_hint


def _norm_key_dict(row: Dict[str, str]) -> Dict[str, str]:
    return {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}


def _get_any(d: Dict[str, str], keys: List[str], default: str = "") -> str:
    for k in keys:
        if k in d and d[k] != "":
            return d[k]
    return default


def _safe_float(s: str) -> float:
    try:
        s2 = re.sub(r"[^0-9.\-]", "", (s or ""))
        return float(s2) if s2 not in ("", ".", "-", "-.", ".-") else 0.0
    except Exception:
        return 0.0


def import_csv_transactions(raw_csv: str, user_id: int) -> Dict[str, object]:
    """Parse CSV rows and create journal entries or legacy transactions."""
    normalized_dates = 0
    unparsable_dates = 0
    count_simple = 0
    count_journal = 0
    skipped_unbalanced: List[str] = []
    skipped_existing: List[str] = []

    lines = raw_csv.splitlines()
    reader = csv.DictReader(lines)
    rows = []
    grouped_rows: Dict[str, List[Dict[str, object]]] = {}
    simple_rows: List[Dict[str, object]] = []

    def _append_group(txn_id, payload):
        if txn_id:
            grouped_rows.setdefault(txn_id, []).append(payload)
        else:
            simple_rows.append(payload)

    try:
        for row in reader:
            rows.append(row)
            drow = _norm_key_dict(row)
            date_raw = _get_any(drow, ["date", "transaction date", "datetime", "timestamp"])
            date_str = date_raw
            date_parsed = None
            parsed_ok = False
            if date_raw:
                try:
                    date_obj = datetime.datetime.strptime(date_raw.replace("-", "/"), "%Y/%m/%d")
                    date_str = date_obj.strftime("%Y/%m/%d")
                    date_parsed = date_obj.date()
                    parsed_ok = True
                except Exception:
                    pass
                if not parsed_ok:
                    y_raw, m_raw, d_raw = _parse_date_tuple(date_raw)
                    try:
                        if y_raw and m_raw and d_raw:
                            date_parsed = datetime.date(y_raw, m_raw, d_raw)
                            date_str = f"{y_raw}/{str(m_raw).zfill(2)}/{str(d_raw).zfill(2)}"
                            parsed_ok = True
                    except Exception:
                        date_parsed = None
            if not parsed_ok and date_parsed is None and date_str:
                y, m, d = _parse_date_tuple(date_str)
                try:
                    if y and m and d:
                        date_parsed = datetime.date(y, m, d)
                        parsed_ok = True
                except Exception:
                    date_parsed = None
            if parsed_ok:
                normalized_dates += 1
            elif date_raw:
                unparsable_dates += 1
            desc = _get_any(drow, ["description", "details", "narration", "memo"])
            debit_account_in = _get_any(drow, ["debit_account", "debit account", "debitacct", "debit"])
            credit_account_in = _get_any(drow, ["credit_account", "credit account", "creditacct", "credit"])
            txn_id = _get_any(drow, ["transaction_id", "transaction id", "txn_id"])
            payload = {
                "date_str": date_str,
                "date_parsed": date_parsed,
                "description": desc,
                "memo": _get_any(drow, ["memo", "note", "notes"]),
                "currency": _get_any(drow, ["currency", "currency_code", "curr"]).upper(),
                "debit_account": debit_account_in,
                "credit_account": credit_account_in,
                "debit_amount": _safe_float(_get_any(drow, ["debit_amount", "debit amount", "debit"])),
                "credit_amount": _safe_float(_get_any(drow, ["credit_amount", "credit amount", "credit"])),
            }
            _append_group(txn_id, payload)

        for txn_id, items in grouped_rows.items():
            if not items:
                continue
            ref = f"CSV:{txn_id}" if txn_id else None
            if ref:
                from finance_app.models.accounting_models import JournalEntry

                existing = JournalEntry.query.filter_by(user_id=user_id, reference=ref[:120]).first()
                if existing:
                    skipped_existing.append(txn_id)
                    continue
            first_with_date = next((it for it in items if it.get("date_str")), None)
            date_str = first_with_date.get("date_str") if first_with_date else ""
            date_parsed = first_with_date.get("date_parsed") if first_with_date else None
            description = next((it.get("description") for it in items if it.get("description")), "")
            line_payloads: List[JournalLinePayload] = []
            line_no = 1
            for item in items:
                currency_code = (item.get("currency") or "").upper() or None
                memo = item.get("memo") or ""
                if item.get("debit_account") and item.get("debit_amount", 0.0) > 0:
                    amt = Decimal(str(item["debit_amount"] or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    if amt > 0:
                        acc = ensure_account(user_id, item["debit_account"])
                        line_payloads.append(
                            JournalLinePayload(
                                dc="D",
                                account_id=acc.id,
                                amount=amt,
                                currency_code=currency_code,
                                memo=memo,
                                line_no=line_no,
                            )
                        )
                        line_no += 1
                if item.get("credit_account") and item.get("credit_amount", 0.0) > 0:
                    amt = Decimal(str(item["credit_amount"] or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    if amt > 0:
                        acc = ensure_account(user_id, item["credit_account"])
                        line_payloads.append(
                            JournalLinePayload(
                                dc="C",
                                account_id=acc.id,
                                amount=amt,
                                currency_code=currency_code,
                                memo=memo,
                                line_no=line_no,
                            )
                        )
                        line_no += 1
            try:
                create_journal_entry(
                    user_id=user_id,
                    date=date_str,
                    date_parsed=date_parsed,
                    description=description or (txn_id if isinstance(txn_id, str) else ""),
                    reference=ref[:120] if ref else None,
                    lines=line_payloads,
                )
            except JournalBalanceError:
                skipped_unbalanced.append(txn_id)
                db.session.rollback()
                continue
            count_journal += 1

        for item in simple_rows:
            debit_account_in = item.get("debit_account")
            credit_account_in = item.get("credit_account")
            debit_acc_obj = ensure_account(user_id, debit_account_in) if debit_account_in else None
            credit_acc_obj = ensure_account(user_id, credit_account_in) if credit_account_in else None
            debit_account = debit_acc_obj.name if debit_acc_obj else debit_account_in
            credit_account = credit_acc_obj.name if credit_acc_obj else credit_account_in
            tx = Transaction(
                date=item.get("date_str"),
                description=item.get("description"),
                debit_account=debit_account,
                debit_amount=item.get("debit_amount", 0.0),
                credit_account=credit_account,
                credit_amount=item.get("credit_amount", 0.0),
                user_id=user_id,
                debit_account_id=debit_acc_obj.id if debit_acc_obj else None,
                credit_account_id=credit_acc_obj.id if credit_acc_obj else None,
                date_parsed=item.get("date_parsed"),
            )
            db.session.add(tx)
            count_simple += 1

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    # Feed adaptive hints from CSV contents
    try:
        for row in rows:
            desc = row.get("description", "") or ""
            da = row.get("debit_account", "") or ""
            ca = row.get("credit_account", "") or ""
            if da:
                record_suggestion_hint(user_id, "debit", desc, da)
            if ca:
                record_suggestion_hint(user_id, "credit", desc, ca)
    except Exception:
        pass

    return {
        "count_simple": count_simple,
        "count_journal": count_journal,
        "normalized_dates": normalized_dates,
        "unparsable_dates": unparsable_dates,
        "skipped_unbalanced": skipped_unbalanced,
        "skipped_existing": skipped_existing,
    }
