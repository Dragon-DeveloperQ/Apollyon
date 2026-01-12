from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from telegram_bot.keyboards.main import get_task_keyboard
from telegram_bot.languages import get_commands

router = Router()

@router.message(F.text.in_(get_commands("tasks")))
async def task_handler(message: Message):
    await message.answer("Ваши задания: ", reply_markup= await get_task_keyboard(message.from_user.id))