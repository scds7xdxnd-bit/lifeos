# Admin Password Reset (Ops Runbook)

Purpose: unblock a specific user when credentials are unknown or mismatched. This is a back-office procedure; no UI changes.

## Check whether the password matches
```bash
export FLASK_APP=lifeos
flask check-user-password --email="user@example.com" --password="plain-text-here"
# Output: user_id=<id> email=<normalized> password_valid=<True|False>
```

## Reset the password via Flask shell
```bash
export FLASK_APP=lifeos
flask shell
```
Then run:
```python
from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.extensions import db

u = User.query.filter_by(email="user@example.com").first()
u.password_hash = hash_password("NewStrongPass123!")
db.session.commit()
print("updated", u.id, u.email)
```

## Login afterward
- Use the exact email casing stored (`user@example.com` → lowercased by default).
- Login endpoints are stateless; clear stale cookies if needed (already handled server-side).

## If sessions are still problematic
- Run the admin session reset CLI:
```bash
export FLASK_APP=lifeos
flask admin-reset-sessions --email="user@example.com" --reason="ops password reset"
```
- This revokes refresh tokens and emits `auth.session.admin_reset`.
