import http

from database.models import UserModel

from fastapi import HTTPException

from jose import JWTError

from modules.auth.helpers import get_data_from_token

from passlib.context import CryptContext

from settings import AppConfig


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def validate_user(
    user: UserModel,
    password: str = None,
    no_user_msg: str = ''
) -> None:
    """Raises an exception if any user's property is invalid"""

    if not user:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail=no_user_msg
        )

    if (
        password and not await verify_password(password, user.password_hash)
    ):
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Wrong credentials'
        )

    if user.deleted_at:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Account deleted. Contact sysadmin'
        )

    if not (user.email and user.email_verified):
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail='Account not verified'
        )


async def validate_refresh_token(refresh_token: str) -> dict[str, str]:
    try:
        jwt_payload = await get_data_from_token(token=refresh_token)
    except JWTError:
        msg = 'Invalid refresh token'
        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            detail=msg
        )
    return jwt_payload


async def verify_password(
        plain_password: str,
        hashed_password: str
) -> bool:
    plain_password = f'{plain_password}{AppConfig.secret_key}'
    return pwd_context.verify(plain_password, hashed_password)
