from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from telegram_bot.languages import languages_menu_list

def get_main_keyboard(language_code="en"):
    main_keyboard_list = [
        [KeyboardButton(text=languages_menu_list[language_code]["profile"])],
        [KeyboardButton(text=languages_menu_list[language_code]["tasks"]), KeyboardButton(text=languages_menu_list[language_code]["settings"])]
    ]
    main_keyboard = ReplyKeyboardMarkup(keyboard=main_keyboard_list, resize_keyboard=True, one_time_keyboard=True)
    return main_keyboard


def get_task_keyboard(language_code="en"):
    task_keyboard_list = [
        [KeyboardButton(text=languages_menu_list[language_code]["new_task"])],
        [KeyboardButton(text=languages_menu_list[language_code]["change_task"])],
        [KeyboardButton(text=languages_menu_list[language_code]["back"]), KeyboardButton(text=languages_menu_list[language_code]["delete_task"])]
    ]
    task_keyboard = ReplyKeyboardMarkup(keyboard=task_keyboard_list, resize_keyboard=True, one_time_keyboard=True)
    return task_keyboard


def get_profile_keyboard(telegram_id: int):
    language_code = get_user_language_by_telegram_id(telegram_id)
    profile_keyboard_list = [
        [KeyboardButton(text=languages_menu_list[language_code]["back"])]
    ]
    profile_keyboard = ReplyKeyboardMarkup(keyboard=profile_keyboard_list, resize_keyboard=True, one_time_keyboard=True)
    return profile_keyboard


def get_settings_keyboard(language_code="en"):
    settings_keyboard_list = [
        [KeyboardButton(text=languages_menu_list[language_code]["notifications"])],
        [KeyboardButton(text=languages_menu_list[language_code]["language"])],
        [KeyboardButton(text=languages_menu_list[language_code]["back"]), KeyboardButton(text=languages_menu_list[language_code]["delete_character"])]
    ]
    settings_keyboard = ReplyKeyboardMarkup(keyboard=settings_keyboard_list, resize_keyboard=True, one_time_keyboard=True)
    return settings_keyboard
