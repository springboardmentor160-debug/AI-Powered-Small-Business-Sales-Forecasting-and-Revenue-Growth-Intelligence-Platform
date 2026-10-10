from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    model_config = {"from_attributes": True}
