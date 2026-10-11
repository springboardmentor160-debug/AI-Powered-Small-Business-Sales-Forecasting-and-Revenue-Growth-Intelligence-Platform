import io
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.database import get_db
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.models.user import User

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("")
def list_sales(
    limit: int = 50,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles(
        "business_owner", "store_manager", "sales_executive", "admin"
    )),
):
    rows = db.query(Sale).order_by(Sale.order_date.desc()).limit(limit).all()
    return [
        {
            "order_id": x.order_id,
            "order_date": x.order_date.isoformat(),
            "product_name": x.product_name,
            "customer_id": x.customer_id,
            "quantity": x.quantity,
            "unit_price": x.unit_price,
            "revenue": x.revenue,
        }
        for x in rows
    ]


@router.post("/upload")
async def upload_sales_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("business_owner", "store_manager", "admin")),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    content = await file.read()

    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {exc}")

    required = {
        "order_id", "order_date", "product_id", "product_name",
        "customer_id", "quantity", "unit_price"
    }

    missing = required - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing columns: {sorted(missing)}"
        )

    inserted = 0

    for _, row in df.iterrows():
        if pd.isna(row["customer_id"]) or pd.isna(row["quantity"]):
            continue

        order_id = str(row["order_id"])
        if db.query(Sale).filter(Sale.order_id == order_id).first():
            continue

        customer_id = str(row["customer_id"])
        product_id = str(row["product_id"])

        if not db.query(Customer).filter(Customer.customer_id == customer_id).first():
            continue

        if not db.query(Product).filter(Product.product_id == product_id).first():
            continue

        try:
            order_date = pd.to_datetime(row["order_date"]).date()
            quantity = float(row["quantity"])
            unit_price = float(row["unit_price"])
        except Exception:
            continue

        if quantity <= 0 or unit_price <= 0:
            continue

        sale = Sale(
            order_id=order_id,
            order_date=order_date,
            product_id=product_id,
            product_name=str(row["product_name"]),
            customer_id=customer_id,
            quantity=quantity,
            unit_price=unit_price,
            revenue=quantity * unit_price,
        )
        db.add(sale)
        inserted += 1

    db.commit()

    return {
        "message": "Sales CSV processed",
        "inserted": inserted,
        "skipped": len(df) - inserted,
    }
