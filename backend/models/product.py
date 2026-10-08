from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stock_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )