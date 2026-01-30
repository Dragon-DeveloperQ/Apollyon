import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from typing import Callable

from database.interactions import get_users_for_notifications

from os import getenv
from dotenv import load_dotenv
load_dotenv("../config/core.env")

NOTIFICATION_CHECK_INTERVAL = int(getenv("NOTIFICATION_CHECK_INTERVAL"))
NOTIFICATION_DELAY = float(getenv("NOTIFICATION_DELAY"))

async def start_reminder_worker(
        bot: Bot,
        logger: logging.Logger,
        tick_seconds: int = 10,
    ):


    while True:
        start_time = datetime.utcnow()

        try:
            # Получаем пользователей
            users = await get_users_for_notifications()
            logger.info("Cycle started. Found %d users to remind.", len(users))

            # Если есть пользователи, которым нужно отправить напоминание
            for user in users:
                try:
                    await bot.send_message(user.telegram_id, "Напоминание")  # Фиксированное сообщение
                    logger.info("Sent reminder to %s", user.telegram_id)
                except Exception as e:
                    logger.error("Failed to send reminder to %s: %s", user.telegram_id, str(e))

                # Пауза между отправками
                await asyncio.sleep(NOTIFICATION_DELAY)

        except Exception as e:
            logger.exception("Unhandled error in reminder worker: %s", e)

        # Ждём, чтобы начать следующий цикл
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        wait_time = max(0, tick_seconds - elapsed_time)  # Учитываем время выполнения цикла
        if wait_time > 0:
            await asyncio.sleep(wait_time)