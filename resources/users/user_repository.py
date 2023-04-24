from sqlalchemy.ext.asyncio import AsyncSession
from logger import default_logger
from resources.users.user import User
from sqlalchemy import text


class UserRepository:
    @classmethod
    async def create(cls, user: User, session: AsyncSession) -> User:
        stmt = text("INSERT INTO users (email, cpf, provider, name, phone) VALUES (:email, :cpf, :provider, :name, :phone) RETURNING users.id, users.created_at")
        result = await session.execute(stmt, user.__dict__)
        first_result = result.first()
        user.id = first_result.id
        user.created_at = first_result.created_at
        return user

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[User]:
        stmt = text("SELECT * from users")
        result = await session.execute(stmt)
        return [
            User(
                cpf=row.cpf,
                phone=row.phone,
                email=row.email,
                name=row.name,
                provider=row.provider,
                created_at=row.created_at,
                id=row.id,
            ) for row in result
        ]

    @classmethod
    async def get_by_id(cls, user_id: int, session: AsyncSession) -> User:
        stmt = text("SELECT * from users WHERE id = :id")
        result = await session.execute(stmt, {"id": user_id})
        row = result.first()
        if not row:
            raise IndexError("Register don't exists")
        return User(
            cpf=row.cpf,
            phone=row.phone,
            email=row.email,
            name=row.name,
            provider=row.provider,
            created_at=row.created_at,
            id=row.id,
        )

    @classmethod
    async def check_exists_email(cls, email: str, session: AsyncSession) -> bool:
        stmt = text("SELECT email FROM users WHERE email = :email")
        result = await session.execute(stmt, {"email": email})
        row = result.first()
        return row is not None

    @classmethod
    async def check_exists_cpf(cls, cpf: str, session: AsyncSession) -> bool:
        stmt = text("SELECT cpf FROM users WHERE cpf = :cpf")
        result = await session.execute(stmt, {"cpf": cpf})
        row = result.first()
        return row is not None

    @classmethod
    async def check_exists_email_batch(cls, email_list: list[str], session: AsyncSession) -> list[str]:
        stmt = text("SELECT email FROM users WHERE email IN :email")
        result = await session.execute(stmt, {"email": email_list})
        return [row.email for row in result]

    @classmethod
    async def check_exists_cpf_batch(cls, cpf_list: list[str], session: AsyncSession) -> list[str]:
        stmt = text("SELECT cpf FROM users WHERE cpf IN :cpf")
        result = await session.execute(stmt, {"cpf": cpf_list})
        return [row.cpf for row in result]

    @classmethod
    async def create_many(cls, users: list[User], session: AsyncSession):
        users_created = [await cls.create(user=user, session=session) for user in users]
        return users_created

    @classmethod
    async def delete(cls, user_id: int, session: AsyncSession):
        stmt = text("DELETE FROM users WHERE id = :id")
        result = await session.execute(stmt, {'id': user_id})
        default_logger.info(result.first())
