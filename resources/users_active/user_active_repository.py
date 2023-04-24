from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from logger import default_logger
from resources.users_active.user_active import UserActive
from resources.utils.sql_query_utils import get_sql_in_params


class UserActiveRepository:

    @classmethod
    async def get_all(cls, async_session: AsyncSession, filters: dict = None) -> list[UserActive]:
        result = await cls._get_all(async_session, filters)
        return [UserActive(cpf=row.cpf, phone=row.phone, email=row.email, name=row.name) for row in result]

    @classmethod
    async def get_all_phones_from_cpf(cls, async_session: AsyncSession, cpf: str, phones: list[str]) -> list[str]:
        params, place_holders = get_sql_in_params(name="phone", params=phones)
        query = f"SELECT phone from users_active where cpf = :cpf AND phone IN {place_holders}"
        stmt = text(query)
        result = await async_session.execute(stmt, {"cpf": cpf, **params})
        return [row.phone for row in result]

    @classmethod
    async def get_one(cls, async_session: AsyncSession, filters: dict = None) -> UserActive | None:
        result = await cls._get_all(async_session, filters)
        row = result.first()
        if row:
            return UserActive(cpf=row.cpf, phone=row.phone, email=row.email, name=row.name)
        return None

    @classmethod
    async def _get_all(cls, async_session, filters):
        filters = filters or dict()
        query = f"SELECT * from users_active"
        if filters:
            query += " WHERE " + " AND ".join([f"{k} = :{k}" for k in list(filters.keys())])
        stmt = text(query)
        result = await async_session.execute(stmt, filters)
        return result
