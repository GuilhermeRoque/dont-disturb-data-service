import traceback
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from logger import logger
from sqlalchemy import text

from resources.users_active.user_active import UserActive


class UserActiveRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[UserActive]:
        try:
            stmt = text("SELECT * from users_active")
            result = await self.session.execute(stmt)
            return [UserActive(cpf=row.cpf, phone=row.phone, email=row.email, name=row.name) for row in result]
        except Exception as e:
            trace_str = traceback.format_exc()
            logger.error(f"{e}\n{trace_str}")
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal error")