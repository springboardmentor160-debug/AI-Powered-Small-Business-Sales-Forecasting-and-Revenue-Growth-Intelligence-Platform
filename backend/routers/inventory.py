from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Inventory, Product, User
from backend.schemas import InventoryItemResponse
from backend.dependencies import require_roles

router = APIRouter(prefix="/api/v1/inventory", tags=["Inventory"])


@router.get("", response_model=List[InventoryItemResponse])
def get_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["owner", "manager", "admin", "sales_executive"])),
):
    """Retrieve full inventory list with current stock levels and reorder thresholds."""
    items = db.query(Inventory).join(Product, Inventory.product_id == Product.id).all()
    results = []
    for item in items:
        results.append(
            InventoryItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                category=item.product.category,
                unit_price=item.product.unit_price,
                stock_level=item.stock_level,
                reorder_point=item.reorder_point,
                is_low_stock=item.is_low_stock,
            )
        )
    return results


@router.get("/alerts", response_model=List[InventoryItemResponse])
def get_inventory_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["owner", "manager", "admin", "sales_executive"])),
):
    """Retrieve low-stock inventory items where stock_level < reorder_point."""
    items = (
        db.query(Inventory)
        .join(Product, Inventory.product_id == Product.id)
        .filter(Inventory.stock_level < Inventory.reorder_point)
        .all()
    )
    results = []
    for item in items:
        results.append(
            InventoryItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,
                category=item.product.category,
                unit_price=item.product.unit_price,
                stock_level=item.stock_level,
                reorder_point=item.reorder_point,
                is_low_stock=item.is_low_stock,
            )
        )
    return results
