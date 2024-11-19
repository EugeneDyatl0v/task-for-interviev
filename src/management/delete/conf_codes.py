import asyncio
import datetime
import sys

import click

from database import Session
from database.models import ConfirmationCodeModel

from logger import logger

from sqlalchemy import delete


async def process_delete_conf_codes():
    logger.info('Start deleting')
    delete_datetime = datetime.datetime.utcnow()
    async with Session() as session:
        query = delete(
            ConfirmationCodeModel
        ).where(
            ConfirmationCodeModel.expired_at < delete_datetime
        )
        await session.execute(query)
        await session.commit()
    logger.info('Finish deleting')


@click.command('delete_conf_codes')
def delete_conf_codes():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_delete_conf_codes())
    loop.close()
    sys.exit()
