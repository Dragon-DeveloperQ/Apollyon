from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram_bot.keyboards.main import get_profile_keyboard, get_stat_points_keyboard
from telegram_bot.languages import get_commands, get_text_by_language
from database.interactions import get_character_stats, increment_character_stat

router = Router()

class UpgradeStats(StatesGroup):
    waiting_for_stat_choice = State()

async def stat_points_handler(message: Message, logger, language_code):
    #logger.debug("Демонстрация очков характеристик пользователя %s", message.from_user.id)
    try:
        stats = await get_character_stats(message.from_user.id)
        stat_points_text = get_text_by_language("stat_points_info", language_code).format(
            strength = stats['strength'],
            agility = stats['agility'],
            physique = stats['physique'],
            intelligence = stats['intelligence'],
            wisdom = stats['wisdom'],
            charisma = stats['charisma'],
            luck = stats['luck'],
            stat_points = stats['stat_points']
        )
        await message.answer(stat_points_text)
    except Exception as e:
        logger.error("Ошибка при получении очков характеристик для пользователя %s: %s", message.from_user.id, str(e))
        stat_points_text = "Не удалось получить информацию об очках характеристик."

@router.message(F.text.in_(get_commands("profile")))
async def profile_handler(message: Message, logger, language_code):
    #logger.debug("Демонстрация профиля пользователя %s", message.from_user.id)
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
    
@router.message(F.text.in_(get_commands("stat_points")))
async def stat_upgrade_handler(message: Message, state: FSMContext, logger, language_code):
    try:
        await message.answer(get_text_by_language("stat_points_upgrade", language_code), reply_markup = await get_stat_points_keyboard(language_code))
        await state.set_state(UpgradeStats.waiting_for_stat_choice)
    except Exception as e:
        logger.error("Ошибка при отображении клавиатуры прокачки характеристик для пользователя %s: %s", message.from_user.id, str(e))
    
@router.message(UpgradeStats.waiting_for_stat_choice)
async def process_stat_choice(message: Message, state: FSMContext, logger, language_code):
    chosen_stat = message.text
    if chosen_stat in get_commands("back_from_stats"):
        await state.clear()
        await profile_handler(message, logger, language_code)
        return
    
    
    stats = {
        "strength": "strength_short",
        "agility": "agility_short",
        "physique": "physique_short",
        "intelligence": "intelligence_short",
        "wisdom": "wisdom_short",
        "charisma": "charisma_short",
        "luck": "luck_short",
    }
    
    map = {}
    for stat, group_key in stats.items():
        for cmd in get_commands(group_key):
            map[cmd.lower()] = stat

    chosen_stat = map.get(chosen_stat.lower())

    if chosen_stat is None:
        await message.answer(get_text_by_language("invalid_stat_choice", language_code))
        return

    try:
        success = await increment_character_stat(message.from_user.id, chosen_stat)
        if success:
            await message.answer(f"{chosen_stat} Успешно прокачана!")
        else:
            await message.answer("Недостаточно очков для прокачки этой характеристики.")
    except Exception as e:
        logger.error("Ошибка при прокачке характеристики для пользователя %s: %s", message.from_user.id, str(e))
        await message.answer("Произошла ошибка при прокачке характеристики.")
    