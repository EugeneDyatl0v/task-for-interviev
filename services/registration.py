import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.registration import (
    EmailRegisterScheme
)
from database.models import ConfirmationCodeModel, UserModel
from logger import logger
from modules.auth.helpers import get_password_hash
from modules.common.helpers import generate_random_string
from modules.common.mixins import SendEmailMixin
from services.abstract import AbstractRegistration
from services.user import UserService
from settings import TemplatesConfig, UnisenderConfig


class EmailRegistration(AbstractRegistration, SendEmailMixin):
    is_password_recovery = True

    async def _user_exists(
            self,
            registration_data: EmailRegisterScheme,
            db_session: AsyncSession
    ) -> bool:
        return bool(await UserService.get_by_email(
            registration_data.email,
            db_session
        ))

    async def _register(
            self,
            request: EmailRegisterScheme,
            db_session: AsyncSession
    ) -> UserModel:
        user = UserModel(
            email=request.email,
            password_hash=await get_password_hash(
                request.password
            ),
        )
        db_session.add(user)
        await db_session.flush()
        return user

    async def _create_confirmation_code(
            self,
            user: UserModel,
            db_session: AsyncSession
    ) -> str:
        confirmation_code = generate_random_string(10)

        await db_session.refresh(user)

        reset_code = ConfirmationCodeModel(
            code=confirmation_code,
            user_id=user.id,
            expired_at=datetime.datetime.utcnow() + datetime.timedelta(
                minutes=60)
        )
        db_session.add(reset_code)
        await db_session.flush()
        return confirmation_code

    async def _send_confirmation_code(
            self,
            request: EmailRegisterScheme,
            confirmation_code: str
    ) -> None:
        logger.info('Sending confirmation code via Unisender')
        await self.send_email_to_user_via_unisender(
            message_subject=TemplatesConfig.subject_verification,
            template_data={'verification_link': confirmation_code},
            template_id=UnisenderConfig.registration_template_id,
            email_address=request.email
        )
