from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from database import engine, Base
from routers import sales, inventory, analytics, auth, users, segments, forecast, reports

# Create Database tables if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MarketMind AI Backend API",
    description="Small Business Sales Intelligence Platform API",
    version="1.0.0"
)

# Startup event to ensure ML artifacts are precomputed
@app.on_event("startup")
def verify_ml_artifacts():
    try:
        from ml.train import artifacts_exist, train_all_artifacts
    except ImportError:
        from backend.ml.train import artifacts_exist, train_all_artifacts
    if not artifacts_exist():
        print("[Startup] Missing ML artifacts. Initializing automated ML pipeline...")
        train_all_artifacts()
    else:
        print("[Startup] All ML model artifacts and business reports are verified online.")

# CORS configuration to allow local frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers (Milestone 1)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(analytics.router)

# Register API Routers (Milestone 2)
app.include_router(segments.router)
app.include_router(forecast.router)
app.include_router(reports.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app_name": "MarketMind AI API Engine",
        "version": "1.0.0",
        "auth": "JWT-enabled",
        "documentation": "/docs"
    }

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "environment": "development"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
