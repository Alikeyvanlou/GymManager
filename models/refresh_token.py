from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.db import Base


class RefreshTokenModel(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True)
    jti = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    user = relationship("UserModel", back_populates="tokens")


class RefreshTokenResponseModel(RefreshTokenModel):
    pass