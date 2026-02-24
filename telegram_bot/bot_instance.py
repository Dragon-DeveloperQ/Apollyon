import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from os import getenv
from dotenv import load_dotenv

# Load bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")  

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)
