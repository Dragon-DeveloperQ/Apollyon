import asyncio
import logging
from datetime import datetime
from aiogram import Bot

from database.interactions import get_users_for_reminders, send_notification, send_reminder

from os import getenv
from dotenv import load_dotenv
load_dotenv("../config/core.env")

REMINDERS_SEND_INTERVAL = float(getenv("REMINDERS_SEND_INTERVAL"))
REMINDERS_DELAY = float(getenv("REMINDERS_DELAY"))
REMINDERS_CHECK_DELAY = float(getenv("REMINDERS_CHECK_DELAY"))

async def start_reminder_worker(
        bot: Bot,
        logger: logging.Logger,
    ):


    while True:
        start_time = datetime.utcnow()

        try:
            # Получаем пользователей
            users = await get_users_for_reminders()
            logger.info("Цикл оповещений. Найдено пользователей: %d", len(users))

            # Если есть пользователи, которым нужно отправить напоминание
            for user in users:
                try:
                    if ((datetime.utcnow() - user.last_reminder_at).total_seconds()) > REMINDERS_SEND_INTERVAL :
                        await send_reminder(bot, user.telegram_id, user.language_code)
                except Exception as e:
                    logger.error("Ошибка отправки оповещений %s: %s", user.telegram_id, str(e))

                # Пауза между отправками
                await asyncio.sleep(REMINDERS_DELAY)

        except Exception as e:
            logger.exception("Необработанная ошибка в воркере оповещений: %s", e)

        await asyncio.sleep(REMINDERS_CHECK_DELAY)  # Фиксированная пауза между циклами