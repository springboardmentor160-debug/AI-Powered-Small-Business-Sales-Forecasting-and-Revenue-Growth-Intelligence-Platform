"""
Database Connection & Session Management for Milestone 2 (MarketMind AI)
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "marketmind_db")

# Allow full DATABASE_URL override from environment
CUSTOM_DB_URL = os.getenv("DATABASE_URL")

if CUSTOM_DB_URL:
    PRIMARY_DB_URL = CUSTOM_DB_URL
else:
    PRIMARY_DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

FALLBACK_DB_URL = "sqlite:///./marketmind.db"

Base = declarative_base()
engine = None

def get_engine():
    global engine
    if engine is not None:
        return engine

    # Attempt PostgreSQL connection
    try:
        pg_engine = create_engine(PRIMARY_DB_URL, pool_pre_ping=True)
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[Database] Connected successfully to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
        engine = pg_engine
        return engine
    except Exception as e:
        print(f"[Database] PostgreSQL connection failed ({e}). Falling back to SQLite persistence engine.")
        sqlite_engine = create_engine(
            FALLBACK_DB_URL,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True
        )
        engine = sqlite_engine
        return engine

db_engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
