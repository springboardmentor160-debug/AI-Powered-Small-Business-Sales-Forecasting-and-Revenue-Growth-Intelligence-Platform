from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=4,
        max_length=128,
    )

    role: str


class UserLogin(BaseModel):

    email: EmailStr

    password: str