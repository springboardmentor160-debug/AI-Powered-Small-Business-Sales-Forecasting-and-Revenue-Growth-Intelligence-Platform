from datetime import datetime, UTC

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class ModelMetric(Base):
    __tablename__ = "model_metrics"

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

    metric_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    metric_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )