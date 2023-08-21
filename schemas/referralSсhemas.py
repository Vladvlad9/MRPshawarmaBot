from pydantic import BaseModel, Field


class ReferralSchema(BaseModel):
    referring_user_id: int = Field(ge=1)
    referred_user_id: int = Field(ge=1)


class ReferralInDBSchema(ReferralSchema):
    id: int = Field(ge=1)
