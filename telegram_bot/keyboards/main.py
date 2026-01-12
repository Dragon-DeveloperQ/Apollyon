from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot.languages import languages_menu_buttons_list

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from database.interactions import get_user_language

async def get_main_keyboard(telegram_id: int):
    language_code = await get_user_language(telegram_id)
    main_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["profile"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["tasks"]), KeyboardButton(text=languages_menu_buttons_list[language_code]["settings"])]
    ]
    main_keyboard = ReplyKeyboardMarkup(keyboard=main_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return main_keyboard


async def get_task_keyboard(telegram_id: int):
    language_code = await get_user_language(telegram_id)
    task_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["new_task"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["change_task"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["back"]), KeyboardButton(text=languages_menu_buttons_list[language_code]["delete_task"])]
    ]
    task_keyboard = ReplyKeyboardMarkup(keyboard=task_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return task_keyboard


async def get_profile_keyboard(telegram_id: int):
    language_code = await get_user_language(telegram_id)
    profile_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["back"])]
    ]
    profile_keyboard = ReplyKeyboardMarkup(keyboard=profile_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return profile_keyboard


'''
------------------------------------------------------------
                        НАСТРОЙКИ
------------------------------------------------------------
'''

async def get_settings_keyboard_by_telegram_id(telegram_id: int):
    language_code = await get_user_language(telegram_id)
    return await get_settings_keyboard_by_language(language_code)

async def get_settings_keyboard_by_language(language_code: str):
    settings_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["notifications"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["language"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["back"]), KeyboardButton(text=languages_menu_buttons_list[language_code]["delete_character"])]
    ]
    settings_keyboard = ReplyKeyboardMarkup(keyboard=settings_keyboard_list, resize_keyboard=True, one_time_keyboard=True)
    return settings_keyboard

def get_settings_language_keyboard():
    settings_language_keyboard_list = [
        [InlineKeyboardButton(text="🇷🇺 ru", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇺🇸 en", callback_data="lang:en")],
    ]
    
    settings_language_keyboard = InlineKeyboardMarkup(inline_keyboard=settings_language_keyboard_list)
    return settings_language_keyboard