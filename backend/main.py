from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, sales, inventory, analytics, users

app = FastAPI(
    title="MarketMind AI — Small Business Sales Intelligence Platform",
    description="API for Milestone 1: Sales, Inventory, Customers, Authentication, and RBAC.",
    version="1.0.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
