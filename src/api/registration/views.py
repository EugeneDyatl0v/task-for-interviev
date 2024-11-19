import datetime
from typing import Union

from src.api.helpers.registration import (
    email_confirmation
)
from src.api.schemas.registration import (
    EmailConfirmationOutScheme, EmailRegisterScheme, EmailResendCodeScheme,
)
from src.api.schemes import ExceptionScheme, Response200Scheme

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


registration_router = APIRouter(
    prefix='/registration',
    tags=['Registration'],
)


@registration_router.post(
    '/',
    responses={
        400: {
            'model': ExceptionScheme,
            'description': 'User already registered.'
        },
        200: {
            'model': Response200Scheme,
            'description': 'User registered.'
        }
    }
)
async def registration(
        request: EmailRegisterScheme,
        db_session: AsyncSession = Depends(get_session)
):
    """Registers a new user using either email or phone, depending on the
    provided data.

    Args:
        request (EmailRegisterScheme): The registration
            data provided by the user. This can either be an email-based
            registration scheme.
        db_session (AsyncSession): The database session used to interact with
            the database.

    Returns:
        Response200Scheme: A response object containing a success message.

    Raises:
        HTTPException: If the user is already registered, a 400 error is
            returned with the relevant exception scheme.
    """

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
            400: {
                'model': ExceptionScheme,
                'description': 'Problem with confirmation code.'
            },
            200: {
                'model': EmailConfirmationOutScheme,
                'description': 'Email/ confirmed.'
            }
        }
)
async def confirmation(
        confirmation_code: str,
        db_session: AsyncSession = Depends(get_session)
) -> EmailConfirmationOutScheme:
    """
    Determine if the confirmation is for email and call
    the appropriate method.

    Args:
        confirmation_code: str, confirmation code from email.
        db_session: AsyncSession, database session.
    """
    confirm = await ConfirmationCodeService.get_confirmation_code_by_code(
        confirmation_code,
        db_session
    )

    if not confirm:
        raise HTTPException(
            status_code=400,
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
            status_code=400,
            detail='No valid field to verify or already verified'
        )


@registration_router.post(
    '/resend_code',
    responses={
        400: {
            'model': ExceptionScheme,
            'description': 'Problem with sending confirmation code.'
        },
        200: {
            'model':
                Response200Scheme,
            'description': 'New confirmation code successfully sent.'
        }
    }
)
async def resend_code(
    request: EmailResendCodeScheme,
    db_session: AsyncSession = Depends(get_session)
):
    """Resend a confirmation code to the user via email or phone.

    This endpoint handles the resending of confirmation codes based on the
    user's email or phone number.
    If a valid user is found, it marks the old confirmation code as used and
    generates a new one.
    The new code is then sent to the user.

    Args:
        request (EmailResendCodeScheme): A request
        object containing either email.
        db_session (AsyncSession): The database session dependency.

    Raises:
        HTTPException: If the user does not exist or if there is an issue
        sending the email.

    Returns:
        Response200Scheme: A response indicating the success of the operation.
    """

    user = await UserService.get_by_email(request.email, db_session)

    if not user:
        raise HTTPException(
            400,
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
            minutes=60)
    )
    db_session.add(confirm_code)

    template_data = {'code': code}
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
