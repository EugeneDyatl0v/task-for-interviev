import datetime
import http
from typing import Optional
from uuid import UUID

from modules.auth.helpers import get_password_hash
from modules.auth.validators import verify_password
from src.api.schemes.users import (
    ClientEditUserScheme,
    EditUserScheme,
    UserFilterScheme,
)

from database.customize import CustomAsyncSession
from database.models import UserModel

from fastapi import HTTPException

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.async_sqlalchemy import paginate

from services.session import SessionService

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    @staticmethod
    async def create_user(
            email: str,
            password: str,
            email_verified: bool,
            deleted_at: Optional[datetime.datetime],
            created_at: Optional[datetime.datetime],
            updated_at: Optional[datetime.datetime],
            db_session: AsyncSession
    ) -> UserModel:
        user = UserModel(
            email=email,
            password_hash=password,
            email_verified=email_verified,
            deleted_at=deleted_at,
            created_at=created_at,
            updated_at=updated_at
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    @staticmethod
    async def update(
            user: UserModel,
            updated_user_data: EditUserScheme | ClientEditUserScheme,
            db_session: CustomAsyncSession
    ) -> UserModel:
        updated_data = updated_user_data.dict(exclude_unset=True)

        for key, value in updated_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.datetime.utcnow()

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        return user

    @staticmethod
    async def get_filtered_users(
            filters: UserFilterScheme,
            db_session: CustomAsyncSession,
            params: Params
    ) -> Page[UserModel]:
        query = select(UserModel)

        if filters.email:
            query = query.where(
                UserModel.email == filters.email
            )
        if filters.email_verified is not None:
            query = query.where(
                UserModel.email_verified == filters.email_verified
            )
        if filters.created_at is not None:
            start_time = filters.created_at - datetime.timedelta(minutes=1)
            end_time = filters.created_at + datetime.timedelta(minutes=1)
            query = query.where(
                UserModel.created_at.between(start_time, end_time))
        if filters.updated_at is not None:
            start_time = filters.updated_at - datetime.timedelta(minutes=1)
            end_time = filters.updated_at + datetime.timedelta(minutes=1)
            query = query.where(
                UserModel.updated_at.between(start_time, end_time))

        return await paginate(db_session, query, params)

    @staticmethod
    async def get_by_id(
            user_id: str | UUID,
            db_session: AsyncSession
    ) -> UserModel | None:
        query = (select(UserModel).filter_by(id=user_id))
        result = await db_session.execute(query)
        user = result.scalars().first()
        return user

    @staticmethod
    async def get_by_email(
            email: str,
            db_session: AsyncSession
    ) -> UserModel | None:
        query = (select(UserModel).filter_by(email=email))
        result = await db_session.execute(query)
        user = result.scalars().one_or_none()
        return user

    @staticmethod
    async def get_by_phone(
            phone_number: str,
            db_session: AsyncSession
    ) -> UserModel | None:
        query = (select(UserModel).filter_by(phone=phone_number))
        result = await db_session.execute(query)
        user = result.scalars().one_or_none()
        return user

    @staticmethod
    async def delete(
            user_id: str,
            db_session: CustomAsyncSession
    ):
        """Completely deletes user and their sessions by user_id"""
        await SessionService.delete(
            user_id=user_id,
            db_session=db_session
        )
        await db_session.execute(delete(UserModel).where(
            UserModel.id == user_id
        ))
        await db_session.commit()

    @staticmethod
    async def safe_delete(
            user_id: str,
            db_session: CustomAsyncSession
    ) -> None:
        user = await UserService.get_by_id(user_id, db_session)
        if not user:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail='User not found by id'
            )
        if user.deleted_at:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='User is already deleted'
            )
        await UserService.remove_deleted(
            db_session=db_session,
            email=user.email,
        )
        await db_session.refresh(user)
        user.deleted_at = datetime.datetime.utcnow()
        if user.email:
            user.email = f'deleted_{user.email}'

        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

    @staticmethod
    async def remove_deleted(
            db_session: CustomAsyncSession,
            email: str | None = None,
    ):
        """Removes rows of already deleted users by email and/or phone"""
        if not email:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='Both email and phone are None'
            )

        conditions = []

        if email is not None:
            conditions.append(UserModel.email == f'deleted_{email}')

        if conditions:
            result = await db_session.execute(
                select(UserModel.id).where(or_(*conditions)))
            user_ids = [str(user_id) for user_id in result.scalars().all()]

            for user_id in user_ids:
                await UserService.delete(
                    user_id=user_id,
                    db_session=db_session
                )

        await db_session.commit()

    @staticmethod
    async def change_password(
            old_password: str,
            new_password: str,
            user_id: str,
            db_session: AsyncSession
    ) -> None:
        query = select(UserModel).filter_by(id=user_id)
        result = await db_session.execute(query)
        db_user = result.scalars().one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail='User not found'
            )

        if not await verify_password(old_password, db_user.password_hash):
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='Incorrect password'
            )

        db_user.password_hash = await get_password_hash(new_password)

        await db_session.commit()

        await SessionService.close_sessions(
            user_id=user_id,
            db_session=db_session
        )

