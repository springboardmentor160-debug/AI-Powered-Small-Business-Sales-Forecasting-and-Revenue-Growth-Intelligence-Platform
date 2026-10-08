from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Sale(Base):
    __tablename__ = "sales"

    __table_args__ = (
        UniqueConstraint(
            "source_system",
            "source_row_id",
            name="uq_sales_source_system_row",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    source_system: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    source_row_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    invoice: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id"),
        nullable=True,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    price: Mapped[float] = mapped_column(
        nullable=False,
    )

    invoice_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )