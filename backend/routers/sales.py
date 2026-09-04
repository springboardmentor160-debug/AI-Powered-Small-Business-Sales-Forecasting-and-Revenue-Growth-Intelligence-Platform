from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/v1/sales", tags=["Sales"])

@router.get("/", response_model=List[schemas.TransactionOut])
def get_transactions(
    store_id: Optional[str] = Query(None, description="Filter transactions by store_id"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(models.Transaction)
    if store_id:
        query = query.filter(models.Transaction.store_id == store_id)
    
    transactions = query.order_by(models.Transaction.transaction_date.desc()).limit(limit).all()
    
    result = []
    for tx in transactions:
        result.append(schemas.TransactionOut(
            transaction_id=tx.transaction_id,
            transaction_date=tx.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if isinstance(tx.transaction_date, datetime) else str(tx.transaction_date),
            product_id=tx.product_id,
            product_name=tx.product.product_name if tx.product else "N/A",
            category=tx.product.category if tx.product else "N/A",
            quantity=tx.quantity,
            unit_price=tx.unit_price,
            total_amount=tx.total_amount,
            store_id=tx.store_id,
            customer_id=tx.customer_id,
            payment_method=tx.payment_method
        ))
    return result

@router.post("/", response_model=schemas.TransactionOut)
def record_transaction(
    tx_data: schemas.TransactionCreate,
    db: Session = Depends(get_db)
):
    product = db.query(models.Inventory).filter(models.Inventory.product_id == tx_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID '{tx_data.product_id}' not found")
    
    if product.stock_level < tx_data.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient inventory stock. Available: {product.stock_level}")

    # Deduct stock
    product.stock_level -= tx_data.quantity

    total_amt = round(tx_data.quantity * product.unit_price, 2)
    tx_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow()

    new_tx = models.Transaction(
        transaction_id=tx_id,
        transaction_date=now,
        product_id=tx_data.product_id,
        quantity=tx_data.quantity,
        unit_price=product.unit_price,
        total_amount=total_amt,
        store_id=tx_data.store_id,
        customer_id=tx_data.customer_id if tx_data.customer_id else "GUEST",
        payment_method=tx_data.payment_method
    )

    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    return schemas.TransactionOut(
        transaction_id=new_tx.transaction_id,
        transaction_date=now.strftime("%Y-%m-%d %H:%M:%S"),
        product_id=new_tx.product_id,
        product_name=product.product_name,
        category=product.category,
        quantity=new_tx.quantity,
        unit_price=new_tx.unit_price,
        total_amount=new_tx.total_amount,
        store_id=new_tx.store_id,
        customer_id=new_tx.customer_id,
        payment_method=new_tx.payment_method
    )
