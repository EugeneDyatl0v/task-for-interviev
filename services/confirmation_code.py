import datetime

from database.models import (
    ConfirmationCodeModel,
    UserModel
)

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class ConfirmationCodeService:
    @staticmethod
    async def get_confirmation_code_by_code(
            code: str,
            db_session: AsyncSession = None
    ) -> ConfirmationCodeModel | None:
        query = (
            select(ConfirmationCodeModel)
            .filter_by(code=code)
            .options(
                selectinload(ConfirmationCodeModel.user)
            )
        )
        result = await db_session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def get_active_confirmation_code_by_user_id(
            user_id: str,
            db_session: AsyncSession = None
    ) -> ConfirmationCodeModel | None:
        query = (
            select(ConfirmationCodeModel)
            .filter_by(user_id=user_id, used=False)
            .order_by(desc(ConfirmationCodeModel.created_at))
        )
        result = await db_session.execute(query)
        return result.scalars().first()

    @staticmethod
    async def create_confirmation_code(
            code: str,
            user: UserModel,
            expired_at: datetime.datetime,
            db_session: AsyncSession = None
    ) -> 'ConfirmationCodeModel':
        await db_session.refresh(user)

        confirmation_code = ConfirmationCodeModel(
            code=code,
            user_id=user.id,
            expired_at=expired_at
        )
        db_session.add(confirmation_code)
        await db_session.commit()
        await db_session.refresh(confirmation_code)
        return confirmation_code
