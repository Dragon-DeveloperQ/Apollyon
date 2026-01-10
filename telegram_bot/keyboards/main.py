from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_keyboard_list = [
    [KeyboardButton(text="👤 Профиль")],
    [KeyboardButton(text="📚 Задания"), KeyboardButton(text="⚙️ Настройки")]
]

profile_keyboard_list = [
    [KeyboardButton(text="⬅️ Назад")]
]

task_keyboard_list = [
    [KeyboardButton(text="📝 Новое задание")],
    [KeyboardButton(text="🪄 Изменить задание")],
    [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="🗑 Удалить задание")]
]

settings_keyboard_list = [
    [KeyboardButton(text="🔔 Уведомления")],
    [KeyboardButton(text="🇷🇺🇺🇦🇺🇸 Язык")],
    [KeyboardButton(text="⬅️ Назад"), KeyboardButton(text="❌ Удалить персонажа")]
]

main_keyboard = ReplyKeyboardMarkup(keyboard=main_keyboard_list, resize_keyboard=True, one_time_keyboard=True)
task_keyboard = ReplyKeyboardMarkup(keyboard=task_keyboard_list, resize_keyboard=True, one_time_keyboard=True)
settings_keyboard = ReplyKeyboardMarkup(keyboard=settings_keyboard_list, resize_keyboard=True, one_time_keyboard=True)
profile_keyboard = ReplyKeyboardMarkup(keyboard=profile_keyboard_list, resize_keyboard=True, one_time_keyboard=True)