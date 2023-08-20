from datetime import datetime
from pydantic import BaseModel, Field


class ProductSchema(BaseModel):
    description: str
    price: float
    image_url: str
    category_id: int
    sub_category_id: int
    size_id : int


class ProductInDBSchema(ProductSchema):
    id: int = Field(ge=1)
