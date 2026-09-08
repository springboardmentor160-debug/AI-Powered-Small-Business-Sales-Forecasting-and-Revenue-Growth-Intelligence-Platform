from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import auth, staff, menu, orders, insights

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MarketMind API",
    description="Restaurant Chain Revenue & Stock Intelligence Platform API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(staff.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(insights.router)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "app_name": "MarketMind API Engine",
        "version": "1.0.0",
        "auth": "JWT-enabled",
        "documentation": "/docs"
    }


@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "database": "connected", "environment": "development"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
