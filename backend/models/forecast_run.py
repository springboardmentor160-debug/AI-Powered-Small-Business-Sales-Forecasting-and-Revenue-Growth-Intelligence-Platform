from datetime import date, datetime, UTC

from sqlalchemy import Date, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)

    training_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    training_end: Mapped[date | None] = mapped_column(Date, nullable=True)

    evaluation_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    evaluation_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    forecast_target: Mapped[str | None] = mapped_column(String(50), nullable=True)

    horizon: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
