import json

from sqlalchemy.orm import Session
from sqlalchemy import select
from core.schemas.user import UserResponseSchema, UserRegisterSchema
from core.models.user import User
from fastapi import HTTPException, Request, status, Response
from core.schemas.otp import VerifyOTPCodeSchema
from redis.asyncio import Redis
from core.auth import create_OTP_code, create_refresh_token
from datetime import timedelta

async def register_user(
    user_data: UserRegisterSchema,
    db: Session,
    request: Request
    ):
    # Check ID number
    stmt = select(User).where(
        User.id_number == user_data.id_number
    )

    user = db.scalar(stmt)

    if user:
        raise HTTPException(
            status_code=409,
            detail="This ID number is already registered."
        )

    # Prepare data
    user_data_dict = user_data.model_dump()

    otp = create_OTP_code()

    user_data_dict["otp"] = otp

    # Save in Redis
    registration_key = f"registration:{user_data.phone_num}"
    redis = request.app.state.redis
    
    await redis.set(
        registration_key,
        json.dumps(user_data_dict),
        ex=300)
    

    return {
        "message": "Registration information saved. OTP verification required.",
        "expires_in": 300
    }
  
async def verify_user(
    item: VerifyOTPCodeSchema,
    request: Request,
    db: Session
):
    redis_client = request.app.state.redis

    registration_key = f"registration:{item.phone_num}"

    # Get data from Redis
    data = await redis_client.get(registration_key)

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Registration not found or expired."
        )

    # JSON → Python dict
    data = json.loads(data)

    # Check OTP
    if data["otp"] != item.code:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP code."
        )

    # Remove OTP from data
    data.pop("otp")

    # Create user in PostgreSQL
    new_user = User(**data)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Delete temporary registration data
    await redis_client.delete(registration_key)

    return new_user

async def resend_otp_code(
    user_data: UserRegisterSchema,
    redis: Redis
    ):
    # Prepare data
    user_data_dict = user_data.model_dump()

    otp = create_OTP_code()

    user_data_dict["otp"] = otp

    # Save in Redis
    registration_key = f"registration:{user_data.phone_num}"

    await redis.set(
        registration_key,
        json.dumps(user_data_dict),
        ex=300
    )

    return {
        "message": "Registration information saved. OTP verification required.",
        "expires_in": 300
    }

from fastapi.security import OAuth2PasswordRequestForm
async def sign_in_user(form_data: OAuth2PasswordRequestForm, db: Session, request: Request):
    stmt = select(User).where(User.phone_num == form_data.username)
    if db.scalar(stmt) is None:
        raise HTTPException(detail="Your Phone Number Not Found.", 
                            status_code=status.HTTP_400_BAD_REQUEST)

     # Prepare data
    user_data_dict = {"phone_num":f"{form_data.username}"}
    
    otp_code = create_OTP_code()
    
    user_data_dict["otp"] = otp_code

    print(user_data_dict)
    # Save in Redis
    registration_key = f"registration:{form_data.username}"
    redis = request.app.state.redis
        
    await redis.set(
            registration_key,
            json.dumps(user_data_dict),
            ex=300)

    return {
        "phone_number": form_data.username,
        "expires_in": 300
    }
  
from core.auth import create_access_token
async def sign_in_verify(
    item: VerifyOTPCodeSchema,
    request: Request,
    db: Session,
    response: Response
):
    stmt = select(User.id).where(User.phone_num == item.phone_num)
    user_id = db.scalar(stmt)
    redis_client = request.app.state.redis

    registration_key = f"registration:{item.phone_num}"

    # Get data from Redis
    data = await redis_client.get(registration_key)

    if not data:
        raise HTTPException(
            status_code=400,
            detail="Registration not found or expired."
        )

    # JSON → Python dict
    data = json.loads(data)

    # Check OTP
    if data["otp"] != item.code:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP code."
        )
    payload={"sub": item.phone_num}
    access_token = create_access_token(payload=payload)
    refresh_token = create_refresh_token(
        response=response, payload=payload, expires_delta=timedelta(hours=24 * 7), user_id=user_id
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return {'phone_number': item.phone_num, "access_token": access_token}

from core.models.user import UserRole
async def users_info(user: User, db: Session):
    if user.role != UserRole.ADMIN:
        raise HTTPException(detail="This URL Not For your Role", status_code=status.HTTP_403_FORBIDDEN)

    stm = select(User)
    return db.scalars(stm).all()