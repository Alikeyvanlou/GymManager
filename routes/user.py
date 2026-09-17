from fastapi import APIRouter, HTTPException, status
from schemas.user import RegisterSchemaResponse, RegisterSchema, SignInSchema, TokenResponseModel, UserExistenceResponse, VerifyUserSchema, ResendOtpCode, ResendOtpCodeResponse
from fastapi import Depends, Request

from depen.database import get_db
from models.user import UserModel
from sqlalchemy.orm import Session
from sqlalchemy import Select
from datetime import datetime, UTC, timedelta

from core.auth import hashing_password, verifying_password, create_access_token, create_OTP_code, verify_otp_code

router = APIRouter(prefix="/users")

@router.post("/register", response_model=UserExistenceResponse)
async def register_user(item: RegisterSchema, request: Request, db: Session = Depends(get_db)):
    email_query = Select(UserModel).where(UserModel.email == item.email)
    if db.scalar(email_query) is not None:
        raise HTTPException(detail="email register before", status_code=status.HTTP_400_BAD_REQUEST)

    phone_number_query = Select(UserModel).where(UserModel.phone_number == item.phone_number)
    if db.scalar(phone_number_query) is not None:
        raise HTTPException(detail="phone register before", status_code=status.HTTP_400_BAD_REQUEST)
    time = datetime.now(UTC) + timedelta(seconds=10)
    otp_code = create_OTP_code(time=time.isoformat())

    registration_key = f"registration:{item.email}"
    redis_client = request.app.state.redis
    await redis_client.hset(
        registration_key,
        mapping={
            "first_name": item.first_name,
            "last_name": item.last_name,
            "email": item.email,
            "phone_number": item.phone_number,
            "password_hash": hashing_password(item.password),
            "otp": otp_code,
        },
    )
    await redis_client.expire(registration_key, 300)
    return {"send": True, "email": item.email, "phone_number": item.phone_number}

@router.post("/register/verify", response_model=RegisterSchemaResponse)
async def verify_user(item: VerifyUserSchema, request: Request, db: Session = Depends(get_db)):
    registration_key = f"registration:{item.email}"
    redis_client = request.app.state.redis
    data = await redis_client.hgetall(registration_key)

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Registration not found",
        )
    encoded_otp = data["otp"]
    otp_code = verify_otp_code(encode_otp_code=encoded_otp, user_code=item.code)

    if otp_code :
        user = UserModel(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone_number=data["phone_number"],
            password=data["password_hash"],
            status="active"
        )

        db.add(user)
        db.commit()

        await redis_client.delete(registration_key)

        return user

@router.post("/register/verify-resend", response_model=ResendOtpCodeResponse)
async def resend_otp_code(item: ResendOtpCode, request: Request):
    registration_key = f"registration:{item.email}"
    redis_client = request.app.state.redis
    data = await redis_client.hgetall(registration_key)

    if data.get("email") is None:
        raise HTTPException(detail="faild request.", status_code=status.HTTP_400_BAD_REQUEST)

    time = datetime.now(UTC)+timedelta(seconds=10)
    otp_code = create_OTP_code(time=time.isoformat())
    await redis_client.hset(
        registration_key,
        mapping={
            "otp": otp_code
        },
    )    
    return {"email": item.email, "resend": True}


@router.post("/login", response_model=TokenResponseModel)
def sign_in_user(item: SignInSchema, db: Session = Depends(get_db)):
    
    user = db.scalar(Select(UserModel).where(UserModel.email == item.email))
    if user is None:
        raise HTTPException(detail="Email or password not valid", status_code=status.HTTP_400_BAD_REQUEST)
    if not verifying_password(item.password, user.password):
        raise HTTPException(detail="Email or password not valid", status_code=status.HTTP_400_BAD_REQUEST)
    payload = {"sub": user.username}
    access_token = create_access_token(payload)
    return {"access_token": access_token, "token_type": "bearer"}

    