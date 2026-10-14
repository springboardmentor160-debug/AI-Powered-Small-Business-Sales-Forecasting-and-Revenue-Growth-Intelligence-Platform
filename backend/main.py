import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

from backend.config import CORS_ALLOWED_ORIGINS
from backend.routers.admin import router as admin_router
from backend.routers.anomalies import router as anomalies_router
from backend.routers.auth import router as auth_router
from backend.routers.churn import router as churn_router
from backend.routers.forecast import router as forecast_router
from backend.routers.inventory import router as inventory_router
from backend.routers.invoices import router as invoices_router
from backend.routers.recommendations import router as recommendations_router
from backend.routers.sales import router as sales_router
from backend.routers.segments import router as segments_router
from backend.services.sales_service import calculate_sales_analytics
from backend.data_pipeline.sources.uci.loader import read_uci_transactions


# ============================================================
# 1. SYSTEM CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("MarketMindCore")


# ============================================================
# 2. GLOBAL APPLICATION STATE
# ============================================================

CACHED_ANALYTICS = {
    "total_revenue": 0.0,
    "total_orders": 0,
    "top_product": "N/A",
}


# ============================================================
# 3. STARTUP / LIFESPAN
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
        # Calculate executive sales analytics
        # ----------------------------------------------------

        analytics = calculate_sales_analytics(df)

        CACHED_ANALYTICS.update(
            analytics
        )

        logger.info(
            "UCI analytics loaded successfully."
        )

        logger.info(
            "Total revenue: %.2f",
            CACHED_ANALYTICS["total_revenue"],
        )

        logger.info(
            "Total orders: %s",
            CACHED_ANALYTICS["total_orders"],
        )

        logger.info(
            "Top product: %s",
            CACHED_ANALYTICS["top_product"],
        )

    except Exception as error:

        logger.exception(
            "UCI analytics initialization failed: %s",
            error,
        )

    # --------------------------------------------------------
    # Ensure invoice storage exists
    # --------------------------------------------------------


    yield

    logger.info(
        "MarketMindAI backend shutdown complete."
    )


# ============================================================
# 4. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="MarketMind AI Secure Server",
    version="2.1.0",
    description=(
        "MarketMind AI - Small Business Sales "
        "Intelligence Platform - Milestone 3 API"
    ),
    lifespan=lifespan,
)


# ============================================================
# 4b. GRACEFUL FAILURES (Milestone 4, Day 5-6)
# ============================================================
# Registered BEFORE the CORS middleware, so CORS wraps it and the browser
# can still read the friendly message when something goes wrong.

@app.middleware("http")
async def catch_unexpected_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled error on %s %s", request.method, request.url.path
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": (
                    "Something went wrong on our side. "
                    "Please try again in a moment."
                )
            },
        )


@app.exception_handler(FileNotFoundError)
async def missing_data_handler(request: Request, exc: FileNotFoundError):
    logger.error("Missing data file for %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "The data for this section is temporarily unavailable. "
                "Please try again later."
            )
        },
    )


@app.exception_handler(pd.errors.EmptyDataError)
async def empty_data_handler(request: Request, exc: Exception):
    logger.error("Empty data file for %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "The data for this section is currently empty."},
    )


# ============================================================
# 5. CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 6. API ROUTERS
# ============================================================

app.include_router(
    auth_router
)

app.include_router(
    sales_router
)

app.include_router(
    segments_router
)

app.include_router(
    forecast_router
)

app.include_router(
    invoices_router
)

app.include_router(
    admin_router
)

app.include_router(
    inventory_router
)

app.include_router(
    recommendations_router
)

app.include_router(
    churn_router
)

app.include_router(
    anomalies_router
)


# ============================================================
# 7. SYSTEM ENDPOINTS
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