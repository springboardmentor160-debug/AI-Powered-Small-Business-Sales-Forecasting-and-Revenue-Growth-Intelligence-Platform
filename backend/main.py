from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from database import engine, Base
from routers import sales, inventory, analytics

# Create Database tables if not existing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MarketMind AI Backend API",
    description="Small Business Sales Intelligence Platform API",
    version="1.0.0"
)

# CORS configuration to allow local React frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app_name": "MarketMind AI API Engine",
        "version": "1.0.0",
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
