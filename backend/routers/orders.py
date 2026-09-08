from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


def _to_order_out(o: models.Order) -> schemas.OrderOut:
    return schemas.OrderOut(
        order_id=o.order_id,
        order_time=o.order_time.strftime("%Y-%m-%d %H:%M:%S") if isinstance(o.order_time, datetime) else str(o.order_time),
        item_id=o.item_id,
        item_name=o.item.item_name if o.item else "N/A",
        category=o.item.category if o.item else "N/A",
        quantity=o.quantity,
        unit_price=o.unit_price,
        total_amount=o.total_amount,
        outlet_id=o.outlet_id,
        patron_id=o.patron_id,
        payment_mode=o.payment_mode
    )


@router.get("/", response_model=List[schemas.OrderOut])
def get_orders(
    outlet_id: Optional[str] = Query(None, description="Filter orders by outlet_id"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(models.Order)
    if outlet_id:
        query = query.filter(models.Order.outlet_id == outlet_id)
    orders = query.order_by(models.Order.order_time.desc()).limit(limit).all()
    return [_to_order_out(o) for o in orders]


@router.post("/", response_model=schemas.OrderOut)
def place_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    item = db.query(models.MenuItem).filter(models.MenuItem.item_id == order_in.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Menu item '{order_in.item_id}' not found")
    if item.stock_units < order_in.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient stock. Available: {item.stock_units}")

    item.stock_units -= order_in.quantity
    total_amt = round(order_in.quantity * item.unit_price, 2)
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow()

    new_order = models.Order(
        order_id=order_id,
        order_time=now,
        item_id=order_in.item_id,
        quantity=order_in.quantity,
        unit_price=item.unit_price,
        total_amount=total_amt,
        outlet_id=order_in.outlet_id,
        patron_id=order_in.patron_id or "WALKIN",
        payment_mode=order_in.payment_mode
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return _to_order_out(new_order)
