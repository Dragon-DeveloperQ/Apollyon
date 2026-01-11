from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from telegram_bot.keyboards.main import get_main_keyboard
from telegram_bot.languages import get_commands

router = Router()

@router.message(F.text.in_(get_commands("back")))
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer('Запуск сообщения по команде /start используя фильтр CommandStart()', reply_markup=get_main_keyboard())



