"""Persistent invoice snapshots built from existing sales transactions."""

from datetime import datetime, timezone
import re
import sqlite3
from io import BytesIO
from typing import Any

from openpyxl import Workbook

from backend.app.database import get_connection


TRANSACTION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,30}$")
INVOICE_NUMBER_PREFIX = "MM-INV-"


class InvoiceConflictError(Exception):
    """Raised when a transaction already has an invoice."""


class InvoiceNotFoundError(Exception):
    """Raised when an invoice or source record cannot be found."""


class InvoiceValidationError(Exception):
    """Raised when invoice input or source data is invalid."""


def _validate_transaction_id(transaction_id: str) -> str:
    normalized = transaction_id.strip()
    if not TRANSACTION_ID_PATTERN.fullmatch(normalized):
        raise InvoiceValidationError("transaction_id must contain 1 to 30 safe characters.")
    return normalized


def _invoice_row(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def create_invoice(transaction_id: str, created_by_user_id: int) -> dict[str, Any]:
    """Create one immutable invoice snapshot for an existing transaction."""
    normalized_transaction_id = _validate_transaction_id(transaction_id)
    invoice_number = f"{INVOICE_NUMBER_PREFIX}{normalized_transaction_id}"
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT invoice_id FROM invoices WHERE transaction_id = ?",
            (normalized_transaction_id,),
        ).fetchone()
        if existing:
            raise InvoiceConflictError("An invoice already exists for this transaction.")

        transaction = connection.execute(
            """
            SELECT
                transaction_id,
                date AS transaction_date,
                product_id,
                product_name,
                category,
                quantity,
                unit_price,
                total_amount,
                store_id,
                customer_id,
                payment_method
            FROM sales_transactions
            WHERE transaction_id = ?
            """,
            (normalized_transaction_id,),
        ).fetchone()
        if transaction is None:
            raise InvoiceNotFoundError("The source transaction was not found.")

        customer = connection.execute(
            """
            SELECT customer_id, name, email
            FROM customers
            WHERE customer_id = ?
            """,
            (transaction["customer_id"],),
        ).fetchone()
        if customer is None:
            raise InvoiceValidationError("The source customer is unavailable.")

        try:
            cursor = connection.execute(
                """
                INSERT INTO invoices (
                    invoice_number,
                    transaction_id,
                    customer_id,
                    store_id,
                    transaction_date,
                    issued_at,
                    status,
                    payment_status,
                    paid_amount,
                    customer_name,
                    customer_email,
                    product_id,
                    product_name,
                    category,
                    quantity,
                    unit_price,
                    total_amount,
                    payment_method,
                    created_by_user_id,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'issued', 'not_recorded', 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice_number,
                    transaction["transaction_id"],
                    customer["customer_id"],
                    transaction["store_id"],
                    transaction["transaction_date"],
                    now,
                    customer["name"],
                    customer["email"],
                    transaction["product_id"],
                    transaction["product_name"],
                    transaction["category"],
                    transaction["quantity"],
                    transaction["unit_price"],
                    transaction["total_amount"],
                    transaction["payment_method"],
                    created_by_user_id,
                    now,
                ),
            )
        except sqlite3.IntegrityError as error:
            raise InvoiceConflictError(
                "An invoice already exists for this transaction."
            ) from error

        return _invoice_row(
            connection.execute(
                "SELECT * FROM invoices WHERE invoice_id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        )


def list_invoices(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """Return persisted invoice snapshots in newest-first order."""
    if not 1 <= limit <= 100:
        raise InvoiceValidationError("limit must be between 1 and 100.")
    if offset < 0:
        raise InvoiceValidationError("offset must not be negative.")
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM invoices
            ORDER BY invoice_id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
    return [_invoice_row(row) for row in rows]


def get_invoice(invoice_id: int) -> dict[str, Any]:
    """Return one persisted invoice snapshot."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM invoices WHERE invoice_id = ?",
            (invoice_id,),
        ).fetchone()
    if row is None:
        raise InvoiceNotFoundError("Invoice not found.")
    return _invoice_row(row)


def build_invoice_workbook(invoice: dict[str, Any]) -> BytesIO:
    """Build an Excel invoice document from persisted invoice fields only."""
    workbook = Workbook()
    sheet = workbook.active
    if sheet is None:
        raise RuntimeError("Unable to create the invoice workbook.")
    sheet.title = "Invoice"
    rows = [
        ("Invoice number", invoice["invoice_number"]),
        ("Invoice status", invoice["status"]),
        ("Payment status", invoice["payment_status"]),
        ("Issued at", invoice["issued_at"]),
        ("Transaction ID", invoice["transaction_id"]),
        ("Transaction date", invoice["transaction_date"]),
        ("Customer ID", invoice["customer_id"]),
        ("Customer name", invoice["customer_name"]),
        ("Customer email", invoice["customer_email"] or ""),
        ("Store ID", invoice["store_id"]),
        ("Product ID", invoice["product_id"]),
        ("Product name", invoice["product_name"]),
        ("Category", invoice["category"] or ""),
        ("Quantity", invoice["quantity"]),
        ("Unit price", invoice["unit_price"]),
        ("Total", invoice["total_amount"]),
        ("Payment method", invoice["payment_method"] or ""),
    ]
    sheet.append(("Field", "Value"))
    for row in rows:
        sheet.append(row)
    sheet.freeze_panes = "A2"
    sheet.column_dimensions["A"].width = 24
    sheet.column_dimensions["B"].width = 42
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output
