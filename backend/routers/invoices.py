import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.auth import require_role
from backend.database import get_db
from backend.schemas.invoice import InvoiceCreate
from backend.services.invoice_service import (
    create_invoice_record,
    load_invoice_records,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


@router.get("/view")
def view_invoices(
    db: Session = Depends(get_db),
    user: dict = Depends(
        require_role(
            [
                "business_owner",
                "admin",
                "store_manager",
                "sales_executive",
            ]
        )
    ),
):
    logger.info(
        "Invoice registry requested by %s",
        user["sub"],
    )

    records = load_invoice_records(db)

    return {
        "status": "Access Granted",
        "mode": "Read-Only",
        "message": (
            "Displaying active transaction "
            "invoice registry."
        ),
        "total_invoices": len(records),
        "invoices": records,
    }


@router.post("/create")
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(
        require_role(
            [
                "sales_executive",
                "admin",
            ]
        )
    ),
):
    payment_status = (
        invoice.payment_status
        .strip()
        .title()
    )

    allowed_statuses = {
        "Pending",
        "Paid",
        "Cancelled",
    }

    if payment_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid payment status. "
                "Use Pending, Paid, or Cancelled."
            ),
        )

    invoice_record = create_invoice_record(
        db,
        customer_name=invoice.customer_name,
        product_name=invoice.product_name,
        quantity=invoice.quantity,
        unit_price=invoice.unit_price,
        payment_status=payment_status,
        created_by=user["sub"],
    )

    logger.info(
        "Invoice %s created by %s",
        invoice_record["invoice_id"],
        user["sub"],
    )

    return {
        "status": "Success",
        "mode": "Write-Authorized",
        "message": (
            "Invoice created and "
            "persisted successfully."
        ),
        "invoice": invoice_record,
    }