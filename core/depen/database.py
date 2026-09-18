from datetime import UTC, datetime

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import Select
from sqlalchemy.orm import Session

from core.config import settings
from core.database.db import SessionLocal
from core.models.refresh_token import RefreshTokenModel
from core.models.user import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

http_bearer = HTTPBearer()
def get_current_user(db: Session = Depends(get_db), 
                     credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        phone_number = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
    except InvalidTokenError as e:
        raise credentials_exception from e

    query = Select(User).where(User.phone_num == phone_number)
    user = db.scalar(query)
    if user is None:
        raise credentials_exception
    return user


def verify_refresh_token(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("refresh_token")
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        phone_number = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
        if payload.get("type") != "refresh":
            raise credentials_exception
    except InvalidTokenError as e:
        raise credentials_exception from e

    user = db.scalar(Select(User).where(User.phone_num == phone_number))
    if user is None:
        raise credentials_exception
    jti = payload.get("jti")
    refresh_token = db.scalar(Select(RefreshTokenModel).where(RefreshTokenModel.jti == jti))

    if jti is None or refresh_token is None:
        raise credentials_exception
    if refresh_token.is_revoked:
        raise credentials_exception
    if refresh_token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        raise credentials_exception

    return refresh_token