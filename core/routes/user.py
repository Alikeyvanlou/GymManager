from fastapi import APIRouter
from fastapi import Depends, Request, Response
from core.schemas.user import *
from core.schemas.otp import VerifyOTPCodeSchema, ResponseOTPCodeSchema
from core.depen.database import get_db
from sqlalchemy.orm import Session
from core.crud.user import *
from redis.asyncio import Redis

router = APIRouter(prefix="/users")


@router.post("/register", response_model=ResponseOTPCodeSchema)
async def register_user_router(user_data: UserRegisterSchema,
                               request: Request,
                                db: Session = Depends(get_db)):
                                
  return await register_user(user_data=user_data, db=db, request= request)


@router.post("/register/verify", response_model=UserResponseSchema)
async def verify_user_roter(item: VerifyOTPCodeSchema,
                            request: Request,
                            db: Session = Depends(get_db)):

    return await verify_user(item=item, request=request, db=db)


@router.post("/register/verify-resend", response_model=ResponseOTPCodeSchema)
async def resend_otp_code_router(item: VerifyOTPCodeSchema, redis=Redis):
    return await resend_otp_code(user_data=item, redis=redis)


from fastapi.security import OAuth2PasswordRequestForm
@router.post("/sign-in", response_model=UserSignInResponse)
async def sign_in_user_router(request: Request, 
                              form_data: OAuth2PasswordRequestForm = Depends(), 
                              db: Session = Depends(get_db)): 
                        
    return await sign_in_user(request=request, form_data=form_data, db=db)


from fastapi.security import OAuth2PasswordRequestForm
@router.post("/sign-in/verify", response_model=UserSignVerifyResponseInSchema)
async def sign_in_verify_router(item: VerifyOTPCodeSchema, request: Request, response: Response, db: Session = Depends(get_db)):
                        
    return await sign_in_verify(request=request, item=item, db=db, response=response)

from core.models.user import User
from core.depen.database import get_current_user
@router.post("/", response_model=list[UserRegisterSchema])
async def users_info_router(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await users_info(user=user, db=db)