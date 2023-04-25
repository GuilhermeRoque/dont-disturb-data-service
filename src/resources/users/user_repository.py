from sqlalchemy.ext.asyncio import AsyncSession
from logger import default_logger
from resources.users.user import UserRegistered, UserRequestPayload
from sqlalchemy import text

from resources.utils.sql_query_utils import get_sql_in_params


class UserRepository:

    @classmethod
    async def create(cls, user: UserRequestPayload, session: AsyncSession) -> UserRegistered:
        stmt = text("INSERT INTO users (email, cpf, provider, name) VALUES (:email, :cpf, :provider, :name) RETURNING users.id, users.created_at")
        result = await session.execute(stmt, user.__dict__)
        first_result = result.first()
        default_logger.info(first_result)
        default_logger.info("\n\n")
        user_registered = UserRegistered(
            cpf=user.cpf,
            email=user.email,
            name=user.name,
            provider=user.provider,
            created_at=first_result.created_at,
            id=first_result.id
        )
        return user_registered

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[UserRegistered]:
        stmt = text("SELECT * from users")
        result = await session.execute(stmt)
        return [
            UserRegistered(
                cpf=row.cpf,
                email=row.email,
                name=row.name,
                provider=row.provider,
                created_at=row.created_at,
                id=row.id,
            ) for row in result
        ]

    @classmethod
    async def get_all_in_cpf(cls, session: AsyncSession, cpf_list: list[str]) -> list[UserRegistered]:
        params, placeholder = get_sql_in_params("cpf", cpf_list)
        stmt = text(f"SELECT * from users WHERE cpf IN {placeholder}")
        result = await session.execute(stmt, params)
        return [
            UserRegistered(
                cpf=row.cpf,
                email=row.email,
                name=row.name,
                provider=row.provider,
                created_at=row.created_at,
                id=row.id,
            ) for row in result
        ]
    @classmethod
    async def get_by_id(cls, user_id: int, session: AsyncSession) -> UserRegistered:
        stmt = text("SELECT * from users WHERE id = :id")
        result = await session.execute(stmt, {"id": user_id})
        row = result.first()
        if not row:
            raise IndexError("Register don't exists")
        return UserRegistered(
            cpf=row.cpf,
            email=row.email,
            name=row.name,
            provider=row.provider,
            created_at=row.created_at,
            id=row.id,
        )

    @classmethod
    async def check_exists_email(cls, email: str, session: AsyncSession) -> str:
        stmt = text("SELECT email FROM users WHERE email = :email")
        result = await session.execute(stmt, {"email": email})
        row = result.first()
        return row.email if row else None

    @classmethod
    async def check_exists_cpf(cls, cpf: str, session: AsyncSession) -> str:
        stmt = text("SELECT cpf FROM users WHERE cpf = :cpf")
        result = await session.execute(stmt, {"cpf": cpf})
        row = result.first()
        return row.cpf if row else None

    @classmethod
    async def check_exists_email_batch(cls, email_list: list[str], session: AsyncSession) -> list[str]:
        result = await cls._get_select_in_query_params("email", email_list, session)
        return [row.email for row in result]

    @classmethod
    async def check_exists_cpf_batch(cls, cpf_list: list[str], session: AsyncSession) -> list[str]:
        result = await cls._get_select_in_query_params("cpf", cpf_list, session)
        return [row.cpf for row in result]

    @classmethod
    async def _get_select_in_query_params(cls, name: str, params: list[str], session: AsyncSession):
        in_params, in_placeholders = get_sql_in_params(name, params)
        query = f"SELECT {name} FROM users WHERE {name} IN {in_placeholders}"
        stmt = text(query)
        result = await session.execute(stmt, in_params)
        return result

    @classmethod
    async def create_many(cls, users: list[UserRequestPayload], session: AsyncSession):
        users_created = [await cls.create(user=user, session=session) for user in users]
        return users_created

    @classmethod
    async def delete(cls, user_id: int, session: AsyncSession):
        stmt = text("DELETE FROM users WHERE id = :id")
        result = await session.execute(stmt, {'id': user_id})
        default_logger.info(result.first())
