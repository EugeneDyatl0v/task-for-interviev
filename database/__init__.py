from database.customize import CustomAsyncSession

from settings import Database

from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(
    Database.url,
    pool_size=Database.pool_size,
    max_overflow=Database.max_overflow,
    pool_recycle=Database.pool_recycle,
    pool_pre_ping=Database.pool_pre_ping
)
Session = async_sessionmaker(engine)
CustomSession = async_sessionmaker(bind=engine, class_=CustomAsyncSession)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session


async def get_custom_session() -> CustomAsyncSession:
    async with CustomSession() as session:
        yield session
