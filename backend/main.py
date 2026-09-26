from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
import os
from backend.models import User
from backend.dependencies import require_roles
from backend.routers import auth, sales, inventory, analytics, users, segmentation, forecasting

app = FastAPI(
    title="MarketMind AI — Small Business Sales Intelligence Platform",
    description="API for Milestone 1 & Milestone 2 (Days 1–10): Sales, Inventory, Customers, Authentication, RBAC, Customer Segmentation, and Multi-Model Revenue Forecasting.",
    version="1.2.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated reports as static files if directory exists
if not os.path.exists("reports"):
    os.makedirs("reports", exist_ok=True)
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Root health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    return {"message": "MarketMind AI API is running"}


# Direct Wireframe root routes with role protection
@app.get("/segments", tags=["Customer Segmentation"], response_model=List[Dict[str, Any]])
def root_segments(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return segmentation.get_customer_segments_aggregated(current_user=current_user)


@app.get("/forecast/revenue", tags=["Sales Forecasting"], response_model=Dict[str, Any])
def root_forecast_revenue(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return forecasting.get_forecast_revenue(current_user=current_user)


@app.get("/forecast/models", tags=["Sales Forecasting"], response_model=List[Dict[str, Any]])
def root_forecast_models(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return forecasting.get_forecast_models_comparison(current_user=current_user)


# Register API v1 routers
app.include_router(auth.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(segmentation.router)
app.include_router(forecasting.router)
