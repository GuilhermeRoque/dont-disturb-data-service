import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"

async_engine = create_async_engine(DATABASE_URL, future=True, echo=True, pool_size=10, max_overflow=5)

AsyncSessionFactory = async_sessionmaker(async_engine, expire_on_commit=False)

Base = declarative_base()


async def get_db_conn() -> AsyncSession:
    db = AsyncSessionFactory()
    try:
        yield db
    finally:
        await db.close()


