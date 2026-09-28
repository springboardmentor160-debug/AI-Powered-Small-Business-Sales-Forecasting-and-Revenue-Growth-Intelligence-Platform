"""JWT authentication, password hashing, and role authorization helpers."""

import base64
import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import get_connection


ROLE_BUSINESS_OWNER = "Business Owner"
ROLE_STORE_MANAGER = "Store Manager"
ROLE_SALES_EXECUTIVE = "Sales Executive"
ROLE_SYSTEM_ADMINISTRATOR = "System Administrator"
ROLES = (
    ROLE_BUSINESS_OWNER,
    ROLE_STORE_MANAGER,
    ROLE_SALES_EXECUTIVE,
    ROLE_SYSTEM_ADMINISTRATOR,
)

JWT_ALGORITHM = "HS256"
JWT_SECRET = os.getenv("MARKETMIND_JWT_SECRET") or secrets.token_urlsafe(32)
ACCESS_TOKEN_MINUTES = 60
PASSWORD_SCRYPT_N = 2**14
PASSWORD_SCRYPT_R = 8
PASSWORD_SCRYPT_P = 1

DEMO_USERS = (
    ("owner@marketmind.local", "Business Owner", "Business Owner", None, "Owner123!"),
    ("manager@marketmind.local", "Store Manager", "Store Manager", "S001", "Manager123!"),
    ("sales@marketmind.local", "Sales Executive", "Sales Executive", "S001", "Sales123!"),
    ("admin@marketmind.local", "System Administrator", "System Administrator", None, "Admin123!"),
)

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Create a salted, memory-hard scrypt password hash."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=PASSWORD_SCRYPT_N,
        r=PASSWORD_SCRYPT_R,
        p=PASSWORD_SCRYPT_P,
    )
    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii")
    encoded_digest = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"scrypt$v1${encoded_salt}${encoded_digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored scrypt hash."""
    try:
        algorithm, version, encoded_salt, encoded_digest = stored_hash.split("$", 3)
        if algorithm != "scrypt" or version != "v1":
            return False
        salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
        expected_digest = base64.urlsafe_b64decode(encoded_digest.encode("ascii"))
        actual_digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=PASSWORD_SCRYPT_N,
            r=PASSWORD_SCRYPT_R,
            p=PASSWORD_SCRYPT_P,
        )
        return hmac.compare_digest(actual_digest, expected_digest)
    except (ValueError, TypeError):
        return False


def ensure_default_users() -> None:
    """Create the four local development users if they do not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN (
                    'Business Owner',
                    'Store Manager',
                    'Sales Executive',
                    'System Administrator'
                )),
                store_id TEXT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        for email, name, role, store_id, password in DEMO_USERS:
            connection.execute(
                """
                INSERT OR IGNORE INTO users
                    (name, email, password_hash, role, store_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email.lower(),
                    hash_password(password),
                    role,
                    store_id,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        connection.commit()


def find_user_by_email(email: str) -> dict[str, Any] | None:
    """Return a user record without exposing its password hash."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT user_id, name, email, password_hash, role, store_id
            FROM users
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()
    return dict(row) if row else None


def find_user_by_id(user_id: int) -> dict[str, Any] | None:
    """Return a current user by database identifier."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT user_id, name, email, role, store_id
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    """Validate credentials and return the matching user."""
    user = find_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    user.pop("password_hash", None)
    return user


def create_access_token(user: dict[str, Any]) -> str:
    """Create a short-lived JWT containing the user's identity and role."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["user_id"]),
        "email": user["email"],
        "role": user["role"],
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    """Decode the bearer JWT and confirm the user still exists."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="A valid bearer token is required.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise unauthorized

    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized from None

    user = find_user_by_id(user_id)
    if not user:
        raise unauthorized
    return user


def require_roles(*allowed_roles: str) -> Callable[..., dict[str, Any]]:
    """Build a FastAPI dependency that authorizes a set of roles."""
    def role_dependency(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your role is not permitted to access this resource.",
            )
        return current_user

    return role_dependency
