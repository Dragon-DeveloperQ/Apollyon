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

def get_text_by_language(text_key, lang_code):
    
    if lang_code not in languages_menu_list:
        return "LANGUAGE_NOT_FOUND"
    
    texts = languages_menu_list.get(lang_code)

    if text_key not in texts:
        return "TEXT_NOT_FOUND"
    
    text = texts.get(text_key)
    return text