import traceback
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from logger import logger
from sqlalchemy.future import select

from resources.users_active.user_active import UserActive
from resources.users_active.user_active_entity import UserActiveEntity


class UserActiveRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[UserActive]:
        try:
            stmt = select(UserActiveEntity)
            result = await self.session.execute(stmt)
            users_active = [db_UserActive for db_UserActive in result.scalars().all()]
            return users_active
        except Exception as e:
            trace_str = traceback.format_exc()
            logger.error(f"{e}\n{trace_str}")
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal error")