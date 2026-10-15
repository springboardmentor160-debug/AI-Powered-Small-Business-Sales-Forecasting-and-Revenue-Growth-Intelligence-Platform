"""Create all tables, seed roles and (optionally) the admin account in the SQLite database. Safe to re-run.

    python init_db.py
The admin comes from ADMIN_EMAIL / ADMIN_PASSWORD (see .env.example); it is only created if it does not exist yet.
Existing users, invoices and data are never deleted.
"""
import os

import models
from auth import ROLES, hash_password
from config import DB_PATH
from database import Base, SessionLocal, engine


def init_database(seed_admin: bool = True) -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for r in ROLES:
            if not db.query(models.Role).filter_by(name=r).first():
                db.add(models.Role(name=r))
        db.commit()
        email, pw = os.getenv("ADMIN_EMAIL", "").strip().lower(), os.getenv("ADMIN_PASSWORD", "")
        if seed_admin and email and pw and not db.query(models.User).filter_by(email=email).first():
            admin = db.query(models.Role).filter_by(name="admin").one()
            db.add(models.User(name="Administrator", email=email, hashed_password=hash_password(pw), role_id=admin.id))
            db.commit()
            print(f"Admin created: {email}")


def main():
    init_database()
    print(f"Tables ready in {DB_PATH}")


if __name__ == "__main__":
    main()
