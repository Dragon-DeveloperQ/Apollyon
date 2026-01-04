import database
import logger as logger
import asyncio

from . import create
from . import read

db_logger = logger.getLogger("database")

async def register_new_user(telegram_id, username):
    db_logger.info(f"Регестрация пользователя: telegram_id={telegram_id}, username={username}")
    async with database.db.async_session_maker() as session:
        user_id = (await create.create_user(session, db_logger, telegram_id=telegram_id, username=username)).id
        await create.create_character(session, db_logger, user_id=user_id)