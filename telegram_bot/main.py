# Для получение файловых импортов из соседних директорий
import contextlib
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from database import interactions
from telegram_bot.services.remindes import start_reminder_worker

import asyncio

# aiogram imports
from aiogram import Bot, Dispatcher

# Local imports
import middlewares
import handlers
import logger
import database

# Initialize logger
aiogram_logger = logger.getLogger("aiogram")

from os import getenv
from dotenv import load_dotenv
# Load bot token
load_dotenv("../config/tokens.env")
TOKEN = getenv("TELEGRAM_TOKEN")
aiogram_logger.info("Токен загружен")

# Initialize dispatcher
dp = Dispatcher()

async def main() -> None:

    bot = Bot(token=TOKEN)
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
    
    reminder_task = asyncio.create_task(start_reminder_worker(bot, aiogram_logger, get_and_mark_callable=interactions.get_and_mark_users_for_reminder))   

    try:
        await dp.start_polling(bot)
    finally:
        reminder_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await reminder_task
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
