from sqlalchemy.ext.asyncio import AsyncSession
from resources.users_active.user_active_repository import UserActiveRepository


class UserActiveUseCases:

    @classmethod
    async def get_users_active(cls, async_session: AsyncSession, filters=None, repository=UserActiveRepository):
        return await repository.get_all(async_session=async_session, filters=filters)
