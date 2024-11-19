import datetime
import http

from src.api.helpers.password_recovery import (
    create_reset_code_schema,
    process_password_recovery
)
from src.api.schemas.password_recovery import (
    ConfirmationCodeResponseScheme,
    EmailRecoverySchema,
    PasswordSchema,
)
from src.api.schemes import ExceptionScheme, Response200Scheme

from database import get_session

from fastapi import APIRouter, Depends, HTTPException

from services.confirmation_code import ConfirmationCodeService
from services.password_recovery import (
    EmailPasswordRecovery
)
from services.session import SessionService

from sqlalchemy.ext.asyncio import AsyncSession

password_recovery_router = APIRouter(
    prefix='/password-recovery',
    tags=['Password recovery'],
)


@password_recovery_router.post(
    '/request',
    responses={
            400: {
                'model': ExceptionScheme,
                'description': 'User with this credentials not exists.'
            },
            200: {
                'model': ConfirmationCodeResponseScheme,
                'description': 'Send message for password recovery.'
            }
        }
)
async def password_recovery_request(
        credentials: EmailRecoverySchema,
        db_session: AsyncSession = Depends(get_session)
):
    """
    Password recovery request via email or phone.
    Args:
        credentials: EmailRecoverySchema | PhoneRecoverySchema, user data.
        db_session: AsyncSession, database session.
    """

    if isinstance(credentials, EmailRecoverySchema):
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

    response_schema = await create_reset_code_schema(
        confirm_code_model,
        db_session
    )

    return ConfirmationCodeResponseScheme(
        message='Message sent.',
        result=response_schema
    )


@password_recovery_router.patch(
    '/{confirmation_code}',
    responses={
            400: {
                'model': ExceptionScheme,
                'description': 'Problem with confirmation code.'
            },
            200: {
                'model': Response200Scheme,
                'description': 'User password updated.'
            }
        }
)
async def password_recovery(
        confirmation_code: str,
        request: PasswordSchema,
        db_session: AsyncSession = Depends(get_session)
):
    """
    Password update via confirmation code.
    Args:
        confirmation_code: str, code from message.
        request: PasswordSchema, two passwords.
        db_session: AsyncSession, database session.
    """
    confirm = await ConfirmationCodeService.get_confirmation_code_by_code(
        confirmation_code,
        db_session
    )
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail='Reset code not found'
        )

    if confirm.expired_at < datetime.datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail='Reset code code expired'
        )
    if confirm.used:
        raise HTTPException(
            status_code=400,
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
