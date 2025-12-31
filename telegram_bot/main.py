import asyncio
from os import getenv
from dotenv import load_dotenv

# aiogram imports
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# Local imports
import handlers
import logger

# Initialize loggers
logger.initAllLoggers()
aiogram_logger = logger.getLogger("aiogram")

# Load bot token
load_dotenv("../config/tokens.env")
TOKEN = getenv("TELEGRAM_TOKEN")
aiogram_logger.info("Токен загружен")

# Initialize dispatcher
dp = Dispatcher()

async def main() -> None:

    bot = Bot(token=TOKEN)
    aiogram_logger.info("Бот запускается...")

    handlers.include_handlers(dp)
    aiogram_logger.info("Хендлеры подключены.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
