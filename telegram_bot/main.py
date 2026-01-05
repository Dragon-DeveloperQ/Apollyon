# Для получение файловых импортов из соседних директорий
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import asyncio

# aiogram imports
from aiogram import Bot, Dispatcher

# Local imports
import handlers
import logger as logger
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

    # await database.interactions.register_new_user(123456789, "test_user")

    # await database.interactions.reward_task_completion(1)

    # tasts = await database.interactions.get_all_tasks_for_character(1)
    # for task in tasts:
    #    aiogram_logger.info(f"Задание: {task.title}, Описание: {task.description}")


    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
