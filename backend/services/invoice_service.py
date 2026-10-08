import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.invoice import Invoice


logger = logging.getLogger(__name__)


def create_invoice_record(
    db: Session,
    *,
    customer_name: str,
    product_name: str,
    quantity: int,
    unit_price: float,
    payment_status: str,
    created_by: str,
) -> dict:
    """Create and persist an invoice in PostgreSQL."""

    invoice_number = (
        "INV-"
        + uuid.uuid4().hex[:10].upper()
    )

    total_amount = round(
        quantity * unit_price,
        2,
    )

    created_at = datetime.now(UTC)

    invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=None,
        customer_name=customer_name.strip(),
        product_name=product_name.strip(),
        quantity=quantity,
        unit_price=round(unit_price, 2),
        total_amount=total_amount,
        status=payment_status,
        created_by=created_by,
        created_at=created_at,
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    logger.info(
        "Invoice %s persisted by %s",
        invoice.invoice_number,
        created_by,
    )

    return {
        "invoice_id": invoice.invoice_number,
        "customer_name": invoice.customer_name,
        "product_name": invoice.product_name,
        "quantity": invoice.quantity,
        "unit_price": invoice.unit_price,
        "total_amount": invoice.total_amount,
        "payment_status": invoice.status,
        "created_by": invoice.created_by,
        "created_at": invoice.created_at.isoformat(),
    }


def load_invoice_records(
    db: Session,
) -> list[dict]:
    """Load invoices from PostgreSQL."""

    invoices = db.scalars(
        select(Invoice).order_by(
            Invoice.created_at.desc()
        )
    ).all()

    return [
        {
            "invoice_id": invoice.invoice_number,
            "customer_name": invoice.customer_name,
            "product_name": invoice.product_name,
            "quantity": invoice.quantity,
            "unit_price": invoice.unit_price,
            "total_amount": invoice.total_amount,
            "payment_status": invoice.status,
            "created_by": invoice.created_by,
            "created_at": invoice.created_at.isoformat(),
        }
        for invoice in invoices
    ]