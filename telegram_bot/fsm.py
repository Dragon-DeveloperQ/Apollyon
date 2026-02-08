from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram import Bot

async def get_fsm_context(user_id: int, bot: Bot, storage) -> FSMContext:
    
    key = StorageKey(
        bot_id=bot.id,
        chat_id=user_id,
        user_id=user_id
    )
    
    
    context = FSMContext(storage=storage, key=key)
    
    return context