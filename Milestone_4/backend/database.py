"""
Database Connection & Session Engine for MarketMind AI (Milestone 4)
Supports both local persistence and Vercel serverless /tmp execution.
"""

import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Determine if running in a serverless or read-only cloud environment
is_serverless = bool(
    os.environ.get("VERCEL")
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    or os.environ.get("VERCEL_ENV")
    or not os.access(BASE_DIR, os.W_OK)
)

import tempfile

if is_serverless:
    # On AWS Lambda / Vercel Serverless, the root filesystem is strictly read-only.
    # The database file MUST be in /tmp (or system temp) so SQLite can read, write, lock, and create tables.
    tmp_dir = "/tmp" if os.path.exists("/tmp") else tempfile.gettempdir()
    os.makedirs(tmp_dir, exist_ok=True)
    DB_PATH = os.path.join(tmp_dir, "marketmind.db")
    
    # Candidate source database locations across Vercel build output structures
    candidate_sources = [
        os.path.join(BASE_DIR, "marketmind.db"),
        os.path.join(BASE_DIR, "marketmind_default.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "marketmind.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "marketmind_default.db"),
        "/var/task/marketmind.db",
        "/var/task/marketmind_default.db",
        "/var/task/Milestone_4/marketmind.db",
        "/var/task/Milestone_4/marketmind_default.db",
    ]
    
    # If /tmp/marketmind.db does not exist or is empty (< 1024 bytes), attempt copy from pre-seeded files
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) < 1024:
        copied = False
        for src in candidate_sources:
            if os.path.exists(src) and os.path.isfile(src) and os.path.getsize(src) > 1024:
                try:
                    shutil.copyfile(src, DB_PATH)
                    print(f"[Database] Successfully copied pre-seeded database from '{src}' to '{DB_PATH}' ({os.path.getsize(DB_PATH):,} bytes).")
                    copied = True
                    break
                except Exception as e:
                    print(f"[Database Warning] Failed to copy from '{src}': {e}")
        if not copied:
            print("[Database Warning] No pre-seeded database bundle found; will initialize new schema in /tmp/marketmind.db.")
else:
    DB_PATH = os.path.join(BASE_DIR, "marketmind.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_db_initialized = False

def ensure_db_initialized():
    """Ensure database tables exist and demo users are seeded with correct passwords."""
    global _db_initialized
    if _db_initialized:
        return
    try:
        from .db_service import init_db_tables, seed_demo_users, populate_milestone3_results
        init_db_tables()
        db = SessionLocal()
        seed_demo_users(db)
        
        outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
        populate_milestone3_results(db, outputs_dir)
        db.close()
        _db_initialized = True
    except Exception as e:
        print(f"[Database Warning] ensure_db_initialized encountered an issue: {e}")

def get_db():
    ensure_db_initialized()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


