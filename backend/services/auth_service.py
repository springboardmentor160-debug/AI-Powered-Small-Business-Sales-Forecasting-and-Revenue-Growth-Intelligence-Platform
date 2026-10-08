import logging
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt
from sqlalchemy.orm import Session

from backend.config import ALGORITHM, SECRET_KEY
from backend.models.user import User
from backend.services.user_service import get_user_by_email

logger = logging.getLogger(__name__)


ALLOWED_ROLES = {
    "business_owner",
    "store_manager",
    "sales_executive",
    "admin",
}


def register_user(
    db: Session,
    user,
) -> dict:
    email = (
        str(user.email)
        .lower()
        .strip()
    )

    if user.role not in ALLOWED_ROLES:
        raise ValueError("Invalid business role.")

    if not user.password.strip():
        raise ValueError("Password cannot be empty.")

    existing_user = get_user_by_email(
        db,
        email,
    )

    if existing_user:
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

    db_user = User(
        username=user.name.strip(),
        email=email,
        hashed_password=hashed_password,
        role=user.role,
        is_active=True,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(
        "Registered user in PostgreSQL: %s",
        email,
    )

    return {
        "message": "User registered successfully!",
        "email": email,
        "role": user.role,
    }


def authenticate_user(
    db: Session,
    credentials,
) -> dict:
    email = (
        str(credentials.email)
        .lower()
        .strip()
    )

    user = get_user_by_email(
        db,
        email,
    )

    if (
        not user
        or not user.is_active
        or not bcrypt.checkpw(
            credentials.password.encode("utf-8"),
            user.hashed_password.encode("utf-8"),
        )
    ):
        raise ValueError(
            "Invalid email or password."
        )

    token = jwt.encode(
        {
            "sub": email,
            "role": user.role,
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
        "role": user.role,
    }