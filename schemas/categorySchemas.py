from datetime import datetime
from pydantic import BaseModel, Field


class CategorySchema(BaseModel):
    name: str


class CategoryInDBSchema(CategorySchema):
    id: int = Field(ge=1)
