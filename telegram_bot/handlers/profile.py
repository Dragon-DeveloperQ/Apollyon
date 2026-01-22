from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from telegram_bot.keyboards.main import get_profile_keyboard, get_stat_points_keyboard
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
        profile_text = get_text_by_language("profile_info", language_code).format(username="Unknown", level=0, exp=0, gold=0)

    await message.answer(profile_text, reply_markup = await get_profile_keyboard(language_code))
    await stat_points_handler(message, logger, language_code)
    

async def stat_points_handler(message: Message, logger, language_code):
    #logger.debug("Демонстрация очков характеристик пользователя %s", message.from_user.id)
    try:
        stats = await get_character_stats(message.from_user.id)
        stat_points_text = (
            f"💪 Сила: {stats['strength']}\n"
            f"🤸 Ловкость: {stats['agility']}\n"
            f"❤️ Телосложение: {stats['physique']}\n"
            f"🧠 Интеллект: {stats['intelligence']}\n"
            f"📿 Мудрость: {stats['wisdom']}\n"
            f"🗣 Харизма: {stats['charisma']}\n"
            f"🍀 Удача: {stats['luck']}\n"
            f"\nДоступные очки для распределения: {stats['stat_points']}"
        )
        await message.answer(stat_points_text)
    except Exception as e:
        logger.error("Ошибка при получении очков характеристик для пользователя %s: %s", message.from_user.id, str(e))
        stat_points_text = "Не удалось получить информацию об очках характеристик."

@router.message(F.text.in_(get_commands("stat_points")))
async def stat_upgrade_handler(message: Message, logger, language_code):
    try:
        await message.answer(get_text_by_language("stat_points_upgrade", language_code), reply_markup = await get_stat_points_keyboard(language_code))
    except Exception as e:
        logger.error("Ошибка при отображении клавиатуры прокачки характеристик для пользователя %s: %s", message.from_user.id, str(e))