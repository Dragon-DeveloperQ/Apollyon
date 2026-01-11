from . import ru
from . import en

languages_menu_list = {
    "ru": ru.menu, 
    "en": en.menu
}

def get_commands(command_name):
    commands = []
    for i in languages_menu_list.values():
        commands.append(i[command_name])
    return commands