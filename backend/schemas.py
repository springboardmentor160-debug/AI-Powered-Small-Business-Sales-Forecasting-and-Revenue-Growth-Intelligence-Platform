from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

RoleName = Literal["business_owner", "store_manager", "sales_executive", "admin"]


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8, max_length=72)       # bcrypt only uses the first 72 bytes
    role: RoleName = "store_manager"
    admin_code: Optional[str] = Field(default=None, max_length=200)   # only needed when role == "admin"


class ForgotPassword(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ResetPassword(BaseModel):
    token: str = Field(min_length=10, max_length=200)
    new_password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str


class InvoiceCreate(BaseModel):
    customer_id: str
    description: Optional[str] = None
    amount: float = Field(gt=0)
    payment_status: Literal["pending", "paid", "overdue"] = "pending"


class InvoiceOut(InvoiceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class InvoiceStatusUpdate(BaseModel):
    payment_status: Literal["pending", "paid", "overdue"]
