from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):

    customer_name: str = Field(
        min_length=1,
        max_length=150,
    )

    product_name: str = Field(
        min_length=1,
        max_length=200,
    )

    quantity: int = Field(
        gt=0,
        le=1_000_000,
    )

    unit_price: float = Field(
        gt=0,
        le=100_000_000,
    )

    payment_status: str = Field(
        default="Pending",
        min_length=1,
        max_length=30,
    )