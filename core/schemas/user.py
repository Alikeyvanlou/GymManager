from pydantic import BaseModel, Field, ConfigDict

from core.models.user import UserRole, SubscriptionStatus


class UserBaseSchema(BaseModel):
    id_number: str = Field(
        ...,
        min_length=10,
        max_length=10,
        pattern=r"^\d{10}$"
    )

    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    phone_num: str = Field(
        ...,
        pattern=r"^09\d{9}$"
    )

    weight: float | None = None
    height: float | None = None
    age: int | None = None
    experience_year: float | None = None


class UserRegisterSchema(BaseModel):
    id_number: str = Field(
        ...,
        min_length=10,
        max_length=10,
        pattern=r"^\d{10}$"
    )

    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    city: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    phone_num: str = Field(
        ...,
        pattern=r"^09\d{9}$"
    )


class UserResponseSchema(UserBaseSchema):
    id: int
    role: UserRole
    subscription: SubscriptionStatus

    model_config = ConfigDict(
        from_attributes=True
    )

class UserResponseSchema(UserBaseSchema):
    id: int
    role: UserRole
    subscription: SubscriptionStatus
    model_config = ConfigDict(
        from_attributes=True
    )

class UserSignVerifyResponseInSchema(BaseModel):

    phone_number: int
    access_token: str

class UserSignInResponse(BaseModel):
    phone_number: str
    expires_in: int

class UserDeleteSchema(BaseModel):
    id: int

