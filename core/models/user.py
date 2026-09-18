from sqlalchemy import String, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
import enum

from core.database.db import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.subscription import Subscription
    from core.models.refresh_token import RefreshTokenModel
    
class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class SubscriptionStatus(enum.Enum):
    NONE = "none"
    ACTIVE = "active"
    EXPIRED = "expired"


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    id_number: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False,
        index=True
    )

    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    phone_num: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        nullable=False,
        index=True
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False
    )

    subscription: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus),
        default=SubscriptionStatus.NONE,
        nullable=False
    )

    # Optional fields
    weight: Mapped[float | None] = mapped_column(
        nullable=True
    )

    height: Mapped[float | None] = mapped_column(
        nullable=True
    )

    age: Mapped[int | None] = mapped_column(
        nullable=True
    )

    experience_year: Mapped[float | None] = mapped_column(
        nullable=True
    )

    subscriptions: Mapped[list["Subscription"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan"
    )

    tokens: Mapped[list["RefreshTokenModel"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan"
    )    