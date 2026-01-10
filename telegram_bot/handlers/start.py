from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from keyboards.main import main_keyboard

router = Router()

@router.message(F.text == "⬅️ Назад")
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer('Запуск сообщения по команде /start используя фильтр CommandStart()', reply_markup=main_keyboard)



