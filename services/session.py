from database.models import SessionModel

from fastapi_pagination import Params as PageParams
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SessionService:
    @staticmethod
    async def get_active_session(
            user_id: str,
            ip: str,
            db_session: AsyncSession
    ) -> SessionModel | None:
        query = (select(SessionModel).filter_by(
            user_id=user_id,
            ip=ip,
            is_active=True,
            is_closed=False
        ))
        result = await db_session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_by_id(
            session_id: str,
            db_session: AsyncSession
    ) -> SessionModel | None:
        query = (select(SessionModel).filter_by(id=session_id))
        result = await db_session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_sessions(
            user_id: str,
            params: PageParams,
            db_session: AsyncSession
    ):
        query = (select(SessionModel).filter_by(user_id=user_id))
        result = await paginate(db_session, query, params=params)
        return result

    @staticmethod
    async def close_sessions(
            db_session: AsyncSession,
            user_id: str,
            ip: str = None
    ) -> int:
        query = (
            update(SessionModel)
            .where(
                SessionModel.user_id == user_id and
                (not ip or ip and SessionModel.ip == ip) and
                SessionModel.is_active)
            .values(is_closed=True)
        )
        result = await db_session.execute(query)
        await db_session.commit()
        return result.rowcount

    @staticmethod
    async def delete(
            user_id: str,
            db_session: AsyncSession
    ) -> None:
        await db_session.execute(delete(SessionModel).where(
            SessionModel.user_id == user_id
        ))
        await db_session.commit()
