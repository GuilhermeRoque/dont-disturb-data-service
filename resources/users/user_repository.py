import datetime
import traceback
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from logger import logger
from resources.users.user import User
from resources.users.user_entity import UserEntity
from sqlalchemy.future import select


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        try:
            db_user = UserEntity.from_domain(user)
            self.session.add(db_user)
            await self.session.commit()
            await self.session.refresh(db_user)
            return db_user.to_domain()
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="User already exists")

    async def get_all(self) -> list[User]:
        try:
            stmt = select(UserEntity)
            result = await self.session.execute(stmt)
            users = [db_user for db_user in result.scalars().all()]
            return users
        except Exception as e:
            trace_str = traceback.format_exc()
            logger.error(f"{e}\n{trace_str}")
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Internal error")

    async def create_many(self, users: list[User]):
        try:
            db_users = [UserEntity.from_domain(user=user) for user in users]
            self.session.add_all(db_users)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="One or more users already exist")

    async def update(self, user: User) -> User:
        try:
            db_user = self.session.query(UserEntity).filter(UserEntity.id == user.id).first()
            if db_user is None:
                raise HTTPException(status_code=404, detail=f"User with id {user.id} not found")
            db_user.name = user.name
            db_user.email = user.email
            await self.session.commit()
            return db_user.to_domain()
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="User already exists")

    async def delete(self, user_id: int):
        try:
            db_user = self.session.query(UserEntity).filter(UserEntity.id == user_id).first()
            if db_user is None:
                raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")
            await self.session.delete(db_user)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="User could not be deleted")
