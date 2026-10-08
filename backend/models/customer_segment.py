from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class CustomerSegment(Base):
    __tablename__ = "customer_segments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    segment_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    cluster_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    algorithm: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),    )