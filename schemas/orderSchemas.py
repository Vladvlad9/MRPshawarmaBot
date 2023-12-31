from datetime import datetime
from pydantic import BaseModel, Field


class OrderSchema(BaseModel):
    user_id: int
    userName: str
    phone: str
    order_date = Field(default=datetime.now())
    total_amount: float = Field(default=0)
    time: str
    description: str
    confirm: bool = Field(default=False)
    bankcard: bool = Field(default=False)


class OrderInDBSchema(OrderSchema):
    id: int = Field(ge=1)
