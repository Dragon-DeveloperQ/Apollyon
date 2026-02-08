from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from os import getenv
from dotenv import load_dotenv

# Load bot token
load_dotenv("../config/tokens.env")
TOKEN = getenv("TELEGRAM_TOKEN")

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)
