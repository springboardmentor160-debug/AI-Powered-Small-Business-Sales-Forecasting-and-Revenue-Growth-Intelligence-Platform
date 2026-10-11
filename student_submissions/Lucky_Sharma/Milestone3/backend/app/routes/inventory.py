from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.database import get_db
from app.models.inventory import Inventory
from app.models.user import User

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("")
def list_inventory(
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles(
        "business_owner", "store_manager", "admin"
    )),
):
    rows = db.query(Inventory).order_by(Inventory.stock_level).all()
    return [
        {
            "product_id": x.product_id,
            "product_name": x.product_name,
            "category": x.category,
            "stock_level": x.stock_level,
            "reorder_point": x.reorder_point,
            "warehouse": x.warehouse,
        }
        for x in rows
    ]


@router.get("/alerts")
def inventory_alerts(
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles(
        "business_owner", "store_manager", "admin"
    )),
):
    rows = (
        db.query(Inventory)
        .filter(Inventory.stock_level < Inventory.reorder_point)
        .order_by(Inventory.stock_level)
        .all()
    )

    return [
        {
            "product_id": x.product_id,
            "product_name": x.product_name,
            "stock_level": x.stock_level,
            "reorder_point": x.reorder_point,
            "warehouse": x.warehouse,
        }
        for x in rows
    ]
