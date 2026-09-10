from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, SessionLocal, engine
from app.models import *  # noqa
from app.routes import auth, customers, dashboard, inventory, invoices, sales, users
from app.utils.seed import seed_database

app = FastAPI(
    title="MarketMind AI API",
    description="AI-Powered Small Business Sales Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    seed_database(db)
finally:
    db.close()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(dashboard.router)
app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(customers.router)
app.include_router(invoices.router)


@app.get("/")
def root():
    return {
        "message": "MarketMind AI backend is running",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
