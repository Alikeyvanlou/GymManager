from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, UTC
from core.config import settings
from uuid import uuid4
from fastapi import Response, HTTPException, status
from models.refresh_token import RefreshTokenModel

password_hash = PasswordHash.recommended()

def hashing_password(pwd: str):
    return password_hash.hash(pwd)

def verifying_password(pwd: str, hash_pwd:str):
    return password_hash.verify(pwd, hash_pwd)

def create_access_token(payload: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    token = jwt.encode(to_encode, "b2a7f90e29d08c8eb0534c69ee8d2fbed0519c6c1d08dae6428d7d8f98e78cca", algorithm="HS256")
    return token

def create_refresh_token(response: Response, payload: dict, expires_delta: timedelta, user_id: int):
    to_encode = payload.copy()
    expire = datetime.now(UTC) + expires_delta
    jti = str(uuid4())
    to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
    token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    new_refresh_token = RefreshTokenModel(
        jti=jti, expires_at=expire, created_at=datetime.now(UTC), user_id=user_id
    )

    response.set_cookie(key="refresh_token", value=token, httponly=True, secure=True)
    return new_refresh_token

def create_OTP_code(time: datetime):
    to_encode = {"code": "123456", "expire": time}
    otp_code = jwt.encode(to_encode, "b2a7f90e29d08c8eb0534c69ee8d2fbed0519c6c1d08dae6428d7d8f98e78cca", algorithm="HS256")
    return otp_code

def verify_otp_code(encode_otp_code: str, user_code: str):
    payload = jwt.decode(encode_otp_code, "b2a7f90e29d08c8eb0534c69ee8d2fbed0519c6c1d08dae6428d7d8f98e78cca", algorithms=["HS256"])
    otp_code = payload.get("code")

    if payload.get("code") is None:
        raise HTTPException(detail="Registration not found.", status_code=status.HTTP_400_BAD_REQUEST)

    if datetime.fromisoformat(payload.get("expire")) < datetime.now(UTC):
        raise HTTPException(detail="Registration expired.", status_code=status.HTTP_400_BAD_REQUEST)

    if payload.get("code") != user_code:
        raise HTTPException(detail="Invalid OTP.", status_code=status.HTTP_400_BAD_REQUEST)

    return otp_code

