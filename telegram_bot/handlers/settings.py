from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from telegram_bot.keyboards.main import get_settings_keyboard
from telegram_bot.languages import get_commands

router = Router()

@router.message(F.text.in_(get_commands("settings")))
async def settings_handler(message: Message):
    await message.answer(".", reply_markup=get_settings_keyboard())