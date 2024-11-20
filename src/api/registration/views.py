import datetime
import http

from database import get_session
from database.models import ConfirmationCodeModel

from fastapi import APIRouter, Depends, HTTPException, status

from modules.common.helpers import generate_random_string
from modules.common.mixins import SendEmailMixin

from services.confirmation_code import ConfirmationCodeService
from services.registration import EmailRegistration
from services.user import UserService

from settings import TemplatesConfig, UnisenderConfig

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.helpers.registration import (
    email_confirmation
)
from src.api.schemes.registration import (
    EmailConfirmationOutScheme, EmailRegisterScheme, EmailResendCodeScheme,
)
from src.api.schemes.response import ExceptionScheme, Response200Scheme


registration_router = APIRouter(
    prefix='/registration',
    tags=['Registration'],
)


@registration_router.post(
    '/',
    responses={
        200: {
            'model': Response200Scheme,
            'description': 'User registered.'
        },
        400: {
            'model': ExceptionScheme,
            'description': 'User already registered.'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Registers a new user using email.'
)
async def registration(
        request: EmailRegisterScheme,
        db_session: AsyncSession = Depends(get_session)
) -> Response200Scheme:
    if isinstance(request, EmailRegisterScheme):
        user = await EmailRegistration().register(
            request,
            db_session
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid request'
        )

    await db_session.refresh(user)

    return Response200Scheme(
        message='You are successfully registered.'
    )


@registration_router.patch(
    '/{confirmation_code}',
    responses={
        200: {
            'model': EmailConfirmationOutScheme,
            'description': 'Email/ confirmed.'
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
    summary='Confirms the user\'s email using a confirmation code.'
)
async def confirmation(
        confirmation_code: str,
        db_session: AsyncSession = Depends(get_session)
) -> EmailConfirmationOutScheme:
    confirm = await ConfirmationCodeService.get_confirmation_code_by_code(
        confirmation_code,
        db_session
    )

    if not confirm:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Confirmation code not found'
        )

    user = confirm.user
    if user.email and not user.email_verified:
        response_result = await email_confirmation(
            confirmation_code,
            db_session
        )
        return EmailConfirmationOutScheme(
            message='Email successfully confirmed.',
            result=response_result
        )
    else:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='No valid field to verify or already verified'
        )


@registration_router.post(
    '/resend_code',
    responses={
        200: {
            'model': Response200Scheme,
            'description': 'New confirmation code successfully sent.'
        },
        400: {
            'model': ExceptionScheme,
            'description': 'Problem with sending confirmation code.'
        },
        500: {
            'model': ExceptionScheme,
            'description': 'Internal server error'
        }
    },
    summary='Resends a confirmation code to the user via email.'
)
async def resend_code(
    request: EmailResendCodeScheme,
    db_session: AsyncSession = Depends(get_session)
) -> Response200Scheme:
    user = await UserService.get_by_email(request.email, db_session)

    if not user:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='User does not exists.'
        )

    confirmation_code = (
        await ConfirmationCodeService.get_active_confirmation_code_by_user_id(
            user.id, db_session
        )
    )

    if confirmation_code:
        confirmation_code.used = True
        db_session.add(confirmation_code)

    code = generate_random_string(10)
    confirm_code = ConfirmationCodeModel(
        code=code,
        user_id=user.id,
        expired_at=datetime.datetime.utcnow() + datetime.timedelta(
            minutes=60
        )
    )
    db_session.add(confirm_code)

    template_data = {'verification_link': code}
    await SendEmailMixin.send_email_to_user_via_unisender(
        message_subject=TemplatesConfig.subject_verification,
        template_data=template_data,
        template_id=UnisenderConfig.registration_template_id,
        email_address=request.email
    )

    await db_session.commit()

    return Response200Scheme(
        message='New confirmation code successfully sent.'
    )
