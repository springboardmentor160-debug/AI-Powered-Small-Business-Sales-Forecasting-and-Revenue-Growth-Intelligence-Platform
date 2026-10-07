from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any
import os
from backend.models import User
from backend.dependencies import require_roles
from backend.routers import auth, sales, inventory, analytics, users, segmentation, forecasting, recommendations, churn, anomalies

app = FastAPI(
    title="MarketMind AI — Small Business Sales Intelligence Platform",
    description="API for Milestone 1, 2, and 3: Sales, Inventory, Customers, Authentication, RBAC, Customer Segmentation, Multi-Model Forecasting, Product Recommendations, Churn Intelligence, and Anomaly Detection.",
    version="1.3.0",
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


# Milestone 3 Direct Root Wireframe Endpoints
@app.get("/recommendations/{customer_id}", tags=["Product Recommendations"], response_model=Dict[str, Any])
def root_recommendations(
    customer_id: str,
    top_n: int = 3,
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return recommendations.get_customer_recommendations_combined(customer_id=customer_id, top_n=top_n, current_user=current_user)


@app.get("/recommendations/{customer_id}/collaborative", tags=["Product Recommendations"], response_model=Dict[str, Any])
def root_recommendations_collaborative(
    customer_id: str,
    top_n: int = 3,
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return recommendations.get_customer_recommendations_collaborative(customer_id=customer_id, top_n=top_n, current_user=current_user)


@app.get("/recommendations/{customer_id}/association", tags=["Product Recommendations"], response_model=Dict[str, Any])
def root_recommendations_association(
    customer_id: str,
    top_n: int = 3,
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return recommendations.get_customer_recommendations_association(customer_id=customer_id, top_n=top_n, current_user=current_user)


@app.get("/churn", tags=["Customer Churn Intelligence"], response_model=Dict[str, Any])
def root_churn(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return churn.get_churn_intelligence_summary(current_user=current_user)


@app.get("/churn/{customer_id}", tags=["Customer Churn Intelligence"], response_model=Dict[str, Any])
def root_churn_customer(
    customer_id: str,
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return churn.get_single_customer_churn_risk(customer_id=customer_id, current_user=current_user)


@app.get("/anomalies", tags=["Anomaly Detection"], response_model=Dict[str, Any])
def root_anomalies(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return anomalies.get_anomalies_full(current_user=current_user)


@app.get("/anomalies/summary", tags=["Anomaly Detection"], response_model=Dict[str, Any])
def root_anomalies_summary(
    current_user: User = Depends(require_roles(["owner", "manager", "admin"]))
):
    return anomalies.get_anomalies_summary(current_user=current_user)


# Register API v1 routers
app.include_router(auth.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(segmentation.router)
app.include_router(forecasting.router)
app.include_router(recommendations.router)
app.include_router(churn.router)
app.include_router(anomalies.router)
