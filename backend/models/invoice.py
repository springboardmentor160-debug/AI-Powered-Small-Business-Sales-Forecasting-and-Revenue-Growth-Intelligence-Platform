from datetime import datetime, UTC

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    invoice_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id"),
        nullable=True,
        index=True,
    )

    customer_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    product_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    unit_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    total_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Pending",
    )

    created_by: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )