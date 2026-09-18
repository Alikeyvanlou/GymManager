from datetime import UTC, datetime, timedelta
from core.config import settings
import jwt
from fastapi import Response
from uuid import uuid4
from core.models.refresh_token import RefreshTokenModel

def create_OTP_code():
    return "123456"

def create_access_token(payload: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def create_refresh_token(response: Response, payload: dict, expires_delta: timedelta, user_id: int):
    to_encode = payload.copy()
    expire = datetime.now(UTC) + expires_delta
    jti = str(uuid4())
    to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    new_refresh_token = RefreshTokenModel(
        jti=jti, expires_at=expire, created_at=datetime.now(UTC), user_id=user_id
    )

    response.set_cookie(key="refresh_token", value=token, httponly=True, secure=True)
    return new_refresh_token