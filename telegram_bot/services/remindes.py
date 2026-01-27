import asyncio
import logging
from aiogram import Bot
from database import interactions
from database.models.models import User, UserPreferences  


from dotenv import load_dotenv
from os import getenv


load_dotenv("../config/core.env")
DELAY_BETWEEN_MESSAGES = int(getenv("REMINDER_DELAY_BETWEEN_MESSAGES", 1))
INTERVAL_SECONDS = int(getenv("REMINDER_INTERVAL_SECONDS", 60))

async def start_reminder_worker(
        bot: Bot, 
        logger: logging.Logger, 
        interval_seconds: int = INTERVAL_SECONDS, 
        delay_between_messages: float = DELAY_BETWEEN_MESSAGES):
    
    """
    bot — aiogram.Bot
    get_and_mark_callable — async функция, возвращающая список объектов с полями telegram_id и reminder_text
    """

    while True:
        try:
            users = await interactions.get_and_mark_users_for_reminder()
            if users:
                logger.info("Reminders: found %d users", len(users))
                for user in users:
                    try:
                        # отправляем пользователю по telegram_id
                        await bot.send_message(user.telegram_id, user.reminder_text)
                        await asyncio.sleep(delay_between_messages)
                    except Exception as e:
                        logger.exception("Ошибка при отправке reminder пользователю %s: %s", getattr(user, "id", None), e)
                        # при rate limit можно сделать backoff и повторить попытку
                        await asyncio.sleep(1)
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Reminder worker cancelled, exiting")
            break
        except Exception:
            logger.exception("Unhandled error in reminder worker; will retry after interval")
            await asyncio.sleep(interval_seconds)