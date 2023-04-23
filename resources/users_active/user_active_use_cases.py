from sqlalchemy.ext.asyncio import AsyncSession
from resources.users_active.user_active_repository import UserActiveRepository


class UserActiveUseCases:

    @classmethod
    async def get_users_active(cls, async_session: AsyncSession):
        repo = UserActiveRepository(async_session)
        return await repo.get_all()
