from fastapi import FastAPI

app = FastAPI(title="MarketMind AI")

@app.get("/")
def home():
    return {"message": "Your backend is officially alive!"}
