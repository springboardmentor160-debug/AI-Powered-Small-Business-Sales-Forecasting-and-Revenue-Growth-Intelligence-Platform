from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from backend.routers import auth, sales, inventory, analytics, users, segmentation, forecasting

app = FastAPI(
    title="MarketMind AI — Small Business Sales Intelligence Platform",
    description="API for Milestone 1 & Milestone 2 (Days 1–6): Sales, Inventory, Customers, Authentication, RBAC, Customer Segmentation, and Sales Forecasting.",
    version="1.1.0",
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
if os.path.exists("reports"):
    app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Root health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    return {"message": "MarketMind AI API is running"}


# Register API v1 routers
app.include_router(auth.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(segmentation.router)
app.include_router(forecasting.router)

