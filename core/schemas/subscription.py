from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SubscriptionBaseSchema(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    start_date: date
    end_date: date


class SubscriptionCreateSchema(SubscriptionBaseSchema):
    user_id: int
    pay_for_this: Decimal = Field(
        ...,
        ge=0
    )


class SubscriptionResponseSchema(SubscriptionBaseSchema):
    id: int
    user_id: int

    remaining_day: int
    pay_for_this: Decimal
    total_price: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


class SubscriptionDeleteSchema(BaseModel):
    id: int