from datetime import datetime
from pydantic import BaseModel, Field


class SizeSchema(BaseModel):
    name: str = Field(default=None)


class SizeInDBSchema(SizeSchema):
    id: int = Field(ge=1)
