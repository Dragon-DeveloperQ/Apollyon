from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from telegram_bot.keyboards.main import get_profile_keyboard
from telegram_bot.languages import get_commands, get_text_by_language
from database.interactions import get_character_stats

router = Router()

@router.message(F.text.in_(get_commands("profile")))
async def start_handler(message: Message, logger, language_code):
    logger.debug("Демонстрация профиля пользователя %s", message.from_user.id)
    try:
        stats = await get_character_stats(message.from_user.id)
        profile_text = get_text_by_language("profile_info", language_code).format(
            username = stats['username'], 
            level = stats['level'], 
            exp = round(float(stats['exp']), 2), 
            gold = round(float(stats['gold']), 2)
            )
    except Exception as e:
        logger.error("Ошибка при получении информации профиля для пользователя %s: %s", message.from_user.id, str(e))
        profile_text = get_text_by_language("profile_info", language_code).format(name="Unknown", level=0, experience=0, gold=0)

    await message.answer(profile_text, reply_markup = await get_profile_keyboard(language_code))