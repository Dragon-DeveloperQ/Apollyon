from . import ru
from . import en

languages_menu_buttons_list = {
    "ru": ru.menu_buttons, 
    "en": en.menu_buttons
}

languages_menu_list = {
    "ru": ru.text,
    "en": en.text
}

def get_commands(command_name):
    commands = []
    for i in languages_menu_buttons_list.values():
        commands.append(i[command_name])
    return commands

def get_text_by_language(lang_code, text_key):
    if lang_code in languages_menu_list:
        return languages_menu_list[lang_code].get(text_key, "")
    return "TEXT NOT FOUND"