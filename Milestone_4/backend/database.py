"""
Database Connection & Session Engine for MarketMind AI (Milestone 4)
Supports both local persistence and Vercel serverless /tmp execution.
"""

import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE_DB_PATH = os.path.join(BASE_DIR, "marketmind.db")

# In Vercel Serverless / AWS Lambda environment, the deployment root is read-only.
# We copy the seeded database to /tmp so all writes, updates, resets, and uploads work seamlessly.
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    TMP_DB_PATH = "/tmp/marketmind.db"
    if not os.path.exists(TMP_DB_PATH) and os.path.exists(SOURCE_DB_PATH):
        try:
            shutil.copyfile(SOURCE_DB_PATH, TMP_DB_PATH)
            print("[Database] Copied initial database to /tmp/marketmind.db for Vercel execution.")
        except Exception as e:
            print(f"[Database Warning] Failed to copy db to /tmp: {e}")
    DB_PATH = TMP_DB_PATH if os.path.exists(TMP_DB_PATH) else SOURCE_DB_PATH
else:
    DB_PATH = SOURCE_DB_PATH

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

