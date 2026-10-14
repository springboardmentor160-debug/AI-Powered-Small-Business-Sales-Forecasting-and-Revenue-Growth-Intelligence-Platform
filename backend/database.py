"""
Database Connection & Session Engine for MarketMind AI (Milestone 4)
Supports both local persistence and Vercel serverless /tmp execution.
"""

import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Check if running in Vercel serverless environment
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("VERCEL_ENV"):
    TMP_DB = "/tmp/marketmind.db"
    try:
        os.makedirs(os.path.dirname(TMP_DB), exist_ok=True)
    except Exception:
        pass
    SOURCE_DB = os.path.join(BASE_DIR, "marketmind.db")
    if not os.path.exists(SOURCE_DB):
        SOURCE_DB = os.path.join(BASE_DIR, "marketmind_default.db")
    if not os.path.exists(SOURCE_DB):
        SOURCE_DB = os.path.join(BASE_DIR, "Milestone_4", "marketmind.db")

    # Copy the seed database into /tmp so SQLite can read and write freely
    if not os.path.exists(TMP_DB) and os.path.exists(SOURCE_DB):
        try:
            shutil.copyfile(SOURCE_DB, TMP_DB)
        except Exception as e:
            print(f"[DB Warning] Failed to copy seed DB: {e}")

    DB_PATH = TMP_DB
else:
    DB_PATH = os.path.join(BASE_DIR, "marketmind.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"
SQLALCHEMY_DATABASE_URL = DATABASE_URL

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_db_initialized = False

def ensure_db_initialized():
    """Ensure database tables exist and demo users are seeded with correct passwords."""
    global _db_initialized
    if _db_initialized:
        return
    _db_initialized = True
    try:
        from .db_service import init_db_tables, seed_demo_users
        init_db_tables()
        db = SessionLocal()
        seed_demo_users(db)
        db.close()
    except Exception as e:
        print(f"[Database Warning] ensure_db_initialized safe catch: {e}")

def get_db():
    ensure_db_initialized()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
