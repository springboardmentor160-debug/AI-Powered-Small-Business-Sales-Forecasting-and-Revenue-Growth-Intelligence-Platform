import logging
import threading
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from backend.auth import require_role
from backend.schemas.invoice import InvoiceCreate
from backend.services.invoice_service import (
    load_invoice_records,
    save_invoice_records,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)

INVOICE_LOCK = threading.Lock()


@router.get("/view")
def view_invoices(
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

    with INVOICE_LOCK:
        records = load_invoice_records()

    records = sorted(
        records,
        key=lambda item: item.get(
            "created_at",
            "",
        ),
        reverse=True,
    )

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

    total_amount = round(
        invoice.quantity
        * invoice.unit_price,
        2,
    )

    invoice_record = {
        "invoice_id": (
            "INV-"
            + uuid.uuid4().hex[:10].upper()
        ),
        "customer_name": (
            invoice.customer_name.strip()
        ),
        "product_name": (
            invoice.product_name.strip()
        ),
        "quantity": invoice.quantity,
        "unit_price": round(
            invoice.unit_price,
            2,
        ),
        "total_amount": total_amount,
        "payment_status": payment_status,
        "created_by": user["sub"],
        "created_at": (
            datetime.now(
                timezone.utc
            ).isoformat()
        ),
    }

    with INVOICE_LOCK:
        records = load_invoice_records()
        records.append(invoice_record)
        save_invoice_records(records)

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