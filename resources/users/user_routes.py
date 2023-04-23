from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db_conn
from resources.users.user import User
from resources.users.user_use_cases import UserUseCases
from fastapi import APIRouter, Depends

user_router = APIRouter(
    prefix="/users"
)


@user_router.post("")
async def create_user(user: User, async_session: AsyncSession = Depends(get_db_conn)):
    return await UserUseCases.create_user(user, async_session)


@user_router.get("")
async def get_users(async_session: AsyncSession = Depends(get_db_conn)):
    return await UserUseCases.get_users(async_session)


@user_router.post("/batch")
async def create_users_batch(users: list[User], async_session: AsyncSession = Depends(get_db_conn)):
    return await UserUseCases.create_users_batch(users, async_session)
