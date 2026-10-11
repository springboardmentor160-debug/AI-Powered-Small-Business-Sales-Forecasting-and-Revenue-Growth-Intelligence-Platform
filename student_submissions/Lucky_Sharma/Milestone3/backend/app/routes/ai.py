import csv
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(tags=["AI"])

# marketmind-ai/data/outputs folder
OUT_DIR = Path(__file__).resolve().parents[3] / "data" / "outputs"


def read_csv(name: str):
    path = OUT_DIR / name
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"{name} not found. Run milestone2_models.py first.",
        )
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@router.get("/segments")
def get_segments(_user: User = Depends(get_current_user)):
    rows = read_csv("segment_summary.csv")
    return [
        {
            "segment": r["segment"],
            "customer_count": int(float(r["customer_count"])),
            "avg_purchase_value": round(float(r["avg_purchase_value"]), 2),
        }
        for r in rows
    ]


def block_sales_executive(user: User):
    if user.role == "sales_executive":
        raise HTTPException(status_code=403, detail="Forecasting is not available for your role")


@router.get("/forecast/revenue")
def get_forecast_revenue(user: User = Depends(get_current_user)):
    block_sales_executive(user)
    r = read_csv("forecast_summary.csv")[0]
    return {
        "period": r["period"],
        "predicted_revenue": round(float(r["predicted_revenue"]), 2),
        "model_used": r["model_used"],
    }


@router.get("/forecast/daily")
def get_forecast_daily(user: User = Depends(get_current_user)):
    block_sales_executive(user)
    return [
        {"date": r["date"], "predicted_revenue": round(float(r["predicted_revenue"]), 2)}
        for r in read_csv("forecast_30days.csv")
    ]