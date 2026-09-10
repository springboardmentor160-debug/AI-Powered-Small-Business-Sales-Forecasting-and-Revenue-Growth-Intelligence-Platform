from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database.database import get_db
from app.models.invoice import Invoice
from app.models.sale import Sale
from app.models.user import User

router = APIRouter(prefix="/invoices", tags=["Invoices"])


class InvoiceCreate(BaseModel):
    sale_id: int
    invoice_number: str
    payment_status: str = "Pending"


@router.get("")
def list_invoices(
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles(
        "business_owner", "store_manager", "sales_executive", "admin"
    )),
):
    return db.query(Invoice).order_by(Invoice.id.desc()).all()


@router.post("")
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("sales_executive", "admin")),
):
    sale = db.query(Sale).filter(Sale.id == payload.sale_id).first()

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    if db.query(Invoice).filter(
        Invoice.invoice_number == payload.invoice_number
    ).first():
        raise HTTPException(status_code=400, detail="Invoice number already exists")

    invoice = Invoice(
        sale_id=sale.id,
        invoice_number=payload.invoice_number,
        amount=sale.revenue,
        payment_status=payload.payment_status,
        invoice_date=date.today(),
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice
