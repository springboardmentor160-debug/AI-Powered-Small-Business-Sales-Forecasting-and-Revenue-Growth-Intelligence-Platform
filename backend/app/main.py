from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.auth import database_models
from app.api.dashboard import router as dashboard_router
from app.auth.routes import router as auth_router


from app.auth import database_models

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "MarketMind AI API is running"}


app.include_router(dashboard_router)
app.include_router(auth_router)