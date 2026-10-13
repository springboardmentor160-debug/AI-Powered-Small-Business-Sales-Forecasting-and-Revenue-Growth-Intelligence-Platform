import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKEND_DIR = PROJECT_ROOT / "backend"


# ============================================================
# UCI DATA
# ============================================================

UCI_RAW_DIR = (
    BACKEND_DIR
    / "data"
    / "raw"
    / "uci"
)

UCI_FILE_1 = (
    UCI_RAW_DIR
    / "online_retail_v1.csv"
)

UCI_FILE_2 = (
    UCI_RAW_DIR
    / "online_retail_v2.csv"
)


# ============================================================
# M2 FORECASTING ARTIFACTS
# ============================================================

UCI_ARTIFACT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)


M5_ARTIFACT_DIR = (
    BACKEND_DIR
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)


# ============================================================
# SEGMENTATION ARTIFACTS
# ============================================================

SEGMENTATION_ARTIFACT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
)





# ============================================================
# AUTHENTICATION
# ============================================================

# The signing key must come from the environment (.env), never from
# source control. If it is missing, a random per-process key is used so
# the app stays secure, but issued tokens stop working on restart.
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(48)
    logger.warning(
        "SECRET_KEY is not set; using a temporary random key. "
        "Set SECRET_KEY in .env for stable sessions."
    )

# Comma-separated list of browser origins allowed to call the API.
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:8501,http://127.0.0.1:8501",
    ).split(",")
    if origin.strip()
]

ALGORITHM = "HS256"
