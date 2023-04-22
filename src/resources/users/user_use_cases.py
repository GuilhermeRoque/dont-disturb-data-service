from sqlalchemy.ext.asyncio import AsyncSession
from resources.users.user import User
from resources.users.user_repository import UserRepository


class UserUseCases:

    @classmethod
    async def create_user(cls, user: User, async_session: AsyncSession):
        repo = UserRepository(async_session)
        return await repo.create(user)

    @classmethod
    async def get_users(cls, async_session: AsyncSession):
        repo = UserRepository(async_session)
        return await repo.get_all()

    @classmethod
    async def create_users_batch(cls, users: list[User], async_session: AsyncSession):
        repo = UserRepository(async_session)
        return await repo.create_many(users)
