import http

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy import select, and_

from database import get_session
from database.models import (
    SessionModel, UserModel,
)

from dotenv import load_dotenv

from fastapi import Request, HTTPException, Depends

from logger import logger
from modules.auth.abstract import (
    AbstractAuthHandler,
    AuthAbstract,
)
from modules.auth.jwt import JWTUser

from modules.auth.schemes import EmailLoginScheme, UserJwtPayload, UserInfo
from modules.auth.validators import validate_user

from services.session import SessionService
from services.user import UserService


from sqlalchemy.ext.asyncio import AsyncSession

from settings import JWTConfig

load_dotenv()


class AuthUser(AuthAbstract):
    JWT = JWTUser
    session_model = SessionModel
    session_service = SessionService


class EmailPasswordAuthHandler(AbstractAuthHandler):
    async def login(
            self,
            credentials: EmailLoginScheme,
            request: Request,
            db_session: AsyncSession,
            oauth_client_id: str | None = None
    ) -> dict[str, str]:
        user = await UserService.get_by_email(
            credentials.email,
            db_session
        )
        await validate_user(
            user=user,
            password=credentials.password,
            no_user_msg='Wrong credentials'
        )
        return await self.auth_class.login_process(
            user=user,
            ip=request.client.host,
            db_session=db_session
        )


class JWTBearer(HTTPBearer):
    """Requests token validation from auth0 and returns decoded payload"""
    def __init__(
            self,
            auto_error: bool = True,
    ):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(
            self,
            request: Request,
            db_session: AsyncSession = Depends(get_session),
    ) -> UserInfo | None:
        credentials: HTTPAuthorizationCredentials
        try:
            credentials = await (
                super(JWTBearer, self).__call__(request)
            )
        except HTTPException:
            raise HTTPException(
                http.HTTPStatus.UNAUTHORIZED,
                detail='Wrong credentials'
            )

        if not credentials:
            return None
        if credentials.scheme != 'Bearer':
            raise HTTPException(
                http.HTTPStatus.BAD_REQUEST,
                detail='Invalid token'
            )

        token = credentials.credentials

        self.validate_token_via_secret(token)

        payload = self.get_payload(token)


        query = (
            select(UserModel)
            .where(
                and_(
                    UserModel.id == payload.user_info.user_id,
                    UserModel.email_verified == True
                )
            )
        )
        result = await db_session.execute(query)
        db_user = result.scalars().one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='Token verification error'
            )

        query = (
            select(SessionModel)
            .where(
                and_(
                    SessionModel.id == payload.user_info.session_id,
                    SessionModel.is_active == True
                )
            )
        )
        result = await db_session.execute(query)
        db_session = result.scalars().one_or_none()

        if not db_session:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='Token verification error'
            )

        return payload.user_info

    def validate_token_via_secret(self, token: str) -> None:
        try:
            jwt.decode(
                token=token,
                key=JWTConfig.secret_key,
                algorithms=[JWTConfig.algorithm]
            )
        except JWTError as e:
            logger.exception(f'Token verification error: {e}')
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail='Token verification error'
            )

    def get_payload(self, token: str) -> UserJwtPayload:
        try:
            payload_dict = jwt.decode(
                token=token,
                key='',
                options={'verify_signature': False}
            )
        except (ValidationError, JWTError):
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail='Authentication service returned invalid token'
            )
        user_info = payload_dict.get('user_info')
        return UserJwtPayload(
            user_info=UserInfo(**user_info),
            token_uuid=payload_dict.get('token_uuid'),
            scope=payload_dict.get('scope')
        )
