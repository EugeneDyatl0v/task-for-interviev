from datetime import datetime

from database.models import ConfirmationCodeModel

from modules.auth.helpers import get_password_hash

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemes.password_recovery import ResetCodeSchemeOut


async def create_reset_code_scheme(
        confirmation_code_model: ConfirmationCodeModel,
        db_session: AsyncSession = None
) -> ResetCodeSchemeOut:
    """
    Creating scheme.

    Args:
        confirmation_code_model: ConfirmationCodeModel
        db_session: AsyncSession
    """
    await db_session.refresh(confirmation_code_model)
    return ResetCodeSchemeOut(
        expired_at=confirmation_code_model.expired_at
    )


async def process_password_recovery(
        confirmation_code: ConfirmationCodeModel,
        password: str,
        db_session: AsyncSession = None
):
    """
    Recovery password and set reset code status on 'used'.

    Args:
        confirmation_code (ConfirmationCodeModel): confirmation code model.
        password (str):, new password.
        db_session (AsyncSession): database session.
    """
    await db_session.refresh(confirmation_code)
    confirmation_code.used = True
    user = confirmation_code.user
    user.updated_at = datetime.utcnow()
    user.password_hash = await get_password_hash(password)
    db_session.add_all([user, confirmation_code])
    await db_session.commit()
