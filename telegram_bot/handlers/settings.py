from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import Command

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from telegram_bot.keyboards.main import get_settings_language_keyboard, get_settings_keyboard_by_language, get_settings_timezone_keyboard
from telegram_bot.languages import get_commands, get_text_by_language
from database.interactions import reset_user_character, save_user_timezone
from core.timezone import find_time_zone

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from database.interactions import change_user_language

router = Router()


@router.message(F.text.in_(get_commands("settings")))
async def settings_handler(message: Message, logger, language_code):
    logger.debug("Открытие настроек для пользователя %s", message.from_user.id)
    await message.answer(get_text_by_language("settings", language_code), reply_markup=await get_settings_keyboard_by_language(language_code))


@router.message(F.text.in_(get_commands("reset_character")))
async def settings_command_handler(message: Message, logger, language_code):
    logger.debug("Сброс персонажа для пользователя %s", message.from_user.id)
    await reset_user_character(message.from_user.id)


# -------- Часовой пояс --------
@router.message(F.text.in_(get_commands("timezone")))
async def timezone_handler(message: Message, logger, language_code):
    logger.debug("Открытие настроек часового пояса для пользователя %s", message.from_user.id)
    await message.answer("Пожалуйста, поделитесь своей локацией или выберите ввод вручную.", reply_markup=get_settings_timezone_keyboard(language_code))

@router.message(F.content_type == "location")
async def location_handler(message: Message, logger, language_code):
    logger.debug("Получена локация от пользователя %s", message.from_user.id)
    lat = message.location.latitude
    lon = message.location.longitude

    tz_name = find_time_zone(lat, lon)
    if not tz_name:
        logger.warning("Не удалось определить часовой пояс по координатам пользователя %s", message.from_user.id)
        await message.answer("Не удалось определить часовой пояс по координатам. Можете ввести вручную.")
        return
    
    await save_user_timezone(message.from_user.id, tz_name)
        
    await message.answer(f"Определён часовой пояс: {tz_name}\nТекущее локальное время: {datetime.now(timezone.utc).astimezone(ZoneInfo(tz_name)).strftime('%Y-%m-%d %H:%M:%S %Z%z')}",
                         reply_markup=types.ReplyKeyboardRemove())


# -------- Выбор языка --------
@router.message(F.text.in_(get_commands("language")))
async def language_handler(message: Message, logger, language_code):
    logger.debug("Открытие выбора языка для пользователя %s", message.from_user.id)
    await message.answer(get_text_by_language("choose_language", language_code), reply_markup=get_settings_language_keyboard())

@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def process_language_callback(callback_query, logger):
    logger.debug("Изменение языка пользователя %s: %s", callback_query.from_user.id, callback_query.data)
    lang_code = callback_query.data.split(":")[1]
    await change_user_language(callback_query.from_user.id, lang_code)

    await callback_query.message.edit_reply_markup(reply_markup=None)

    await callback_query.answer("{0} на {1}".format(get_text_by_language("language_changed", lang_code), lang_code))
    await callback_query.message.answer(get_text_by_language("settings", lang_code), reply_markup=await get_settings_keyboard_by_language(lang_code))