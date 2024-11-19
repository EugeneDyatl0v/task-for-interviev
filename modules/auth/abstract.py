import datetime
import http
import uuid
from abc import ABC
from typing import Union

from database import Session
from database.models import (
    SessionModel, UserModel
)

from dotenv import load_dotenv

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jose import JWTError, jwt

from modules.auth.helpers import get_session_by_id
from modules.auth.schemes import EmailLoginScheme
from modules.common.helpers import generate_random_string

from settings import JWTConfig

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()


class JWTBearerAbsract(HTTPBearer):
    scope: str = 'user'

    def __init__(
            self,
            auto_error: bool = True,
            roles: list[str] | None = None
    ):
        super(JWTBearerAbsract, self).__init__(auto_error=auto_error)
        self.roles = roles if roles else []

    async def __call__(self, request: Request) -> dict[str, str] | None:
        credentials: HTTPAuthorizationCredentials
        try:
            credentials = await (
                super(JWTBearerAbsract, self).__call__(request)
            )
        except HTTPException:
            raise HTTPException(
                http.HTTPStatus.BAD_REQUEST,
                detail='Wrong credentials'
            )

        error_invalid_token = HTTPException(
            http.HTTPStatus.BAD_REQUEST,
            detail='Invalid token'
        )
        error_no_rights = HTTPException(
            status_code=403,
            detail='Insufficient privileges'
        )

        if credentials:
            if not credentials.scheme == 'Bearer':
                raise error_invalid_token
            if not (
                payload := await self.verify_jwt(credentials.credentials)
            ):
                raise error_invalid_token

            user_property = JWTConfig.user_property

            provided_role = int(payload[user_property].get('role_id'))
            if not await self.role_allowed(provided_role):
                raise error_no_rights

            user_scope = payload.get('scope')
            if user_scope != self.scope:
                raise HTTPException(
                    status_code=http.HTTPStatus.FORBIDDEN,
                    detail='Invalid user scope'
                )

            await self.check_session(
                user_scope,
                payload[user_property].get('session_id'),
                payload=payload
            )
            return payload
        else:
            return None

    async def verify_jwt(self, token: str) -> (
            dict[str, str | dict[str, str]] | None
    ):
        """
        Decode JWT by algorithm and secret key.

        return: dict or None
            JWT payload with user's data
        """
        try:
            payload = jwt.decode(
                token, JWTConfig.secret_key, algorithms=[JWTConfig.algorithm]
            )
        except JWTError:
            payload = None
        return payload

    async def check_session(
            self,
            scope: str,
            session_id: str,
            payload: dict[str, str] | None = None
    ):
        """Checks whether the current session is active.

        Returns: bool, authentication result.
        """

        async with Session() as session:
            res = await session.execute(
                select(SessionModel).filter_by(id=session_id)
            )
            current_session = res.scalars().first()

        if current_session:
            if not current_session.is_active:
                raise HTTPException(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    detail='Session is inactive. Refresh it'
                )
            elif (
                    current_session.auth_token_data.get('token_uuid')
                    != payload.get('token_uuid')
            ):
                raise HTTPException(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    detail='Token is invalid'
                )
            elif current_session.is_closed:
                raise HTTPException(
                    status_code=http.HTTPStatus.UNAUTHORIZED,
                    detail='Session was closed. Log in again'
                )
            else:
                return True
        else:
            message = 'Session not found by ID'

        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            detail=message
        )

    async def role_allowed(self, provided_role: int) -> bool:
        if len(self.roles) == 0:
            return True
        if not provided_role:
            return False
        return False


class AuthAbstract(ABC):
    """Handles authentication operations

    Attributes:
        JWT (JWT): class for handling JWT operations.
        session_model: database model of which session objects are handled
    """
    JWT = None
    session_model: SessionModel | None = None

    @classmethod
    async def get_tokens(
            cls,
            auth_session: SessionModel,
            old_payload: dict[str, str] | None = None
    ):
        """
        Getting an authorization token and a refresh token.

        Args:
            auth_session (SessionModel): object of the session related
                to the current authorization.
            old_payload(dict or None): jwt payload
                if the token existed earlier.

        Returns:
            tuple(str, str), the authorization token and the refresh token.
        """

        token_gen = cls.JWT(
            auth_session,
            old_payload=old_payload
        )

        await token_gen.generate_payload()

        auth_token, auth_payload = await token_gen.generate_auth_token()
        (
            refresh_token,
            refresh_payload,
        ) = await token_gen.generate_refresh_token()

        return auth_token, refresh_token, auth_payload, refresh_payload

    @classmethod
    async def login_process(
            cls,
            user: UserModel,
            ip: str,
            db_session: AsyncSession,
            session_id: str | None = None
    ):
        """
        User login process with session creation.
        It is used with a standard user login.

        Args:
            user (UserModel): user to login.
            ip (str): client IP address
            session_id (str): id of user auth session
            db_session (AsyncSession): database connection.

        Returns:
            JSON object containing auth and refresh tokens
            or server error message
        """
        user_id = user.id
        if session_id:
            auth_session = await get_session_by_id(
                session_id,
                db_session=db_session
            )
            if not auth_session:
                raise HTTPException(
                    status_code=http.HTTPStatus.NOT_FOUND,
                    detail='Session not found by ID'
                )
        else:
            auth_session = cls.session_model(
                user_id=user_id,
                ip=ip
            )
            db_session.add(auth_session)
            await db_session.commit()
            await db_session.refresh(auth_session)

        (
            auth_token,
            refresh_token,
            auth_payload,
            refresh_payload,
        ) = await cls.get_tokens(auth_session=auth_session)

        auth_session.auth_token_data = auth_payload
        auth_session.refresh_token_data = refresh_payload

        db_session.add(auth_session)
        await db_session.commit()
        await db_session.refresh(auth_session)

        return {
            'auth_payload': auth_payload,
            'refresh_payload': refresh_payload,
            'auth_token': auth_token,
            'refresh_token': refresh_token,
        }

    @classmethod
    async def update_tokens(
            cls,
            jwt_payload: dict,
            db_session: AsyncSession,
    ):
        """Refresh tokens by user refresh_token.

        Returns: tuple(str, str)
            auth_token, refresh_token - new tokens for authorization
        """

        current_session = await get_session_by_id(
            session_id=jwt_payload[JWTConfig.user_property].get('session_id'),
            db_session=db_session
        )

        if current_session:
            if current_session.is_active:
                if (
                        current_session.refresh_token_data.get('refresh_uuid')
                        != jwt_payload.get('refresh_uuid')
                ):
                    raise HTTPException(
                        status_code=http.HTTPStatus.UNAUTHORIZED,
                        detail='Invalid refresh token '
                    )

                (
                    auth_token,
                    refresh_token,
                    auth_payload,
                    refresh_payload,
                ) = await cls.get_tokens(
                    auth_session=current_session.id,
                    old_payload=current_session.auth_token_data
                )

                current_session.auth_token_data = auth_payload
                current_session.refresh_token_data = refresh_payload

                db_session.add(current_session)
                await db_session.commit()
                await db_session.refresh(current_session)

                return auth_token, refresh_token

            msg = 'Session not active'
            raise HTTPException(
                status_code=http.HTTPStatus.UNAUTHORIZED,
                detail=msg
            )
        else:
            msg = 'Session does not exist'
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail=msg
            )

    @classmethod
    async def logout_user(
            cls,
            session_id: str,
            db_session: AsyncSession
    ):
        """User logout.Deactivating current session.

        Returns: None
        """
        current_session = await get_session_by_id(
            session_id=session_id,
            db_session=db_session
        )
        if not current_session:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail='Session not found by ID'
            )
        current_session.is_active = False

        db_session.add(current_session)
        await db_session.commit()
        await db_session.refresh(current_session)

    @staticmethod
    async def _get_session_for_confirm_code(user_id: str):
        raise NotImplementedError



class AbstractAuthHandler(ABC):
    def __init__(self, auth_class: AuthAbstract):
        self.auth_class = auth_class

    @staticmethod
    async def login(
            credentials: EmailLoginScheme,
            request: Request,
            db_session: AsyncSession,
            oauth_client_id: str | None = None
    ) -> dict[str, str]:
        pass
