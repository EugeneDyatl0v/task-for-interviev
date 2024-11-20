import datetime
import http

from database import get_session

from fastapi import APIRouter, Depends, HTTPException

from services.confirmation_code import ConfirmationCodeService
from services.password_recovery import (
    EmailPasswordRecovery
)
from services.session import SessionService

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.helpers.password_recovery import (
    create_reset_code_scheme,
    process_password_recovery
)
from src.api.schemes.password_recovery import (
    ConfirmationCodeResponseScheme,
    EmailRecoveryScheme,
    PasswordScheme,
)
from src.api.schemes.response import ExceptionScheme, Response200Scheme


password_recovery_router = APIRouter(
    prefix='/password-recovery',
    tags=['Password recovery'],
)


@password_recovery_router.post(
    '/request',
    responses={
        200: {
            'model': ConfirmationCodeResponseScheme,
            'description': 'Send message for password recovery.'
        },
        400: {
            'model': ExceptionScheme,
            'description': 'User with this credentials not exists.'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Request password recovery via email.'
)
async def password_recovery_request(
        credentials: EmailRecoveryScheme,
        db_session: AsyncSession = Depends(get_session)
):
    if isinstance(credentials, EmailRecoveryScheme):
        confirm_code_model = await EmailPasswordRecovery(
        ).password_recovery_request(
            credentials,
            db_session
        )
    else:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Invalid credentials'
        )

    response_scheme = await create_reset_code_scheme(
        confirm_code_model,
        db_session
    )

    return ConfirmationCodeResponseScheme(
        message='Message sent.',
        result=response_scheme
    )


@password_recovery_router.patch(
    '/{confirmation_code}',
    responses={
        200: {
            'model': Response200Scheme,
            'description': 'User password updated.'
        },
        400: {
            'model': ExceptionScheme,
            'description': 'Problem with confirmation code.'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Update password via confirmation code.'
)
async def password_recovery(
        confirmation_code: str,
        request: PasswordScheme,
        db_session: AsyncSession = Depends(get_session)
):
    confirm = await ConfirmationCodeService.get_confirmation_code_by_code(
        confirmation_code,
        db_session
    )
    if not confirm:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Reset code not found'
        )

    if confirm.expired_at < datetime.datetime.utcnow():
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Reset code code expired'
        )
    if confirm.used:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='This reset code already used'
        )
    await process_password_recovery(confirm, request.password, db_session)
    await db_session.refresh(confirm)
    closed_sessions_count = await SessionService.close_sessions(
        user_id=confirm.user_id,
        db_session=db_session
    )

    return Response200Scheme(message=(
        f'User password updated {closed_sessions_count} sessions closed'
    ))
