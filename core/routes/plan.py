from fastapi import APIRouter
from fastapi import Depends, Request
from core.schemas.user import UserResponseSchema, UserRegisterSchema
from core.schemas.otp import VerifyOTPCodeSchema, ResponseOTPCodeSchema
from core.depen.database import get_db
from sqlalchemy.orm import Session
from core.crud.user import register_user, verify_user, resend_otp_code
from redis.asyncio import Redis
from core.schemas.plan import PlanResponseSchema

router = APIRouter(prefix="/plans")

from core.crud.plan import get_plans
@router.get("/", response_model=list[PlanResponseSchema])
async def get_plans_router(db: Session = Depends(get_db)):
   return await get_plans(db=db)