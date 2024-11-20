import http
from datetime import datetime

from src.api.schemes.registration import (
    EmailConfirmationScheme
)

from fastapi import HTTPException

from services.confirmation_code import ConfirmationCodeService

from sqlalchemy.ext.asyncio import AsyncSession


async def abstract_confirmation(
        confirmation_code: str,
        db_session: AsyncSession,
        user_attribute: str,
        confirmation_scheme_class
):
    """
    Confirmation function.

    Args:
        confirmation_code (str): confirmation code from email or phone.
        db_session (AsyncSession):, database session.
        user_attribute (str): user attribute to check (email or phone).
        confirmation_scheme_class: scheme class to use for the response.
    """
    confirmation = await ConfirmationCodeService.get_confirmation_code_by_code(
        confirmation_code,
        db_session
    )

    if not confirmation:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Confirmation code not found'
        )

    user = confirmation.user
    if not user:
        raise HTTPException(
            status_code=http.HTTPStatus.NOT_FOUND,
            detail='User from confirmation code not found'
        )
    try:
        user_value = getattr(user, user_attribute)
    except AttributeError:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail=f'No {user_attribute} to confirm'
        )

    if confirmation.expired_at < datetime.utcnow():
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='Confirmation code expired'
        )
    if confirmation.used:
        raise HTTPException(
            status_code=http.HTTPStatus.BAD_REQUEST,
            detail='This confirmation code already used'
        )
    confirmation.used = True
    setattr(user, f'{user_attribute}_verified', True)
    user.updated_at = datetime.utcnow()

    db_session.add_all([user, confirmation])
    await db_session.flush()

    response_scheme = confirmation_scheme_class(
        **{
            user_attribute: user_value,
            f'{user_attribute}_verified': getattr(
               user, f'{user_attribute}_verified'
            )
        }
    )

    await db_session.commit()

    return response_scheme


async def email_confirmation(
        confirmation_code: str,
        db_session: AsyncSession
) -> EmailConfirmationScheme:
    return await abstract_confirmation(
        confirmation_code=confirmation_code,
        db_session=db_session,
        user_attribute='email',
        confirmation_scheme_class=EmailConfirmationScheme
    )
