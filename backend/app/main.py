"""FastAPI entry point for the initial MarketMind backend."""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import ensure_default_users
from .database import initialize_database
from .routes import reporting_router, router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize the SQLite data store when the application starts."""
    initialize_database()
    ensure_default_users()
    yield


app = FastAPI(
    title="MarketMind AI API",
    description="Initial sales, inventory, and customer summaries.",
    version="0.1.0",
    lifespan=lifespan,
)
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "MARKETMIND_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router)
app.include_router(reporting_router)


@app.get("/")
def root() -> dict[str, str]:
    """Return basic API information."""
    return {"name": "MarketMind AI API", "status": "running"}


@app.get("/health")
def health() -> dict[str, str]:
    """Return the service health status."""
    return {"status": "healthy"}
