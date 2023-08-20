from datetime import datetime
from pydantic import BaseModel, Field


class OrderDetailSchema(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    subtotal: float


class OrderDetailInDBSchema(OrderDetailSchema):
    id: int = Field(ge=1)
