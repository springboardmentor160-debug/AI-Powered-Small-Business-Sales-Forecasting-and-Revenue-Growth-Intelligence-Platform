"""FastAPI entry point for the initial MarketMind backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import ensure_default_users
from .database import initialize_database
from .routes import router


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    """Return basic API information."""
    return {"name": "MarketMind AI API", "status": "running"}


@app.get("/health")
def health() -> dict[str, str]:
    """Return the service health status."""
    return {"status": "healthy"}
