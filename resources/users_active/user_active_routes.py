from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db_conn
from fastapi import APIRouter, Depends

from resources.users_active.user_active import UserActive
from resources.users_active.user_active_use_cases import UserActiveUseCases

user_active_router = APIRouter(
    prefix="/users_active"
)


@user_active_router.get("")
async def get_users_active(cpf: str = None,
                           email: str = None,
                           phone: str = None,
                           async_session: AsyncSession = Depends(get_db_conn)) -> list[UserActive]:
    filters = {'cpf': cpf, 'email': email, 'phone': phone}
    filters = {k: v for k, v in filters.items() if v is not None}
    return await UserActiveUseCases.get_users_active(async_session=async_session, filters=filters)