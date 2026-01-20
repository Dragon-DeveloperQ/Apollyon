from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot.languages import languages_menu_buttons_list

from database.interactions import get_user_language

async def get_main_keyboard(language_code: str):
    main_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["profile"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["tasks"]), KeyboardButton(text=languages_menu_buttons_list[language_code]["settings"])]
    ]
    main_keyboard = ReplyKeyboardMarkup(keyboard=main_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return main_keyboard


'''
------------------------------------------------------------
                        ЗАДАНИЯ
------------------------------------------------------------
'''


async def get_task_keyboard(language_code: str):
    task_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["start_task"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["new_task"]), KeyboardButton(text=languages_menu_buttons_list[language_code]["change_task"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["back"]), KeyboardButton(text=languages_menu_buttons_list[language_code]["delete_task"])]
    ]
    task_keyboard = ReplyKeyboardMarkup(keyboard=task_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return task_keyboard

async def task_completion_keyboard1(language_code: str):
    task_completion_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["back"])]
    ]
    task_completion_keyboard = ReplyKeyboardMarkup(keyboard=task_completion_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return task_completion_keyboard

async def task_creation_keyboard1(language_code: str):
    task_creation_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["cancel_task_creation"])]
    ]
    task_creation_keyboard = ReplyKeyboardMarkup(keyboard=task_creation_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return task_creation_keyboard

async def task_creation_keyboard2(language_code: str):
    task_creation_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["skip_description"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["cancel_task_creation"])]
    ]
    task_creation_keyboard = ReplyKeyboardMarkup(keyboard=task_creation_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return task_creation_keyboard

async def task_change_keyboard(language_code: str):
    task_change_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["change_task_name"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["change_task_description"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["cancel_task_change"])]
    ]
    task_change_keyboard = ReplyKeyboardMarkup(keyboard=task_change_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return task_change_keyboard

async def task_change_cancel_keyboard(language_code: str):
    task_change_cancel_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["cancel_task_change"])]
    ]
    task_change_cancel_keyboard = ReplyKeyboardMarkup(keyboard=task_change_cancel_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return task_change_cancel_keyboard

async def task_change_cancel_keyboard_for_description(language_code: str):
    task_change_cancel_keyboard_for_description_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["delete_description"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["cancel_task_change"])]
    ]
    task_change_cancel_keyboard_for_description = ReplyKeyboardMarkup(keyboard=task_change_cancel_keyboard_for_description_list, resize_keyboard=True, one_time_keyboard=False)
    return task_change_cancel_keyboard_for_description

async def complete_task_keyboard1(language_code: str):
    complete_task_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["cancel_task_execution"])]
    ]
    complete_task_keyboard = ReplyKeyboardMarkup(keyboard=complete_task_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return complete_task_keyboard

async def complete_task_keyboard2(language_code: str):
    complete_task_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["complete_task"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["cancel_task_execution"])]
    ]
    complete_task_keyboard = ReplyKeyboardMarkup(keyboard=complete_task_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return complete_task_keyboard

async def get_task_delete_keyboard(language_code: str):
    task_delete_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["cancel_task_deletion"])]
    ]
    task_delete_keyboard = ReplyKeyboardMarkup(keyboard=task_delete_keyboard_list, resize_keyboard=True, one_time_keyboard=False)
    return task_delete_keyboard

'''
------------------------------------------------------------
                        ПРОФИЛЬ     
------------------------------------------------------------
'''


async def get_profile_keyboard(language_code: str):
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
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["language"]), KeyboardButton(text=languages_menu_buttons_list[language_code]["timezone"])],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["back"]), KeyboardButton(text=languages_menu_buttons_list[language_code]["reset_character"])]
    ]
    settings_keyboard = ReplyKeyboardMarkup(keyboard=settings_keyboard_list, resize_keyboard=True)
    return settings_keyboard

def get_settings_language_keyboard():
    settings_language_keyboard_list = [
        [InlineKeyboardButton(text="🇷🇺 ru", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇺🇸 en", callback_data="lang:en")],
    ]
    
    settings_language_keyboard = InlineKeyboardMarkup(inline_keyboard=settings_language_keyboard_list)
    return settings_language_keyboard

def get_settings_timezone_keyboard(language_code: str):
    settings_timezone_keyboard_list = [
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["send_location"], request_location=True)],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["enter_timezone_manually"] )],
        [KeyboardButton(text=languages_menu_buttons_list[language_code]["settings"])]
    ]
    
    settings_timezone_keyboard = ReplyKeyboardMarkup(keyboard=settings_timezone_keyboard_list, resize_keyboard=True)
    return settings_timezone_keyboard