"""Architecture and data-contract invariants."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable, Set, Tuple

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
LIFEOS_ROOT = REPO_ROOT / "lifeos"
EVENT_GAP_ALLOWLIST = set()
BANNED_MIGRATION_OPS = {
    "drop_table",
    "drop_column",
    "drop_index",
    "drop_constraint",
    "alter_column",
    "batch_alter_table",
    "execute",
    "rename_table",
    "rename_column",
}


def _collect_logged_events() -> Set[Tuple[str, str, int]]:
    """Return (event_type, path, lineno) for literal log_event usages."""
    logged: Set[Tuple[str, str, int]] = set()
    for path in LIFEOS_ROOT.rglob("*.py"):
        if "tests" in path.parts:
            continue
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            func = node.func
            is_log_event = (isinstance(func, ast.Name) and func.id == "log_event") or (
                isinstance(func, ast.Attribute) and func.attr == "log_event"
            )
            if not is_log_event:
                continue
            event_arg = node.args[0]
            if isinstance(event_arg, ast.Constant) and isinstance(event_arg.value, str):
                logged.add((event_arg.value, str(path.relative_to(REPO_ROOT)), node.lineno))
    return logged


def _load_catalog_event_types() -> Set[str]:
    """Load event names declared in domain catalogs."""
    catalog_events: Set[str] = set()
    for events_file in LIFEOS_ROOT.glob("domains/*/events.py"):
        namespace: dict = {}
        exec(events_file.read_text(), namespace)  # nosec B102: safe, event modules only declare constants
        catalog = namespace.get("EVENT_CATALOG") or {}
        catalog_events.update(catalog.keys())
    return catalog_events


def test_logged_events_are_catalogued():
    logged_events = _collect_logged_events()
    catalog_events = _load_catalog_event_types()
    missing = {evt for evt, _, _ in logged_events if evt not in catalog_events}
    # Known gaps tracked explicitly; any new gap should fail this test.
    assert missing == EVENT_GAP_ALLOWLIST


def _controllers_importing_models() -> Set[str]:
    violating: Set[str] = set()
    for path in LIFEOS_ROOT.rglob("controllers/*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and ".models." in node.module:
                    violating.add(str(path.relative_to(REPO_ROOT)))
                    break
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if ".models." in alias.name:
                        violating.add(str(path.relative_to(REPO_ROOT)))
                        break
    return violating


def test_controller_model_boundary_is_explicitly_allowlisted():
    violating = _controllers_importing_models()
    allowlisted = {
        "lifeos/domains/finance/controllers/accounting_api.py",
        "lifeos/domains/finance/controllers/journal_api.py",
        "lifeos/domains/finance/controllers/pages.py",
        "lifeos/domains/finance/controllers/receivable_api.py",
        "lifeos/domains/habits/controllers/habit_pages.py",
        "lifeos/domains/health/controllers/health_pages.py",
        "lifeos/domains/projects/controllers/project_api.py",
        "lifeos/domains/projects/controllers/project_pages.py",
        "lifeos/domains/relationships/controllers/rel_api.py",
        "lifeos/domains/relationships/controllers/rel_pages.py",
        "lifeos/domains/skills/controllers/skill_pages.py",
    }
    assert violating.issubset(allowlisted)


def _services_importing_controllers() -> Set[str]:
    violating: Set[str] = set()
    for path in LIFEOS_ROOT.rglob("services/*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and ".controllers." in node.module:
                violating.add(str(path.relative_to(REPO_ROOT)))
                break
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if ".controllers." in alias.name:
                        violating.add(str(path.relative_to(REPO_ROOT)))
                        break
    return violating


def test_services_do_not_depend_on_controllers():
    assert _services_importing_controllers() == set()


def _is_two_phase_migration(path: Path) -> bool:
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TWO_PHASE":
                    if isinstance(node.value, ast.Constant) and node.value.value is True:
                        return True
    return False


def _destructive_ops_in_upgrade(path: Path, banned_ops: Iterable[str]) -> Set[str]:
    tree = ast.parse(path.read_text())
    banned_hits: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    func = inner.func
                    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "op":
                        if func.attr in banned_ops:
                            banned_hits.add(func.attr)
    return banned_hits


def test_migrations_are_additive_by_default():
    migration_roots = [
        REPO_ROOT / "migrations" / "versions",
        REPO_ROOT / "lifeos" / "migrations" / "versions",
    ]
    violations: dict[str, Set[str]] = {}
    for root in migration_roots:
        if not root.exists():
            continue
        for path in root.glob("*.py"):
            if _is_two_phase_migration(path):
                continue
            destructive = _destructive_ops_in_upgrade(path, BANNED_MIGRATION_OPS)
            if destructive:
                violations[str(path.relative_to(REPO_ROOT))] = destructive
    assert violations == {}
