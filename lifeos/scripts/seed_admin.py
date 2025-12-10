"""Seed base roles/permissions and an admin user.

Usage:
    python -m lifeos.scripts.seed_admin --email admin@example.com --password secret123
"""

from __future__ import annotations

import click

from lifeos import create_app
from lifeos.core.auth.models import Permission, Role
from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.extensions import db

BASE_PERMISSIONS = [
    "finance:write",
    "health:write",
    "habits:write",
    "skills:write",
    "projects:write",
    "journal:write",
    "relationships:write",
    "admin",
]


def seed_roles_and_permissions() -> None:
    perm_objs = {}
    for code in BASE_PERMISSIONS:
        perm = Permission.query.filter_by(code=code).first()
        if not perm:
            perm = Permission(code=code, description=f"{code} permission")
            db.session.add(perm)
        perm_objs[code] = perm

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator")
        db.session.add(admin_role)
    admin_role.permissions = list(perm_objs.values())

    db.session.commit()


def seed_admin_user(email: str, password: str, full_name: str | None = None) -> User:
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            full_name=full_name or "Admin",
            password_hash=hash_password(password),
        )
        db.session.add(user)
        db.session.flush()
    # attach admin role
    admin_role = Role.query.filter_by(name="admin").first()
    if admin_role and admin_role not in user.roles:
        user.roles.append(admin_role)
    finance_role = Role.query.filter_by(name="finance:write").first()
    if finance_role and finance_role not in user.roles:
        user.roles.append(finance_role)
    db.session.commit()
    return user


@click.command()
@click.option("--email", required=True, help="Admin email")
@click.option("--password", required=True, help="Admin password")
@click.option("--full-name", default="Admin", help="Admin display name")
def main(email: str, password: str, full_name: str) -> None:
    app = create_app()
    with app.app_context():
        seed_roles_and_permissions()
        user = seed_admin_user(email, password, full_name)
        click.echo(f"Seeded admin user {user.email} with roles {[r.name for r in user.roles]}")


if __name__ == "__main__":
    main()
