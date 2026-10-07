import json
import logging
import threading
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import bcrypt
import pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field
from backend.routers.sales import router as sales_router
from backend.schemas.auth import UserRegister, UserLogin
from backend.services.invoice_service import save_invoice_records
from backend.schemas.invoice import InvoiceCreate
from backend.routers.segments import router as segments_router
from backend.routers.forecast import router as forecast_router
from backend.routers.invoices import router as invoices_router
from backend.routers.auth import router as auth_router
from backend.data_pipeline.sources.uci.loader import read_uci_transactions
from backend.routers.inventory import router as inventory_router
from backend.routers.admin import router as admin_router
from backend.services.sales_service import calculate_sales_analytics
from backend.services.sales_service import (
    prepare_sales_data,
    calculate_sales_analytics,
)
from backend.config import (
    ALGORITHM,
    SECRET_KEY,
    UCI_RAW_DIR,
    UCI_FILE_1,
    UCI_FILE_2,
    UCI_ARTIFACT_DIR,
    M5_ARTIFACT_DIR,
    SEGMENTATION_ARTIFACT_DIR,
    INVOICE_DATA_DIR,
    INVOICE_FILE,
)
#============================================================
# 1. SYSTEM CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("MarketMindCore")

# ============================================================
# 2. PROJECT PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

# ------------------------------------------------------------
# UCI RAW DATA
# ------------------------------------------------------------

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

# ------------------------------------------------------------
# UCI M2 FORECASTING ARTIFACTS
# ------------------------------------------------------------

UCI_ARTIFACT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

# ------------------------------------------------------------
# SEGMENTATION ARTIFACTS
# ------------------------------------------------------------

SEGMENTATION_ARTIFACT_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "milestone-2"
    / "segmentation"
)

# ------------------------------------------------------------
# M5 FORECASTING ARTIFACTS
# ------------------------------------------------------------

M5_ARTIFACT_DIR = (
    BACKEND_DIR
    / "artifacts"
    / "milestone-2"
    / "forecasting"
)

# ------------------------------------------------------------
# INVOICE REGISTRY
# ------------------------------------------------------------

INVOICE_DATA_DIR = (
    BACKEND_DIR
    / "data"
)

INVOICE_FILE = (
    INVOICE_DATA_DIR
    / "invoices.json"
)

INVOICE_LOCK = threading.Lock()


# ============================================================
# 3. GLOBAL APPLICATION STATE
# ============================================================

from backend.services.user_service import fake_users_db

CACHED_ANALYTICS = {
    "total_revenue": 0.0,
    "total_orders": 0,
    "top_product": "N/A",
}

# ============================================================
# 5. STARTUP DATA PIPELINE
# ============================================================

@asynccontextmanager
async def lifespan(
    _: FastAPI,
) -> AsyncIterator[None]:

    logger.info(
        "Initializing MarketMindAI analytics pipeline..."
    )

    try:

        df = read_uci_transactions()

        # ----------------------------------------------------
        # Standardize source column names
        # ----------------------------------------------------

        rename_map = {}

        if "InvoiceNo" in df.columns:
            rename_map["InvoiceNo"] = "Invoice"

        if "UnitPrice" in df.columns:
            rename_map["UnitPrice"] = "Price"

        if rename_map:
            df = df.rename(
                columns=rename_map
            )

        # ----------------------------------------------------
        # Validate source schema
        # ----------------------------------------------------

            # ----------------------------------------------------
            # Calculate executive sales analytics
            # ----------------------------------------------------

            analytics = calculate_sales_analytics(df)

            CACHED_ANALYTICS.update(
                analytics
            )
            app.state.sales_analytics = CACHED_ANALYTICS.copy()

            logger.info(
                "UCI analytics loaded successfully."
            )

            logger.info(
                "Total revenue: %.2f",
                CACHED_ANALYTICS[
                    "total_revenue"
                ],
            )

            logger.info(
                "Total orders: %s",
                CACHED_ANALYTICS[
                    "total_orders"
                ],
            )

            logger.info(
                "Top product: %s",
                CACHED_ANALYTICS[
                    "top_product"
                ],
            )

    except Exception as error:

        logger.exception(
            "UCI analytics initialization failed: %s",
            error,
        )

    # --------------------------------------------------------
    # Ensure invoice storage exists
    # --------------------------------------------------------

    INVOICE_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not INVOICE_FILE.exists():

        save_invoice_records([])

    yield

    logger.info(
        "MarketMindAI backend shutdown complete."
    )


# ============================================================
# 6. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="MarketMind AI Secure Server",
    version="2.1.0",
    description=(
        "MarketMind AI - Small Business Sales "
        "Intelligence Platform - Milestone 2 API"
    ),
    lifespan=lifespan,
)


# ============================================================
# 7. CORS
# ============================================================

app.include_router(sales_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(segments_router)
app.include_router(forecast_router)
app.include_router(invoices_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(inventory_router)

# ============================================================
# 9. SECURITY / RBAC
# ============================================================

def get_current_user(
    authorization: str = Header(...),
) -> dict:

    if not authorization.startswith(
        "Bearer "
    ):

        raise HTTPException(
            status_code=401,
            detail=(
                "Malformed Authorization header. "
                "Expected Bearer token."
            ),
        )

    token = (
        authorization[7:]
        .strip()
    )

    if not token:

        raise HTTPException(
            status_code=401,
            detail="Missing bearer token.",
        )

    try:

        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[
                ALGORITHM
            ],
        )

    except JWTError as error:

        logger.warning(
            "JWT validation failed: %s",
            error,
        )

        raise HTTPException(
            status_code=401,
            detail=(
                "Expired or invalid "
                "authentication token."
            ),
        ) from error


def require_role(
    allowed_roles: list[str],
):

    def role_checker(
        user: dict = Depends(
            get_current_user
        ),
    ):

        if user.get("role") not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Access denied. "
                    "Required role(s): "
                    + ", ".join(
                        allowed_roles
                    )
                ),
            )

        return user

    return role_checker


# ============================================================
# 10. SYSTEM HEALTH
# ============================================================

@app.get("/")
def root():

    return {
        "application": "MarketMind AI",
        "version": "2.1.0",
        "status": "online",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "MarketMind AI backend",
        "version": "2.1.0",
    }