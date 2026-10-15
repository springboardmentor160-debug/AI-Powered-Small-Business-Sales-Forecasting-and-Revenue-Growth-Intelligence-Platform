"""SQLAlchemy engine/session for the SQLite database (no server, no Docker, no PostgreSQL)."""
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DATA_DIR, DB_PATH

DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# URL.create handles Windows paths (C:\...) correctly.
DATABASE_URL = URL.create("sqlite", database=str(DB_PATH))
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},   # FastAPI serves requests from a thread pool
)


@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_conn, _record):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")      # SQLite ignores foreign keys unless asked
    cur.execute("PRAGMA journal_mode=WAL")     # readers do not block the writer
    cur.execute("PRAGMA synchronous=NORMAL")
    cur.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
