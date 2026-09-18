from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PlanBaseSchema(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    description: str | None = None

    duration: int = Field(
        ...,
        gt=0
    )

    price: Decimal = Field(
        ...,
        gt=0
    )

    discount: Decimal = Field(
        default=0,
        ge=0,
        le=100
    )


class PlanCreateSchema(PlanBaseSchema):
    pass


class PlanResponseSchema(PlanBaseSchema):
    id: int
    price_after_discount: Decimal

    model_config = ConfigDict(
        from_attributes=True
    )


class PlanUpdateSchema(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    description: str | None = None

    duration: int | None = Field(
        default=None,
        gt=0
    )

    price: Decimal | None = Field(
        default=None,
        gt=0
    )

    discount: Decimal | None = Field(
        default=None,
        ge=0,
        le=100
    )


class PlanDeleteSchema(BaseModel):
    id: int