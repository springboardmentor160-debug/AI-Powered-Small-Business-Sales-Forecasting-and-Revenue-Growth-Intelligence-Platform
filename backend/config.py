"""Central configuration: paths, .env loading and the SQLite database URL.

Everything is derived from this file's location, so the project works no matter which directory you start it from.
"""
import os
import warnings
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"                      # SQLite file lives here (stable, absolute location)
DEFAULT_DB_PATH = DATA_DIR / "marketmind.db"
PROCESSED_DIR = PROJECT_ROOT / "datasets" / "processed"
ML_OUTPUTS = PROJECT_ROOT / "ml" / "outputs"

# backend/.env wins over a project-root .env; real environment variables win over both.
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(PROJECT_ROOT / ".env")


def resolve_database_path() -> Path:
    """Return the absolute path of the SQLite file.

    * DATABASE_URL unset                  -> <project>/data/marketmind.db
    * DATABASE_URL=sqlite:///relative.db  -> resolved relative to the project root
    * DATABASE_URL=sqlite:///C:/abs/x.db  -> used as given
    * anything that is not SQLite (e.g. an old PostgreSQL URL) is ignored with a warning.
    """
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        return DEFAULT_DB_PATH
    if not url.startswith("sqlite"):
        warnings.warn(f"DATABASE_URL is not a SQLite URL ({url.split(':', 1)[0]}); ignoring it and using {DEFAULT_DB_PATH}")
        return DEFAULT_DB_PATH
    raw = url.split("sqlite:///", 1)[-1] if "sqlite:///" in url else ""
    if not raw or raw == ":memory:":
        return DEFAULT_DB_PATH
    p = Path(raw)
    return p if p.is_absolute() else (PROJECT_ROOT / p).resolve()


DB_PATH = resolve_database_path()

DEFAULT_SECRET = "dev-only-secret-change-me"
SECRET_KEY = os.getenv("SECRET_KEY", "").strip() or DEFAULT_SECRET
if SECRET_KEY == DEFAULT_SECRET or SECRET_KEY.startswith("change-this"):
    warnings.warn("SECRET_KEY is a placeholder - fine for local development, set a long random value before deploying.")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "8"))
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]


# ---- password-reset e-mail (SMTP). Leave SMTP_HOST empty to run in dev mode: the e-mail is printed in the console + saved in data/outbox/.
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587") or 587)
SMTP_USER = os.getenv("SMTP_USER", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "").strip() or SMTP_USER
SMTP_SECURITY = os.getenv("SMTP_SECURITY", "starttls").strip().lower()      # starttls (port 587) | ssl (port 465) | none
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").strip().rstrip("/")   # base URL put in the reset link
RESET_TOKEN_MINUTES = int(os.getenv("RESET_TOKEN_MINUTES", "30") or 30)
OUTBOX_DIR = DATA_DIR / "outbox"

# ---- sign-up of administrators from the login page needs this code (empty = admin sign-up disabled)
ADMIN_REGISTRATION_CODE = os.getenv("ADMIN_REGISTRATION_CODE", "").strip()

# ---- the sample data ends on a fixed historical day; 1 = show every date moved forward so the newest record is today
REBASE_DATES_TO_TODAY = os.getenv("REBASE_DATES_TO_TODAY", "1").strip().lower() not in ("0", "false", "no", "off", "")
