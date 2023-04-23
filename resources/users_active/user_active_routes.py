from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db_conn
from fastapi import APIRouter, Depends

from resources.users_active.user_active_use_cases import UserActiveUseCases

user_active_router = APIRouter(
    prefix="/users_active"
)


@user_active_router.get("/")
async def get_users_active(async_session: AsyncSession = Depends(get_db_conn)):
    return await UserActiveUseCases.get_users_active(async_session)
