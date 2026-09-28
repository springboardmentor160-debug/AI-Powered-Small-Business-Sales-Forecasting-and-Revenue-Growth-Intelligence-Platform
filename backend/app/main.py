"""FastAPI entry point for the initial MarketMind backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import initialize_database
from .routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize the SQLite data store when the application starts."""
    initialize_database()
    yield


app = FastAPI(
    title="MarketMind AI API",
    description="Initial sales, inventory, and customer summaries.",
    version="0.1.0",
    lifespan=lifespan,
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
