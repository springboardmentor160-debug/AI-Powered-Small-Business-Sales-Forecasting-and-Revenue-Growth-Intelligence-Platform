from datetime import datetime, UTC

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class CustomerRFM(Base):
    __tablename__ = "customer_rfm"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    recency: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    frequency: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    monetary: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),    )