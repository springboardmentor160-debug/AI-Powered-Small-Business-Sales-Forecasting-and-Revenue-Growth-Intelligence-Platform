from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class DemandFeature(Base):
    __tablename__ = "demand_features"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id"),
        nullable=True,
        index=True,
    )

    store_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    feature_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    units_sold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    lag_1: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    lag_7: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    rolling_mean_7: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    lag_28: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    lag_56: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    lag_84: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    rolling_mean_7_28: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )