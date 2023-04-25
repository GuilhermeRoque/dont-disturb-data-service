from sqlalchemy.ext.asyncio import AsyncSession
from db import get_db_conn
from resources.users.user import UserRequestPayload, UserRegistered
from resources.users.user_use_cases import UserUseCases
from fastapi import APIRouter, Depends


user_router = APIRouter(
    prefix="/users"
)


@user_router.post("")
async def create_user(user: UserRequestPayload, async_session: AsyncSession = Depends(get_db_conn)) -> UserRegistered:
    return await UserUseCases.create_user(user, async_session)


@user_router.get("")
async def get_users(async_session: AsyncSession = Depends(get_db_conn)) -> list[UserRegistered]:
    return await UserUseCases.get_users(async_session)


@user_router.post("/batch")
async def create_users_batch(users: list[UserRequestPayload], async_session: AsyncSession = Depends(get_db_conn)) -> list[UserRegistered]:
    return await UserUseCases.create_users_batch(users, async_session)
