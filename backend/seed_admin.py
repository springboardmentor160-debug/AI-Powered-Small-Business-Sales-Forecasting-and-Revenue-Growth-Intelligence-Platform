"""Create the first admin account from environment variables (idempotent).

    ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME (optional)

A brand-new database has no users, so nobody could sign in or open the
Administration page. Run after `python -m backend.init_db`.
"""

import os

import bcrypt
from sqlalchemy import select

from backend.database import SessionLocal
from backend.models.user import User


def seed_admin() -> None:
    email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD") or ""
    name = (os.getenv("ADMIN_NAME") or "Administrator").strip()

    if not email or not password:
        print("ADMIN_EMAIL / ADMIN_PASSWORD not set - skipping admin seed.")
        return

    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email)):
            print(f"Admin {email} already exists - nothing to do.")
            return
        db.add(User(
            username=name,
            email=email,
            hashed_password=bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode(),
            role="admin",
            is_active=True,
        ))
        db.commit()
        print(f"Admin {email} created.")


if __name__ == "__main__":
    seed_admin()
