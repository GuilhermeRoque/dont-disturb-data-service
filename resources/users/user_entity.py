from db import Base
from sqlalchemy import Column, Integer, String, DateTime, func
from resources.users.user import User


class UserEntity(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    phone = Column(String)
    provider = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    def to_domain(self) -> User:
        return User(id=self.id, name=self.name, email=self.email, cpf=self.cpf, phone=self.phone, created_at=self.created_at, provider=self.provider)

    @classmethod
    def from_domain(cls, user: User):
        return cls(id=user.id, name=user.name, email=user.email, cpf=user.cpf, phone=user.phone, created_at=user.created_at, provider=user.provider)