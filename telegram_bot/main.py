# main.py
import contextlib
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import asyncio

# Импортируем готовые объекты
from telegram_bot.bot_instance import bot, dp, storage

# Local imports
import middlewares
import handlers
import logger
import database
import reminders

# Initialize logger
aiogram_logger = logger.getLogger("aiogram")
aiogram_logger.info("Токен загружен")

async def main() -> None:
    if bot is None:
        aiogram_logger.critical("Не удалось инициализировать бота. Проверьте токен.")
        return
    else:
        aiogram_logger.info("Бот запускается...")

    await database.db.init_db()
    aiogram_logger.info("База данных инициализирована.")

    handlers.include_handlers(dp)
    aiogram_logger.info("Хендлеры подключены.")

    middlewares.include_middlewares(dp)
    aiogram_logger.info("Middlewares подключены.")

    remindestask = asyncio.create_task(
        reminders.reminders.start_reminder_worker(bot, aiogram_logger)
    )

    try:
        await dp.start_polling(bot)
    finally:
        remindestask.cancel()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())