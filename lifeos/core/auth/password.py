"""Password hashing helpers."""

from lifeos.extensions import bcrypt


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.generate_password_hash(plain_password).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Validate a plaintext password against a stored hash."""
    return bcrypt.check_password_hash(hashed_password, plain_password)
