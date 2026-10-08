from datetime import date

from sqlalchemy import Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class DateDimension(Base):
    __tablename__ = "dates"

    date: Mapped[date] = mapped_column(
        Date,
        primary_key=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    day: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )