from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from resources.phones.phone import PhoneRequestPayload, PhoneRegistered
from resources.utils.sql_query_utils import get_sql_in_params


class PhonesRepository:

    @classmethod
    async def create(cls, phone: PhoneRequestPayload, session: AsyncSession) -> PhoneRegistered:
        stmt = text("INSERT INTO phones (phone, id_user) VALUES (:phone, :id_user) RETURNING phones.id, phones.created_at")
        result = await session.execute(stmt, phone.__dict__)
        first_result = result.first()
        phone_registered = PhoneRegistered(
            phone=phone.phone,
            id_user=phone.id_user,
            id=first_result.id,
            created_at=first_result.created_at
        )
        return phone_registered

    @classmethod
    async def create_many(cls, phones: list[PhoneRequestPayload], session: AsyncSession) -> list[PhoneRegistered]:
        return [await cls.create(phone=phone, session=session) for phone in phones]

    @classmethod
    async def delete_phones(cls, async_session: AsyncSession, phones: list[str]):
        params, placeholders = get_sql_in_params(name="phone", params=phones)
        query = f"DELETE from phones where phone IN {placeholders}"
        stmt = text(query)
        await async_session.execute(stmt, params)

