from typing import Union

from database import get_session

from fastapi import (
    APIRouter, Depends, Request
)

from modules.auth.classes import AuthUser, JWTBearer
from modules.auth.schemes import (
    EmailLoginScheme, UserInfo
)
from modules.auth.validators import (
    validate_refresh_token
)

from services.user import UserService

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.helpers.auth import get_login_handler
from src.api.schemes.auth import ChangePasswordScheme, JWTScheme, LoginResponse
from src.api.schemes.response import (
    ExceptionScheme,
    Response200Scheme,
    Response400Scheme,
    Response403Scheme,
    jwt_bearer_responses
)


router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)


@router.post(
    '/login/',
    responses={
        200: {
            'model': LoginResponse | Response200Scheme,
            'description': 'Returns tokens or redirect URI with tokens'
        },
        400: {
            'model': Response400Scheme,
            'description': 'Wrong credentials'
        },
        403: {
            'model': Response403Scheme,
            'description': 'Account deleted'
        },
        422: {
            'model': ExceptionScheme,
            'description': 'Invalid request scheme'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Authenticates a user and returns authentication tokens.'
)
async def login(
        login_info: EmailLoginScheme,
        request: Request,
        db_session: AsyncSession = Depends(get_session)
) -> Union[LoginResponse, Response200Scheme]:
    login_handler = get_login_handler(login_info)
    result = await login_handler(auth_class=AuthUser).login(
        credentials=login_info,
        request=request,
        db_session=db_session
    )
    auth_token = result.get('auth_token')
    refresh_token = result.get('refresh_token')
    return LoginResponse(
        auth_token=auth_token,
        refresh_token=refresh_token,
        continue_uri=None
    )


@router.patch(
    '/password/',
    responses={
        200: {
            'model': Response200Scheme,
            'description': 'Password successfully changed'
        },
        **jwt_bearer_responses,
        400: {
            'model': ExceptionScheme,
            'description': 'Session does not exist'
        },
        401: {
            'model': ExceptionScheme,
            'description': 'Invalid refresh token'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        },
    },
    summary='Changes the user\'s password.'
)
async def change_password(
    request: ChangePasswordScheme,
    db_session: AsyncSession = Depends(get_session),
    user_info: UserInfo = Depends(JWTBearer())
):
    await UserService.change_password(
        request.old_password,
        request.new_password,
        user_info.user_id,
        db_session
    )

    return Response200Scheme(
        message='Password successfully changed'
    )


@router.post(
    '/refresh/',
    responses={
        200: {
            'model': JWTScheme,
            'description': 'Returns new pair of tokens'
        },
        400: {
            'model': ExceptionScheme,
            'description': 'Session does not exist'
        },
        401: {
            'model': ExceptionScheme,
            'description': 'Invalid refresh token'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        },

    },
    summary='Validates the refresh token and returns a new pair of tokens.'
)
async def refresh_tokens(
        refresh_payload: dict[str, str] = Depends(validate_refresh_token),
        db_session: AsyncSession = Depends(get_session)
) -> JWTScheme:
    auth_token, refresh_token = await AuthUser.update_tokens(
        jwt_payload=refresh_payload,
        db_session=db_session
    )
    return JWTScheme(
        auth_token=auth_token,
        refresh_token=refresh_token
    )
