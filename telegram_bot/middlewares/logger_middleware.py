import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from logger import loggerMiddleware

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class LoggerMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        # кладём логгер в контекст
        data["logger"] = loggerMiddleware
        
        return await handler(event, data)