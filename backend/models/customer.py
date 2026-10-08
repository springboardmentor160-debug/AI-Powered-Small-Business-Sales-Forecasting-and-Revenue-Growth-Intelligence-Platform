from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )