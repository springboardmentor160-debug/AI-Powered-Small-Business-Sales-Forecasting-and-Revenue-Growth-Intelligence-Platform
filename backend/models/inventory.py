from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    store_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    inventory_date: Mapped[object] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    initial_stock: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    units_sold: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    ending_stock: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )