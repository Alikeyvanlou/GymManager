from sqlalchemy.orm import Session
from sqlalchemy import select
from core.models.plans import Plan

async def get_plans(db: Session):
    stmt = select(Plan)
    print(db.scalars(stmt))
    return db.scalars(stmt)