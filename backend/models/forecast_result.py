from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    forecast_run_id: Mapped[int] = mapped_column(
        ForeignKey("forecast_runs.id"),
        nullable=False,
        index=True,
    )

    forecast_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    predicted_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    lower_bound: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    upper_bound: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )