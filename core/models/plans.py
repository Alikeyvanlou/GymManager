from decimal import Decimal

from sqlalchemy import Numeric, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database.db import Base


class Plan(Base):
    __tablename__ = "plan"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    discount: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False
    )

    price_after_discount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )