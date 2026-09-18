from pydantic import BaseModel, Field


class VerifyOTPCodeSchema(BaseModel):
    phone_num: str = Field(
        ...,
        pattern=r"^09\d{9}$"
    )

    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$"
    )


class ResponseOTPCodeSchema(BaseModel):
    message: str
    expires_in: int