import logging
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from backend.config import ALGORITHM, SECRET_KEY
from backend.services.user_service import fake_users_db

logger = logging.getLogger(__name__)


ALLOWED_ROLES = {
    "business_owner",
    "store_manager",
    "sales_executive",
    "admin",
}


def register_user(user) -> dict:
    email = (
        str(user.email)
        .lower()
        .strip()
    )

    if user.role not in ALLOWED_ROLES:
        raise ValueError("Invalid business role.")

    if not user.password.strip():
        raise ValueError("Password cannot be empty.")

    if email in fake_users_db:
        raise ValueError(
            "This profile is already registered."
        )

    hashed_password = (
        bcrypt.hashpw(
            user.password.encode("utf-8"),
            bcrypt.gensalt(),
        )
        .decode("utf-8")
    )

    fake_users_db[email] = {
        "name": user.name.strip(),
        "role": user.role,
        "hashed_password": hashed_password,
    }

    logger.info(
        "Registered user: %s",
        email,
    )

    return {
        "message": "User registered successfully!",
        "email": email,
        "role": user.role,
    }


def authenticate_user(credentials) -> dict:
    email = (
        str(credentials.email)
        .lower()
        .strip()
    )

    user = fake_users_db.get(email)

    if (
        not user
        or not bcrypt.checkpw(
            credentials.password.encode("utf-8"),
            user["hashed_password"].encode("utf-8"),
        )
    ):
        raise ValueError(
            "Invalid email or password."
        )

    token = jwt.encode(
        {
            "sub": email,
            "role": user["role"],
            "exp": (
                datetime.now(timezone.utc)
                + timedelta(hours=8)
            ),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "access_token": token,
        "role": user["role"],
    }