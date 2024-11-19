from typing import Union

from modules.auth.classes import AuthAdmin, JWTBearer
from services.user import UserService
from src.api.auth.schemes import ChangePasswordScheme
from src.api.helpers.auth import get_login_handler
from src.api.schemas.auth import LoginResponse
from src.api.schemes import (
    ExceptionScheme,
    JWTScheme,
    Response200Scheme,
    jwt_bearer_responses
)

from database import get_session


from fastapi import (
    APIRouter, Depends, Request
)

from modules.auth.schemes import (
    EmailLoginScheme, UserInfo
)
from modules.auth.validators import (
    validate_refresh_token
)

from sqlalchemy.ext.asyncio import AsyncSession


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
        **jwt_bearer_responses,
        422: {
            'model': ExceptionScheme,
            'description': 'Invalid request scheme'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Authenticates user',
    response_model=None
)
async def login(
        login_info: EmailLoginScheme,
        request: Request,
        db_session: AsyncSession = Depends(get_session)
) -> Union[LoginResponse, Response200Scheme]:
    login_handler = get_login_handler(login_info)
    result = await login_handler(auth_class=AuthAdmin).login(
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

"""
@router.post(
    '/close-sessions/',
    responses={
        200: {
            'model': Response200Scheme,
            'description': 'Sessions were successfully closed'
        },
        **jwt_bearer_responses,
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Closes all user\'s sessions'
)
async def close_sessions(
        jwt_payload=Depends(JWTBearerAdmin()),
        db_session: AsyncSession = Depends(get_session)
) -> Response200Scheme:
    user_id = jwt_payload[JWTConfig.user_property].get('user_id')
    await SessionService.close_sessions(
        user_id=user_id,
        db_session=db_session
    )
    return Response200Scheme(message='All sessions were closed')
"""


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
    summary='Checks refresh token and returns new tokens'
)
async def refresh_tokens(
        refresh_payload: dict[str, str] = Depends(validate_refresh_token),
        db_session: AsyncSession = Depends(get_session)
) -> JWTScheme:
    auth_token, refresh_token = await AuthAdmin.update_tokens(
        jwt_payload=refresh_payload,
        db_session=db_session
    )
    return JWTScheme(
        auth_token=auth_token,
        refresh_token=refresh_token
    )
