from datetime import datetime
from pydantic import BaseModel, Field


class SubCategorySchema(BaseModel):
    category_id: int
    name: str


class SubCategoryInDBSchema(SubCategorySchema):
    id: int = Field(ge=1)
