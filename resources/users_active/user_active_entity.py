from db import Base
from sqlalchemy import Column, Integer, String, DateTime, func
from resources.users_active.user_active import UserActive


class UserActiveEntity(Base):
    __tablename__ = "users_active"

    id = Column(Integer, primary_key=True, index=True)
    cpf = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    phone = Column(String)

    def to_domain(self) -> UserActive:
        return UserActive(id=self.id, name=self.name, email=self.email, cpf=self.cpf, phone=self.phone)

    @classmethod
    def from_domain(cls, user: UserActive):
        return cls(id=user.id, name=user.name, email=user.email, cpf=user.cpf, phone=user.phone)