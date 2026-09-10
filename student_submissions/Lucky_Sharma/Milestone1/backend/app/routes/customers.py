from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.database import get_db
from app.models.customer import Customer
from app.models.user import User

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("")
def list_customers(
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles(
        "business_owner", "store_manager", "sales_executive", "admin"
    )),
):
    return db.query(Customer).order_by(Customer.id).all()
