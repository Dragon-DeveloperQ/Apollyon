import sys
from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import logger

from os import getenv
from dotenv import load_dotenv

from .models import Base


# Load bot token
load_dotenv("../config/db.env")
DATABASE_URL = getenv("DATABASE_URL")

db_logger = logger.getLogger("database")


# Создаём async engine
async_engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    future=True
)

# Session maker
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False  # Объекты остаются доступными после commit
)

async def init_db():
    db_logger.info("Инициализация базы данных...")
    
    async with async_engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
            db_logger.info("База данных успешно инициализирована.")
        except Exception as e:
            db_logger.error(f"Ошибка при инициализации таблиц: {e}")
    
    


async def get_session():
    async with async_session_maker() as session:
        yield session