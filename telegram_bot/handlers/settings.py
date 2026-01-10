from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from keyboards.main import settings_keyboard

router = Router()

@router.message(F.text == "⚙️ Настройки")
async def settings_handler(message: Message):
    await message.answer(".", reply_markup=settings_keyboard)