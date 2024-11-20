import datetime

from database.models import ConfirmationCodeModel, UserModel

from modules.common.helpers import generate_random_string
from modules.common.mixins import SendEmailMixin

from services.abstract import AbstractPasswordRecovery
from services.user import UserService

from settings import TemplatesConfig, UnisenderConfig

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemes.password_recovery import EmailRecoveryScheme


class EmailPasswordRecovery(AbstractPasswordRecovery, SendEmailMixin):
    async def _get_user(
            self,
            credentials: EmailRecoveryScheme,
            db_session: AsyncSession
    ) -> UserModel | None:
        return await UserService.get_by_email(
            credentials.email,
            db_session
        )

    async def _create_confirmation_code(
            self,
            user: UserModel,
            db_session: AsyncSession
    ) -> ConfirmationCodeModel | None:
        code_value = generate_random_string(10)

        await db_session.refresh(user)

        confirmation_code = ConfirmationCodeModel(
            code=code_value,
            user_id=user.id,
            expired_at=(
                datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            )
        )
        db_session.add(confirmation_code)
        await db_session.flush()

        return confirmation_code

    async def _send_confirmation_code(
            self,
            credentials: EmailRecoveryScheme,
            confirmation_code: str
    ) -> None:
        await SendEmailMixin.send_email_to_user_via_unisender(
            email_address=credentials.email,
            message_subject=TemplatesConfig.subject_reset_password,
            template_data={
                'reset_link': confirmation_code,
            },
            template_id=UnisenderConfig.password_reset_template_id
        )
