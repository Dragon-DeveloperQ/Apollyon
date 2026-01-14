import sys
from pathlib import Path

from logger import loggerMiddleware
from database.interactions import get_user_language, register_new_user

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class Middleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict):
        
        # Добавление логгера в данные middlewares
        data["logger"] = loggerMiddleware
        
        # Проверка пользователя на регестрацию
        user = data.get("event_from_user")
        if user is None:
            loggerMiddleware.debug("Не удалось получить пользователя из события для регестрации.")
            return await handler(event, data)

        if await get_user_language(user.id) is None:
            loggerMiddleware.debug("Регестрация пользователя %s", user.id)
            await register_new_user(user.id, user.full_name)

        # Определение языка пользователя
        user = data.get("event_from_user")
        if user is not None:
            language_code = await get_user_language(user.id)
        else:
            loggerMiddleware.debug("Не удалось получить пользователя из события для определения языка.")
            language_code = "en"  # Язык по умолчанию
        data["language_code"] = language_code


        return await handler(event, data)