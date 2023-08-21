from datetime import datetime
from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    user_id: int
    purchase_quantity: int


class UserInDBSchema(UserSchema):
    id: int = Field(ge=1)
