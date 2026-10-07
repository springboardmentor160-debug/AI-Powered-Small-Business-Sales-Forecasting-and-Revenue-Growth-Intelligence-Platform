from pathlib import Path


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
# INVOICE REGISTRY
# ============================================================

INVOICE_DATA_DIR = (
    BACKEND_DIR
    / "data"
)

INVOICE_FILE = (
    INVOICE_DATA_DIR
    / "invoices.json"
)


# ============================================================
# AUTHENTICATION
# ============================================================

SECRET_KEY = "super-secret-key-for-internship"

ALGORITHM = "HS256"