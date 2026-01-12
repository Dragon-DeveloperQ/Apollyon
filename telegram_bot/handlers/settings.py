from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from telegram_bot.keyboards.main import get_settings_keyboard_by_telegram_id, get_settings_language_keyboard, get_settings_keyboard_by_language
from telegram_bot.languages import get_commands

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from database.interactions import change_user_language

router = Router()

@router.message(F.text.in_(get_commands("settings")))
async def settings_handler(message: Message, logger):
    logger.debug("Открытие настроек для пользователя %s", message.from_user.id)
    await message.answer("Настройки:", reply_markup=await get_settings_keyboard_by_telegram_id(message.from_user.id))

@router.message(F.text.in_(get_commands("language")))
async def language_handler(message: Message, logger):
    logger.debug("Открытие выбора языка для пользователя %s", message.from_user.id)
    await message.answer("Выберите язык:", reply_markup=get_settings_language_keyboard())


@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def process_language_callback(callback_query, logger):
    logger.debug("Изменение языка пользователя %s: %s", callback_query.from_user.id, callback_query.data)
    lang_code = callback_query.data.split(":")[1]
    await change_user_language(callback_query.from_user.id, lang_code)

    await callback_query.message.edit_reply_markup(reply_markup=None)

    await callback_query.answer(f"Язык изменен на {lang_code}.")
    await callback_query.message.answer("Настройки:", reply_markup=await get_settings_keyboard_by_language(lang_code))