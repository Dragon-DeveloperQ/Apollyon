from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from telegram_bot.keyboards.main import get_main_keyboard
from telegram_bot.languages import get_commands, get_text_by_language

router = Router()

@router.message(F.text.in_(get_commands("back")))
@router.message(Command("start"))
async def start_handler(message: Message, logger, language_code):
    logger.debug("Возврат в главное меню для пользователя %s", message.from_user.id)
    await message.answer(get_text_by_language("main_menu", language_code), reply_markup= await get_main_keyboard(language_code))



