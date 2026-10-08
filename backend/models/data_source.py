from datetime import datetime, UTC

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class DataSource(Base):
    __tablename__ = "data_sources"

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

    source_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    source_file: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_version: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )