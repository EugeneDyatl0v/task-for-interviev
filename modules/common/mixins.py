import asyncio

from logger import logger

from modules.common.helpers import send_email

from settings import UnisenderConfig


class SendEmailMixin:
    @classmethod
    async def send_email_to_user_via_unisender(
            cls,
            message_subject: str,
            template_data: dict,
            template_id: str,
            email_address: str,
    ) -> None:
        try:
            await asyncio.wait_for(
                send_email(
                    message_subject,
                    email_address,
                    template_data,
                    template_id
                ),
                timeout=int(UnisenderConfig.sending_timeout)
            )
            logger.info(f"Message for {email_address} sent successfully")
        except asyncio.TimeoutError:
            logger.error(
                f"Timeout error: Sending message to Kafka took longer than "
                f"{UnisenderConfig.sending_timeout} seconds. "
                f"Email: {email_address}"
            )
        except Exception as e:
            logger.exception(
                f"Failed to send message to Kafka: {e}. Email: {email_address}"
            )
